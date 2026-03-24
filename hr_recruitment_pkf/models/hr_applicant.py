from datetime import datetime
from odoo import models, fields, api
from odoo.exceptions import ValidationError
from odoo.tools.translate import _
from odoo.tools import html2plaintext
import logging
from odoo.addons.ai.utils.llm_api_service import LLMApiService
import json
import os

_logger = logging.getLogger(__name__)


class HrApplicant(models.Model):
    _inherit = "hr.applicant"

    interview_notes = fields.Html(string="Interview Notes")
    ai_analysis = fields.Html(string="AI Analysis")
    ai_analysis_score = fields.Float(string="AI Analysis Score")
    applicant_resume = fields.Binary(string="Applicant Resume")
    applicant_resume_name = fields.Char(string="Applicant Resume Name")

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
            # 1. AI Analysis Trigger
            if applicant.applicant_resume and applicant.job_id:
                applicant._analyze_resume_ai()

            # 2. Duplicate Check
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

    def write(self, vals):
        res = super().write(vals)
        if 'applicant_resume' in vals:
            for applicant in self:
                applicant._analyze_resume_ai()
        return res

    def _analyze_resume_ai(self):
        self.ensure_one()
        if not self.applicant_resume:
            return
            
        if not self.job_id or not self.job_id.description:
            self.write({
                'ai_analysis': '<p class="text-warning"><b>AI Analysis Skipped:</b> The selected Job Position does not have a Job Summary (Description). The AI needs a Job Description to compare the resume against.</p>',
                'ai_analysis_score': 0
            })
            return

        
        api_key = self.env['ir.config_parameter'].sudo().get_param('ai.openai_key') or os.getenv('ODOO_AI_CHATGPT_TOKEN')
        if not api_key:
            _logger.info("Skipping AI Resume Analysis for Applicant %s because no OpenAI API key is set.", self.id)
            self.write({
                'ai_analysis': '<p class="text-warning"><b>AI Analysis Skipped:</b> No OpenAI API key is configured on this database.</p>',
                'ai_analysis_score': 0
            })
            return

        _logger.info("Starting AI Resume Analysis for Applicant %s", self.id)

        try:

            schema = {
                "type": "object",
                "properties": {
                    "analysis": {"type": "string"},
                    "score": {"type": "integer"}
                },
                "required": ["analysis", "score"],
                "additionalProperties": False
            }

            system_prompt = """
            You are an expert HR recruiter and ATS specialized in resume screening.
            Your task is to analyze the candidate's uploaded resume against the provided Job Description.
            
            GOALS:
            1. Evaluate how well the candidate's skills and experience match the requirements.
            2. Provide a concise textual analysis identifying key strengths and missing skills. Format your response using HTML tags (e.g. <ul>, <li>, <strong>, <br/>, <p>) to make it highly readable and well-structured. DO NOT wrap the HTML in markdown blocks like ````html`.
            3. Provide a match score from 0 to 100 representing their suitability for the role.
            """

            job_description = self.job_id.description or "No job description provided."
            # Strip HTML tags if any (basic cleanup for LLM)
            job_description_text = html2plaintext(job_description)

            user_prompt = f"Analyze the attached resume against this Job Description:\n\n{job_description_text}"

            files = [{
                'mimetype': 'application/pdf',
                'value': self.applicant_resume.decode('utf-8') if isinstance(self.applicant_resume, bytes) else self.applicant_resume,
                'file_ref': '<resume_pdf>'
            }]

            service = LLMApiService(self.env, provider='openai')
            responses = service.request_llm(
                llm_model='gpt-4o',
                system_prompts=[system_prompt],
                user_prompts=[user_prompt],
                schema=schema,
                files=files,
                temperature=0
            )

            if responses:
                response_content = responses[-1]
                data = json.loads(response_content)
                self.write({
                    'ai_analysis': data.get('analysis', ''),
                    'ai_analysis_score': data.get('score', 0)
                })
                _logger.info("AI Analysis completed for Applicant %s. Score: %s", self.id, data.get('score'))
            else:
                _logger.warning("No response received from AI for Applicant %s", self.id)

        except Exception as e:
            _logger.error("AI Resume Analysis Failed for Applicant %s: %s", self.id, e)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model_create_multi
    def create(self, vals_list):
        attachments = super().create(vals_list)
        for attachment in attachments:
            # If attachment is linked to an applicant and not part of a specific field (e.g. website form uploads)
            if attachment.res_model == 'hr.applicant' and attachment.res_id and not attachment.res_field:
                applicant = self.env['hr.applicant'].sudo().browse(attachment.res_id)
                # Populate the custom resume field if it's currently empty
                if applicant.exists() and not applicant.applicant_resume:
                    applicant.sudo().write({
                        'applicant_resume': attachment.datas,
                        'applicant_resume_name': attachment.name
                    })
        return attachments
    