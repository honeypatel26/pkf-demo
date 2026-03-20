# -*- coding: utf-8 -*-
import ast
from odoo import models, fields, api, _


class MailComposeMessage(models.TransientModel):
    _inherit = 'mail.compose.message'

    ac_partner_ids = fields.Many2many(
        'res.partner',
        relation='mail_compose_message_ac_res_partner_rel',
        column1='wizard_id',
        column2='partner_id',
        string="To",
        default=lambda self: self._default_ac_partner_ids()
    )

    def _default_ac_partner_ids(self):
        if self.env.context.get('default_composition_mode') == 'mass_mail' and self.env.context.get('default_model') == 'pkf.ac.team.independence':
            res_ids = self.env.context.get('default_res_ids')
            evaluation_id = self.env.context.get('default_evaluation_id')
            partner_ids = []
            if res_ids:
                partner_ids = self.env['pkf.ac.team.independence'].sudo().browse(res_ids).mapped('partner_id').ids
            if evaluation_id:
                eval_rec = self.env['pkf.ac.evaluation'].sudo().browse(evaluation_id)
                if eval_rec.create_uid.partner_id:
                    partner_ids.append(eval_rec.create_uid.partner_id.id)
            return list(set(partner_ids))
        return False

    def _inject_member_urls(self, body, accept_url, decline_url):
        """
        Safely replace Accept/Decline href attributes in the email HTML body.
        Uses lxml (available in all Odoo installs) to avoid regex HTML corruption.
        Buttons must have data-link-type="accept" or "decline" so they can be identified.
        """
        if not body:
            return body
        try:
            from lxml import html as lxml_html
            wrapped = body
            root = lxml_html.fromstring(wrapped)

            for anchor in root.xpath('.//a[@data-link-type="accept"]'):
                anchor.set('href', accept_url)
            for anchor in root.xpath('.//a[@data-link-type="decline"]'):
                anchor.set('href', decline_url)
            for anchor in root.xpath('.//a[@data-link-type="view-ac"]'):
                anchor.set('href', view_ac_url)

            # Return the inner HTML of the wrapper element
            inner = (root.text or '') + ''.join(
                lxml_html.tostring(child, encoding='unicode') for child in root
            )
            return inner
        except Exception:
            return body

    def _render_body_for_member(self, body_template, member):
        """
        Render the body for a specific team member.
        Tries the user's (possibly edited) body first, falls back to original template.
        """
        if body_template and self.template_id:
            # Strategy 1: render the user's edited body as QWeb for this member
            try:
                result = self.template_id._render_template(
                    body_template, 'pkf.ac.team.independence', [member.id], engine='qweb'
                )
                rendered = result.get(member.id)
                if rendered:
                    return rendered
            except Exception:
                pass

        # Strategy 2: render from the original template (fallback — loses user edits)
        if self.template_id:
            try:
                result = self.template_id._generate_template([member.id], ['body_html'])
                rendered = result[member.id].get('body_html', '')
                if rendered:
                    return rendered
            except Exception:
                pass

        return body_template or ''

    def _render_subject_for_member(self, subject_template, member):
        """Render the Jinja2 subject for a specific team member."""
        if subject_template and self.template_id:
            try:
                result = self.template_id._render_template(
                    subject_template, 'pkf.ac.team.independence', [member.id], engine='jinja'
                )
                rendered = result.get(member.id)
                if rendered:
                    return rendered
            except Exception:
                pass

        # Fallback: render from template
        if self.template_id:
            try:
                result = self.template_id._generate_template([member.id], ['subject'])
                rendered = result[member.id].get('subject', '')
                if rendered:
                    return rendered
            except Exception:
                pass

        return subject_template or ''

    def action_send_mail(self):
        # Only intercept for our A&C mass-mail flow
        if self.composition_mode == 'mass_mail' and self.model == 'pkf.ac.team.independence':

            # ── 1. Capture user's possibly-edited content ──
            body_field = 'body' if 'body' in self._fields else 'body_html'
            edited_body = str(getattr(self, body_field, '') or '')
            edited_subject = self.subject or ''

            # ── 2. Resolve team members to send to ──
            evaluation_id = self.env.context.get('default_evaluation_id')
            if not evaluation_id and self.res_ids:
                try:
                    raw_ids = ast.literal_eval(self.res_ids)
                    if raw_ids:
                        evaluation_id = self.env['pkf.ac.team.independence'].browse(raw_ids[0]).evaluation_id.id
                except Exception:
                    pass

            new_team_ids = []
            if self.ac_partner_ids and evaluation_id:
                for partner in self.ac_partner_ids:
                    member = self.env['pkf.ac.team.independence'].search([
                        ('evaluation_id', '=', evaluation_id),
                        ('partner_id', '=', partner.id),
                    ], limit=1)
                    if not member:
                        member = self.env['pkf.ac.team.independence'].create({
                            'evaluation_id': evaluation_id,
                            'partner_id': partner.id,
                            'name': partner.name,
                            'email': partner.email,
                        })
                    new_team_ids.append(member.id)
            else:
                try:
                    new_team_ids = ast.literal_eval(self.res_ids) if self.res_ids else []
                except Exception:
                    new_team_ids = []

            # Deduplicate
            new_team_ids = list(dict.fromkeys(new_team_ids))
            team_members = self.env['pkf.ac.team.independence'].browse(new_team_ids)

            # ── 3. Send one correctly rendered email per team member ──
            for member in team_members:
                accept_url = member.action_accept_url()
                decline_url = member.action_decline_url()

                # Render body and subject for this specific member
                rendered_body = self._render_body_for_member(edited_body, member)
                rendered_subject = self._render_subject_for_member(edited_subject, member)

                # Inject correct per-recipient Accept/Decline URLs using safe lxml parser
                final_body = self._inject_member_urls(rendered_body, accept_url, decline_url)

                # ── FIX: Use ONLY recipient_ids OR email_to — never both ──
                # Using both causes Odoo to send two emails to the same address.
                create_vals = {
                    'author_id': self.env.user.partner_id.id,
                    'subject': rendered_subject,
                    'body_html': final_body,
                    'auto_delete': True,
                }
                if member.partner_id:
                    create_vals['recipient_ids'] = [(4, member.partner_id.id)]
                else:
                    create_vals['email_to'] = member.email or ''

                mail = self.env['mail.mail'].sudo().create(create_vals)
                mail.send()

                # Log in each team member's chatter for audit trail
                member.message_post(
                    body=_("Independence email sent to %s (%s).") % (member.name, member.email),
                    message_type='comment',
                    subtype_xmlid='mail.mt_note',
                )

            return {'type': 'ir.actions.act_window_close'}

        return super(MailComposeMessage, self).action_send_mail()
