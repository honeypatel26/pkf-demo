from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    interview_notes = fields.Html(string="Interview Notes")

    @api.constrains('attachment_ids')
    def _check_attachment_pdf(self):
        for applicant in self:
            for attachment in applicant.attachment_ids:
                if attachment.mimetype != 'application/pdf':
                    raise ValidationError(_("Only PDF files are allowed for resume uploads. The file %s is not a PDF.") % attachment.name)

    @api.model_create_multi
    def create(self, vals_list):
        applicants = super().create(vals_list)
        for applicant in applicants:
            if not applicant.email_from or not applicant.partner_phone:
                continue

            # Protected stages names
            protected_stages = ['Virtual Bench']
            
            # Find duplicate applications for the same job position
            domain = [
                ('id', '!=', applicant.id),
                ('job_id', '=', applicant.job_id.id),
                ('active', '=', True),
                ('stage_id.name', 'not in', protected_stages),
                '|',
                ('email_normalized', '=', applicant.email_normalized),
                ('email_from', '=', applicant.email_from),
                ('partner_phone', '=', applicant.partner_phone)
            ]
            
            duplicate = self.search(domain, limit=1)
            
            if duplicate:
                # Find 'Duplicate' refuse reason
                refuse_reason = self.env['hr.applicant.refuse.reason'].search([('name', '=', 'Duplicate')], limit=1)
                
                if refuse_reason:
                    # Refuse the applicant (archive)
                    # We use write instead of action_refuse_reason_apply to avoid wizard overhead
                    applicant.write({
                        'refuse_reason_id': refuse_reason.id,
                        'active': False,
                        'refuse_date': datetime.now()
                    })
                    
                    # Log message
                    msg = _("Refused automatically because this application has been identified as a duplicate of %s") % duplicate.partner_name
                    applicant.message_post(body=msg)
                    
        return applicants
    