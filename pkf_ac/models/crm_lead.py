# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class CrmLead(models.Model):
    _inherit = "crm.lead"

    # ------------------------------------------------------------
    # A&C dynamic access (hidden technical field)
    # Used by CRM record rules to grant access based on users assigned in related A&C evaluations.
    # ------------------------------------------------------------
    ac_allowed_user_ids = fields.Many2many(
        comodel_name="res.users",
        relation="crm_lead_ac_allowed_user_rel",
        column1="lead_id",
        column2="user_id",
        string="A&C Allowed Users",
        help="Technical field used for A&C access control based on assigned users in related A&C evaluations.",
    )

    # ------------------------------------------------------------
    # Related A&C evaluations (what we show on CRM tab as one2many list)
    # ------------------------------------------------------------
    ac_evaluation_ids = fields.One2many(
        comodel_name="pkf.ac.evaluation",
        inverse_name="engagement_id",
        string="A&C Evaluations",
        readonly=True,
    )

    # Smart button counter: how many A&C evaluations are related to this lead
    ac_evaluation_count = fields.Integer(
        string="A&C Evaluations",
        compute="_compute_ac_evaluation_count",
        readonly=True,
    )

    def _compute_ac_evaluation_count(self):
        Eval = self.env["pkf.ac.evaluation"].sudo()
        for lead in self:
            lead.ac_evaluation_count = Eval.search_count([("engagement_id", "=", lead.id)])

    # ------------------------------------------------------------
    # Global rename: Contact -> Client (view-agnostic, works in popups)
    # ------------------------------------------------------------
    @api.model
    def fields_get(self, allfields=None, attributes=None):
        """Rename crm.lead.partner_id label globally to 'Client'."""
        res = super().fields_get(allfields=allfields, attributes=attributes)
        if "partner_id" in res:
            res["partner_id"]["string"] = "Client"
        return res

    # ------------------------------------------------------------
    # Force Sales/Pipeline action when opened from A&C
    # ------------------------------------------------------------
    def get_formview_action(self, access_uid=None):
        """Force opening Opportunities (Sales / Pipeline) when opened from A&C,
        regardless of user's 'Show Lead Menu' setting.
        """
        self.ensure_one()

        # This flag must be passed from A&C field context (engagement_id many2one)
        if self.env.context.get("from_ac_engagement"):
            # Use Pipeline action so UI is consistent for all users
            action = self.env.ref("crm.crm_lead_action_pipeline").read()[0]
            action.update({
                "res_id": self.id,
                "views": [(False, "form")],
                "view_mode": "form",
                "context": dict(self.env.context, default_type="opportunity"),
            })
            return action

        return super().get_formview_action(access_uid=access_uid)

    # ------------------------------------------------------------
    # A&C -> CRM access rebuild
    # ------------------------------------------------------------
    def _ac_rebuild_allowed_users(self):
        """Rebuild ac_allowed_user_ids based on ALL related A&C evaluations."""
        Eval = self.env["pkf.ac.evaluation"].sudo()
        Users = self.env["res.users"]

        for lead in self:
            users = Users
            evals = Eval.search([("engagement_id", "=", lead.id)])

            for ev in evals:
                if ev.manager_assigned_id:
                    users |= ev.manager_assigned_id
                if ev.partner_reviewer_id:
                    users |= ev.partner_reviewer_id
                if ev.engagement_partner_id:
                    users |= ev.engagement_partner_id
                if ev.assignee_ids:
                    users |= ev.assignee_ids

            lead.sudo().write({"ac_allowed_user_ids": [(6, 0, users.ids)]})

    # -----------------------
    # Actions (smart button)
    # -----------------------
    def action_open_ac_evaluations(self):
        """Smart button: open related A&C evaluations for this lead."""
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": _("A&C Evaluations"),
            "res_model": "pkf.ac.evaluation",
            "view_mode": "list,form",
            "domain": [("engagement_id", "=", self.id)],
            "context": {"default_engagement_id": self.id},
        }


class PkfAcEvaluation(models.Model):
    _inherit = "pkf.ac.evaluation"

    def _ac_sync_crm_access(self, leads):
        """Rebuild CRM allowed users for given leads (safe helper)."""
        leads = leads.filtered(lambda l: l)
        if leads:
            leads._ac_rebuild_allowed_users()

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)

        # When A&C is created, rebuild CRM access for impacted leads
        leads = records.mapped("engagement_id")
        self._ac_sync_crm_access(leads)

        return records

    def write(self, vals):
        # If engagement_id changes, we must rebuild for BOTH old and new leads
        old_leads = self.mapped("engagement_id")

        res = super().write(vals)

        tracked_fields = {
            "manager_assigned_id",
            "partner_reviewer_id",
            "engagement_partner_id",
            "assignee_ids",
            "engagement_id",
            "active",
        }

        if tracked_fields.intersection(vals.keys()):
            new_leads = self.mapped("engagement_id")
            self._ac_sync_crm_access(old_leads | new_leads)

        return res

    def unlink(self):
        leads = self.mapped("engagement_id")
        res = super().unlink()

        # After delete, rebuild CRM access (remove users that were only related to deleted evals)
        self._ac_sync_crm_access(leads)

        return res