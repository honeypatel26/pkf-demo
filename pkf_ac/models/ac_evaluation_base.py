# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from odoo.models import Constraint


class PkfAcEvaluation(models.Model):
    _name = "pkf.ac.evaluation"
    _description = "Acceptance & Continuance Evaluation"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _rec_name = "name"
    _order = "id desc"

    # =========================
    # Reference / Sequence
    # =========================
    name = fields.Char(
        string="Reference",
        required=True,
        copy=False,
        readonly=True,
        default="New",
        index=True,
        tracking=True,
    )

    access_token = fields.Char(string="Access Token", copy=False, readonly=True)

    state = fields.Selection(
        [
            ("new", "New"),
            ("in_progress", "In Progress"),
            ("done", "Done"),
            ("unlock", "Unlock"),
            ("done_locked", "Done/Locked"),
            ("lost", "Lost/Deselected"),
        ],
        string="Status",
        default="new",
        tracking=True,
        required=True,
    )

    # =========================
    # Main fields
    # =========================
    evaluation_type = fields.Selection(
        [
            ("acceptance", "Acceptance Evaluation"),
            ("continuance", "Continuance Evaluation"),
        ],
        string="Evaluation Type",
        tracking=True,
    )

    engagement_type = fields.Selection(
        [
            ("audit", "Audit"),
            ("review", "Review"),
            ("due_diligence", "Due Diligence"),
            ("attestation", "Attestation"),
            ("compilation", "Compilation"),
        ],
        string="Engagement Type",
        required=True,
        tracking=True,
    )

    # Engagement Name = CRM Lead
    engagement_id = fields.Many2one(
        "crm.lead",
        string="Engagement Name",
        required=True,
        tracking=True,
        ondelete="restrict",
    )

    # Client = related from CRM Lead partner
    client_id = fields.Many2one(
        "res.partner",
        string="Client",
        related="engagement_id.partner_id",
        store=True,
        readonly=True,
    )

    major_relationships = fields.Char(string="Major Relationships")
    client_since = fields.Date(string="Client Since")
    industry = fields.Char(string="Industry")
    main_operations = fields.Char(string="Main Operations")

    engagement_partner_id = fields.Many2one(
        "res.users",
        string="Engagement Partner",
        tracking=True,
        ondelete="restrict",
    )
    partner_since = fields.Date(string="Partner Since")

    type_of_organization = fields.Selection(
        [
            ("private", "Private Company"),
            ("public", "Public Company"),
            ("government", "Government"),
            ("not_for_profit", "Not for Profit"),
            ("pie", "Public Interest Entity"),
        ],
        string="Type of Organization",
    )

    manager_assigned_id = fields.Many2one(
        "res.users",
        string="Manager Assigned",
        tracking=True,
        ondelete="restrict",
    )

    assignee_ids = fields.Many2many(
        "res.users",
        string="Assignees",
        tracking=True,
        relation='pkf_ac_eval_assignee_rel',
        column1='evaluation_id',
        column2='user_id',
    )

    pkf_office_id = fields.Many2one(
        "res.company",
        string="PKF Office",
        required=True,
        tracking=True,
        default=lambda self: self.env.company,
    )

    # Right column (legacy/manual field, can stay)
    engagement_risk = fields.Selection(
        [("low", "Low Risk"), ("medium", "Medium Risk"), ("high", "High Risk")],
        string="Engagement Risk",
    )

    deadline_for_completion = fields.Date(string="Deadline for completion")
    stock_exchange = fields.Char(string="Stock Exchange")
    location_of_stock_exchange = fields.Char(string="Location of Stock Exchange")
    client_stock_symbol = fields.Char(string="Client's Stock Symbol")

    market_capitalization = fields.Monetary(
        string="Market Capitalization",
        currency_field="currency_id",
    )

    currency_id = fields.Many2one(
        "res.currency",
        string="Reporting Currency",
        default=lambda self: self.env.company.currency_id,
    )

    financial_reporting_framework_id = fields.Many2one(
        "pkf.ac.reporting.framework",
        string="Financial Reporting Framework",
    )

    auditing_standards_used_id = fields.Many2one(
        "pkf.ac.auditing.standard",
        string="Auditing Standards Used",
    )

    year_end_date = fields.Date(string="Year End")

    eqcr_needed = fields.Selection([("yes", "Yes"), ("no", "No")], string="EQCR Needed")
    sec_registrant = fields.Selection([("yes", "Yes"), ("no", "No")], string="SEC Registrant")
    new_page_lines_ids = fields.One2many(comodel_name='trend.research',inverse_name="evaluation_id", string="Trend Research Lines")
    team_independence_ids = fields.One2many("pkf.ac.team.independence", "evaluation_id", string="Team Independence")


    partner_reviewer_id = fields.Many2one(
        "res.users",
        string="Partner Reviewer",
        ondelete="restrict",
    )
    reviewer_since = fields.Date(string="Reviewer Since")

    # ============================================================
    # NEW: Overall Engagement Risk badge (DO NOT recompute the risk)
    # We only "map" existing computed text from risk_analysis.py:
    # overall_engagement_risk (e.g. "Low Risk", "Medium Risk", "High Risk")
    # ============================================================

    overall_risk_level = fields.Selection(
        [
            ("low", "Low Risk"),
            ("medium", "Medium Risk"),
            ("high", "High Risk"),
            ("unknown", "Unknown Risk"),
        ],
        string="Engagement Risk",
        compute="_compute_overall_risk_level",
        store=True,
        tracking=True,
        readonly=True,
    )

    _constraints = [Constraint(["name"], "unique")]
    engagement_letter_ids = fields.One2many(
        "engagement.letter",
        "evaluation_id",
        string="Engagement Letters",
    )
    engagement_letter_count = fields.Integer(
        string="Engagement Letter Count",
        compute="_compute_engagement_letter_count"
    )
    source_create_date = fields.Datetime(
        string="Original Create Date"
    )
    create_year = fields.Integer(
        string="Created Year",
        compute="_compute_create_year",
        store=True,
        index=True
    )

    @api.depends('create_date')
    def _compute_create_year(self):
        for rec in self:
            if rec.source_create_date:
                rec.create_year = rec.source_create_date.year
            elif rec.create_date:
                rec.create_year = rec.create_date.year
            else:
                rec.create_year = False
    # =========================
    # Create: sequence + remove default "Model created"
    # =========================
    @api.model_create_multi
    def create(self, vals_list):
        seq = self.env["ir.sequence"]
        for vals in vals_list:
            if vals.get("name", "New") == "New":
                vals["name"] = seq.next_by_code("pkf.ac.evaluation") or "New"

        ctx = dict(self.env.context)
        # In different versions mail.thread checks different flags — set several
        ctx.update({
            "mail_create_nolog": True,
            "mail_create_nosubscribe": True,
            "tracking_disable": True,
        })

        records = super(PkfAcEvaluation, self.with_context(ctx)).create(vals_list)

        # Post a clean custom message
        for rec in records:
            rec.message_post(
                body=_("%s created") % rec.name,
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
        return records

    # ============================================================
    # Compute: badge value mapping (no risk calculation here)
    # Source field comes from risk_analysis.py:
    # - overall_engagement_risk (Char) is already computed there
    # ============================================================
    @api.depends("overall_engagement_risk")
    def _compute_overall_risk_level(self):
        for rec in self:
            src = (rec.overall_engagement_risk or "").strip().lower()

            # IMPORTANT: if source is empty -> clear badge
            if not src:
                rec.overall_risk_level = False
                continue

            if "high" in src:
                rec.overall_risk_level = "high"
            elif "medium" in src:
                rec.overall_risk_level = "medium"
            elif "low" in src:
                rec.overall_risk_level = "low"
            else:
                rec.overall_risk_level = False

    # =========================
    # Helper methods
    # =========================
    def get_engagement_type_label(self):
        self.ensure_one()
        if not self.engagement_type:
            return ""
        return dict(self._fields["engagement_type"].selection).get(self.engagement_type, "")

    # =========================
    # Status buttons
    # =========================
    def action_set_in_progress(self):
        self.write({"state": "in_progress"})

    def action_set_done(self):
        self.write({"state": "done"})

    def action_set_unlock(self):
        self.write({"state": "unlock"})

    def action_set_done_locked(self):
        self.write({"state": "done_locked"})

    def action_set_lost(self):
        self.write({"state": "lost"})

    # =========================
    # Engagement Letter integration
    # =========================
    @api.depends("engagement_letter_ids")
    def _compute_engagement_letter_count(self):
        for rec in self:
            rec.engagement_letter_count = len(rec.engagement_letter_ids)

    def action_view_engagement_letters(self):
        self.ensure_one()
        return {
            "name": _("Engagement Letters"),
            "type": "ir.actions.act_window",
            "res_model": "engagement.letter",
            "view_mode": "list,form",
            "domain": [("evaluation_id", "=", self.id)],
            "context": {"default_evaluation_id": self.id},
        }

    def action_create_engagement_letter(self):
        self.ensure_one()
        if not self.client_id:
            raise UserError(_("Please set a Client first."))
        
        vals = {
            "partner_id": self.client_id.id,
            "responsible_partner_id": self.engagement_partner_id.id,
            "owner_id": self.engagement_partner_id.id,
            "evaluation_id": self.id,
        }
        
        letter = self.env["engagement.letter"].create(vals)
        
        return {
            "name": _("Engagement Letter"),
            "type": "ir.actions.act_window",
            "res_model": "engagement.letter",
            "view_mode": "form",
            "res_id": letter.id,
            "target": "current",
        }

    def action_send_evaluation_email(self):
        self.ensure_one()
        template = self.env.ref("pkf_ac.email_template_ac_review", raise_if_not_found=False)
        
        # Synchronize team members from partners/assignees
        partners = self.env['res.partner']
        if self.engagement_partner_id.partner_id:
            partners |= self.engagement_partner_id.partner_id
        if self.assignee_ids.partner_id:
            partners |= self.assignee_ids.partner_id
        if self.partner_reviewer_id.partner_id:
            partners |= self.partner_reviewer_id.partner_id
        if self.manager_assigned_id.partner_id:
            partners |= self.manager_assigned_id.partner_id

        existing_partners = self.team_independence_ids.mapped('partner_id')
        new_team_vals = []
        for partner in partners:
            if partner not in existing_partners:
                new_team_vals.append({
                    'evaluation_id': self.id,
                    'partner_id': partner.id,
                    'name': partner.name,
                    'email': partner.email,
                })
        if new_team_vals:
            self.env['pkf.ac.team.independence'].create(new_team_vals)

        # Open composer for the Team Independence model in mass_mail mode
        # mass_mail = sends one email per recipient (respects per-recipient edits)
        team_members = self.team_independence_ids.filtered(lambda t: t.confirmation == 'pending')

        if not team_members:
            raise UserError(_("No pending team members to send emails to."))

        team_ids = team_members.ids

        ctx = {
            "default_model": "pkf.ac.team.independence",
            "active_model": "pkf.ac.team.independence",
            "active_ids": team_ids,
            "default_res_ids": team_ids,
            "default_evaluation_id": self.id,
            "default_use_template": True,
            "default_template_id": template.id if template else False,
            "default_composition_mode": "mass_mail",
            "default_email_layout_xmlid": "mail.mail_notification_layout_with_responsible_signature",
            "force_email": True,
        }
        return {
            "type": "ir.actions.act_window",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(False, "form")],
            "view_id": False,
            "target": "new",
            "context": ctx,
        }


class PkfAcReportingFramework(models.Model):
    _name = "pkf.ac.reporting.framework"
    _description = "A&C Financial Reporting Framework"
    _order = "name"

    name = fields.Char(string="Name", required=True)


class PkfAcAuditingStandard(models.Model):
    _name = "pkf.ac.auditing.standard"
    _description = "A&C Auditing Standard"
    _order = "name"

    name = fields.Char(string="Name", required=True)

