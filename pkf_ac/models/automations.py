# -*- coding: utf-8 -*-
from odoo import api, models, _
from odoo.exceptions import ValidationError
from odoo.tools import html_escape
from markupsafe import Markup


class PkfAcEvaluationAutomations(models.AbstractModel):
    """
    A&C automations storage.

    - Send real email via mail.mail
    - Log only short note in chatter (no full email body)
    - Trigger only on real state transition to avoid duplicates
    - Auto-followers: add all users from key fields as followers (no removals)
    """
    _name = "pkf.ac.evaluation.automations"
    _description = "PKF A&C Automations (Helpers)"

    # -----------------------
    # URL / HELPERS
    # -----------------------
    @api.model
    def _ac_get_base_url(self):
        return self.env["ir.config_parameter"].sudo().get_param("web.base.url", "")

    def _ac_get_record_url(self):
        self.ensure_one()
        base = self._ac_get_base_url()
        if not base:
            return ""
        return f"{base}/web#id={self.id}&model={self._name}&view_type=form"

    def _ac_get_selection_label(self, field_name, value):
        """Return selection label for a selection field value (e.g. 'audit' -> 'Audit')."""
        field = self._fields.get(field_name)
        if not field or not getattr(field, "selection", None):
            return value or ""
        selection = field.selection
        if callable(selection):
            selection = selection(self.env)
        return dict(selection).get(value, value or "")

    # -----------------------
    # AUTO FOLLOWERS
    # -----------------------
    def _ac_get_follower_partner_ids_from_fields(self):
        """
        Collect partner_ids that must be followers based on the record fields.

        Fields used:
        - create_uid (creator)
        - engagement_partner_id (res.users)
        - partner_reviewer_id (res.users) [optional]
        - manager_assigned_id (res.users)
        - assignee_ids (res.users many2many)
        """
        self.ensure_one()
        partner_ids = set()

        # Creator
        if self.create_uid and self.create_uid.partner_id:
            partner_ids.add(self.create_uid.partner_id.id)

        # Engagement Partner
        if self.engagement_partner_id and self.engagement_partner_id.partner_id:
            partner_ids.add(self.engagement_partner_id.partner_id.id)

        # Partner Reviewer (if chosen)
        if self.partner_reviewer_id and self.partner_reviewer_id.partner_id:
            partner_ids.add(self.partner_reviewer_id.partner_id.id)

        # Manager Assigned
        if self.manager_assigned_id and self.manager_assigned_id.partner_id:
            partner_ids.add(self.manager_assigned_id.partner_id.id)

        # Assignees
        if self.assignee_ids:
            partner_ids.update(self.assignee_ids.mapped("partner_id").ids)

        # Remove falsy (just in case)
        partner_ids.discard(False)
        return list(partner_ids)

    def _ac_sync_followers_add_only(self):
        """
        Add followers from fields to chatter followers.

        NOTE:
        - Add only (do not remove existing followers).
        - This matches your requirement: "add to followers of this record".
        """
        for rec in self:
            partner_ids_to_add = rec._ac_get_follower_partner_ids_from_fields()
            if not partner_ids_to_add:
                continue

            current_partner_ids = set(rec.message_partner_ids.ids)
            missing = [pid for pid in partner_ids_to_add if pid not in current_partner_ids]
            if missing:
                rec.message_subscribe(partner_ids=missing)

    # -----------------------
    # EMAIL RECIPIENTS (PARTNERS)
    # -----------------------
    def _ac_get_recipients_partners(self):
        """
        Email recipients:
        - Engagement Partner (engagement_partner_id)
        - Partner Reviewer (partner_reviewer_id) if selected
        """
        self.ensure_one()
        partners = self.env["res.partner"].browse()

        if self.engagement_partner_id and self.engagement_partner_id.partner_id:
            partners |= self.engagement_partner_id.partner_id

        if self.partner_reviewer_id and self.partner_reviewer_id.partner_id:
            partners |= self.partner_reviewer_id.partner_id

        return partners.filtered(lambda p: bool(p.email))

    # -----------------------
    # IN PROGRESS EMAIL
    # -----------------------
    def _ac_build_in_progress_email(self, triggering_user=None):
        self.ensure_one()
        triggering_user = triggering_user or self.env.user

        doc_name_raw = self.name or (self.display_name or _("N/A"))
        engagement_name_raw = self.engagement_id.name if self.engagement_id else _("N/A")
        client_name_raw = self.client_id.name if self.client_id else _("N/A")
        office_name_raw = self.pkf_office_id.name if self.pkf_office_id else _("N/A")
        engagement_type_label_raw = self._ac_get_selection_label("engagement_type", self.engagement_type) or _("N/A")

        record_url = self._ac_get_record_url()
        subject = _("%(eng)s Assigned to You") % {"eng": engagement_name_raw or doc_name_raw}

        triggering_name = html_escape(triggering_user.name or "")
        doc_name = html_escape(doc_name_raw)
        engagement_name = html_escape(engagement_name_raw)
        client_name = html_escape(client_name_raw)
        office_name = html_escape(office_name_raw)
        engagement_type_label = html_escape(engagement_type_label_raw)

        link_html = ""
        if record_url:
            link_html = (
                f'<p>To view the details, please '
                f'<a href="{html_escape(record_url)}">click here</a>.</p>'
            )

        body_html = Markup(
            f"""
            <p>Dear Partner(s),</p>
            <p>{triggering_name} has just assigned you the following activity:</p>

            <p><b>Document:</b> {doc_name}</p>
            <p><b>Engagement Type:</b> {engagement_type_label}</p>
            <p><b>Engagement Name:</b> {engagement_name}</p>
            <p><b>Client:</b> {client_name}</p>
            <p><b>Office:</b> {office_name}</p>

            {link_html}

            <p>--<br>Administrator<br>PKF-Antares</p>
            <p>403-375-9955 | info@pkfantares.com | <a href="http://pkfantares.com">http://pkfantares.com</a></p>
            """
        )
        return subject, body_html

    def _ac_send_in_progress_email_and_log(self, triggering_user=None):
        self.ensure_one()
        recipients = self._ac_get_recipients_partners()

        if not recipients:
            self.message_post(
                body=_("Email was not sent: recipients not set or missing emails."),
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
            return False

        subject, body_html = self._ac_build_in_progress_email(triggering_user=triggering_user)
        email_to = ",".join([p.email for p in recipients if p.email])

        mail = self.env["mail.mail"].sudo().create({
            "subject": subject,
            "body_html": body_html,
            "email_to": email_to,
            "email_from": "notifications@pkfantares.com",
            "auto_delete": False,
        })
        mail.sudo().send()

        names = ", ".join(recipients.mapped("name"))
        self.message_post(
            body=Markup(f"Email sent to: <b>{html_escape(names)}</b>."),
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )
        return True

    # -----------------------
    # DONE EMAIL
    # -----------------------
    def _ac_build_done_email(self, triggering_user=None):
        self.ensure_one()
        triggering_user = triggering_user or self.env.user

        doc_name_raw = self.name or (self.display_name or _("N/A"))
        engagement_name_raw = self.engagement_id.name if self.engagement_id else _("N/A")
        client_name_raw = self.client_id.name if self.client_id else _("N/A")
        office_name_raw = self.pkf_office_id.name if self.pkf_office_id else _("N/A")
        engagement_type_label_raw = self._ac_get_selection_label("engagement_type", self.engagement_type) or _("N/A")

        record_url = self._ac_get_record_url()
        subject = _("Status Update: %(eng)s is now Done") % {"eng": engagement_name_raw or doc_name_raw}

        triggering_name = html_escape(triggering_user.name or "")
        doc_name = html_escape(doc_name_raw)
        engagement_name = html_escape(engagement_name_raw)
        client_name = html_escape(client_name_raw)
        office_name = html_escape(office_name_raw)
        engagement_type_label = html_escape(engagement_type_label_raw)

        link_html = ""
        if record_url:
            link_html = (
                f'<p>To view the details, please '
                f'<a href="{html_escape(record_url)}">click here</a>.</p>'
            )

        body_html = Markup(
            f"""
            <p>Dear Partner(s),</p>
            <p>The status of the following activity has been updated to <b>Done</b> by {triggering_name}:</p>

            <p><b>Document:</b> {doc_name}</p>
            <p><b>Engagement Type:</b> {engagement_type_label}</p>
            <p><b>Engagement Name:</b> {engagement_name}</p>
            <p><b>Client:</b> {client_name}</p>
            <p><b>Office:</b> {office_name}</p>

            {link_html}

            <p>--<br>Administrator<br>PKF-Antares</p>
            <p>403-375-9955 | info@pkfantares.com | <a href="http://pkfantares.com">http://pkfantares.com</a></p>
            """
        )
        return subject, body_html

    def _ac_send_done_email_and_log(self, triggering_user=None):
        self.ensure_one()
        recipients = self._ac_get_recipients_partners()

        if not recipients:
            self.message_post(
                body=_("Email was not sent: recipients not set or missing emails."),
                message_type="comment",
                subtype_xmlid="mail.mt_note",
            )
            return False

        subject, body_html = self._ac_build_done_email(triggering_user=triggering_user)
        email_to = ",".join([p.email for p in recipients if p.email])

        mail = self.env["mail.mail"].sudo().create({
            "subject": subject,
            "body_html": body_html,
            "email_to": email_to,
            "email_from": "notifications@pkfantares.com",
            "auto_delete": False,
        })
        mail.sudo().send()

        names = ", ".join(recipients.mapped("name"))
        self.message_post(
            body=Markup(f"Email sent to: <b>{html_escape(names)}</b>."),
            message_type="comment",
            subtype_xmlid="mail.mt_note",
        )
        return True


class PkfAcEvaluation(models.Model):
    _inherit = ["pkf.ac.evaluation", "pkf.ac.evaluation.automations"]

    # -----------------------
    # VALIDATION (NO SAME USER)
    # -----------------------
    @api.constrains("engagement_partner_id", "partner_reviewer_id")
    def _check_partner_not_same_as_reviewer(self):
        for rec in self:
            if rec.engagement_partner_id and rec.partner_reviewer_id and rec.engagement_partner_id == rec.partner_reviewer_id:
                raise ValidationError(_("You cannot select the same user for Engagement Partner and Partner Reviewer fields."))

    # -----------------------
    # VALIDATION (7 YEARS RULE)
    # -----------------------
    @api.constrains("engagement_partner_id", "partner_since", "partner_reviewer_id", "reviewer_since", "create_date")
    def _check_7_years_rule(self):
        """
        7 years rule (same logic as Studio: compare years only):
        - Engagement Partner: (create_year - partner_since_year) >= 7 -> not allowed
        - Partner Reviewer: (create_year - reviewer_since_year) >= 7 -> not allowed
        """
        for rec in self:
            if not rec.create_date:
                continue

            created_year = rec.create_date.year

            if rec.engagement_partner_id and rec.partner_since:
                if (created_year - rec.partner_since.year) >= 7:
                    raise ValidationError(_("You cannot select this Engagement Partner because of the 7 Years Rule."))

            if rec.partner_reviewer_id and rec.reviewer_since:
                if (created_year - rec.reviewer_since.year) >= 7:
                    raise ValidationError(_("You cannot select this Partner Reviewer because of the 7 Years Rule."))

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        # Auto-followers on create
        records._ac_sync_followers_add_only()
        return records

    def write(self, vals):
        """
        - Auto-followers when any related user field changes
        - Email automations only on real transitions:
            * to in_progress
            * to done
        """
        skip_status = self.env.context.get("skip_ac_status_notify")

        # Track status before write for transition detection
        before_state = {}
        if not skip_status and "state" in vals:
            for rec in self:
                before_state[rec.id] = rec.state

        res = super().write(vals)

        # Auto-followers: add followers when these fields are updated
        follower_fields = {"assignee_ids", "manager_assigned_id", "engagement_partner_id", "partner_reviewer_id"}
        if follower_fields.intersection(vals.keys()):
            self._ac_sync_followers_add_only()

        # Email automations: run only if state changed
        if not skip_status and "state" in vals:
            for rec in self:
                old = before_state.get(rec.id)
                if old != "in_progress" and rec.state == "in_progress":
                    rec._ac_send_in_progress_email_and_log(triggering_user=self.env.user)

                if old != "done" and rec.state == "done":
                    rec._ac_send_done_email_and_log(triggering_user=self.env.user)

        return res