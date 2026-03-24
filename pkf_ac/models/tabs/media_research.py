# -*- coding: utf-8 -*-
import base64
import csv
import io

from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.addons.ai.utils.llm_api_service import LLMApiService
import json
import logging

_logger = logging.getLogger(__name__)


class PkfAcMediaResearch(models.Model):
    _name = "pkf.ac.media.research"
    _description = "A&C Media Research"
    _order = "date desc, id desc"

    evaluation_id = fields.Many2one(
        "pkf.ac.evaluation",
        string="Evaluation",
        required=True,
        ondelete="cascade",
    )
    
    reception = fields.Selection(
        [
            ("positive", "Positive"),
            ("negative", "Negative"),
        ],
        string="Reception",
        required=True,
        default="positive",
    )

    title = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    analysis = fields.Text(string="Comment / Analysis")
    auditor_comments = fields.Text(string="Auditor Comments")
    source = fields.Text(string="Source")
    date = fields.Date(string="Date", default=fields.Date.context_today)


class PkfAcEvaluationMedia(models.Model):
    _inherit = "pkf.ac.evaluation"

    media_research_ids = fields.One2many(
        "pkf.ac.media.research",
        "evaluation_id",
        string="Media Research Findings",
    )

    def action_export_media_csv(self):
        self.ensure_one()

        output = io.StringIO()
        writer = csv.writer(output)

        # Header
        writer.writerow([
            "Reception",
            "Title",
            "Description",
            "Comment / Analysis",
            "Auditor Comments",
            "Source",
            "Date",
        ])

        # Data
        for line in self.media_research_ids:
            writer.writerow([
                line.reception,
                line.title or "",
                line.description or "",
                line.analysis or "",
                line.auditor_comments or "",
                line.source or "",
                line.date or "",
            ])

        file_data = base64.b64encode(output.getvalue().encode())
        output.close()

        attachment = self.env['ir.attachment'].create({
            'name': f'Media_Research_{self.id}.csv',
            'type': 'binary',
            'datas': file_data,
            'mimetype': 'text/csv',
        })

        return {
            'type': 'ir.actions.act_url',
            'url': f'/web/content/{attachment.id}?download=true',
            'target': 'self',
        }

    def action_research_media(self):
        self.ensure_one()
        client_name = self.client_id.name
        _logger.info(f"MEDIA RESEARCH: Starting for '{client_name}'")

        if not client_name:
            raise UserError(_("Please set a Customer/Client first."))

        schema = {
            "type": "object",
            "properties": {
                "findings": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "reception": {"type": "string", "enum": ["positive", "negative"]},
                            "title": {"type": "string"},
                            "description": {"type": "string"},
                            "analysis": {"type": "string"},
                            "source": {"type": "string"},
                            "date": {"type": ["string", "null"], "format": "date"}
                        },
                        "required": ["reception", "title", "description", "analysis", "source", "date"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["findings"],
            "additionalProperties": False
        }

        system_prompt = f"""
        You are an expert audit researcher specializing in Corporate Intelligence and KYC.
        Your task is to research the company: {client_name} and its direct network of influence.
        
        GOALS:
        1. Conduct a comprehensive background and media review (both positive and adverse).
        2. Check company website, LinkedIn, regulatory databases, and general news sources.
        3. Identify both general/positive information (e.g., business overview, awards, successful projects, financial performance) 
           AND adverse findings (e.g., "fraud", "litigation", "regulatory action", "sanctions", "criminal charges").
        
        EXPECTED OUTPUT:
        - Reception: 'negative' if adverse findings exist (fraud, litigation, etc), 'positive' for general or beneficial information.
        - Title: Short professional heading summarizing the specific finding, news, or review area.
        - Description: Brief summary of what type of screening was conducted or the event/achievement found.
        - Analysis: Detailed findings, financial context, or risk assessment.
        - Source: List relevant URLs reviewed.
        - Date: Date the finding or report was published/conducted (YYYY-MM-DD). Use current date if specific publication date is unknown.
        """

        user_prompt = f"Perform balanced media research (positive achievements and adverse risks) for '{client_name}'."

        try:
            service = LLMApiService(self.env, provider='openai')
            responses = service.request_llm(
                llm_model='gpt-4o',
                system_prompts=[system_prompt],
                user_prompts=[user_prompt],
                schema=schema,
                web_grounding=True,
                temperature=0
            )

            if not responses:
                raise UserError(_("No response received from AI."))

            content = responses[-1]
            data = json.loads(content)

            # Clear existing data (optional, user might want to keep history? 
            # Usually research is refreshed. Let's keep existing and add new if not identical, 
            # but for simplicity let's clear if starting fresh research)
            # self.media_research_ids.unlink()

            for item in data.get('findings', []):
                self.env['pkf.ac.media.research'].create({
                    'evaluation_id': self.id,
                    'reception': item.get('reception', 'positive'),
                    'title': item.get('title', 'Review'),
                    'description': item.get('description', ''),
                    'analysis': item.get('analysis', ''),
                    'source': item.get('source', ''),
                    'date': item.get('date') or fields.Date.context_today(self),
                })

            return True

        except Exception as e:
            _logger.error(f"Media Research Failed: {str(e)}")
            raise UserError(_(f"Media Research Failed: {str(e)}"))
