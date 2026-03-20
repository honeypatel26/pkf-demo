from odoo import fields, models, api, _
from odoo.exceptions import UserError
from odoo.addons.ai.utils.llm_api_service import LLMApiService
import json
import logging

_logger = logging.getLogger(__name__)


class PkfAcRelationship(models.Model):
    _inherit = "pkf.ac.evaluation"

    customer_name = fields.Char(related="client_id.name", string="Customer/Client", store=True)

    ownership_structure_file = fields.Binary(string="Ownership Structure")
    ownership_structure_file_name = fields.Char(string="File Name")
    ownership_structure_description = fields.Text(string="Ownership Structure Description")

    other_documents_file = fields.Binary(string="Other Documents")
    other_documents_file_name = fields.Char(string="File Name")
    other_documents_description = fields.Text(string="Other Documents Description")

    def action_research_customer(self):
        self.ensure_one()
        _logger.info(f"AI RESEARCH (Native): Starting for customer '{self.customer_name}'")

        if not self.customer_name:
            raise UserError(_("Please set a Customer/Client first."))

        # Define the schema for structured output
        schema = {
            "type": "object",
            "properties": {
                "key_management": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "associated_companies": {"type": "string"},
                            "country": {"type": ["string", "null"]},
                            "source_url": {"type": ["string", "null"]}
                        },
                        "required": ["name", "role", "associated_companies", "country", "source_url"],
                        "additionalProperties": False
                    }
                },
                "directors": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "role": {"type": "string"},
                            "associated_companies": {"type": "string"},
                            "country": {"type": ["string", "null"]},
                            "source_url": {"type": ["string", "null"]}
                        },
                        "required": ["name", "role", "associated_companies", "country", "source_url"],
                        "additionalProperties": False
                    }
                }
            },
            "required": ["key_management", "directors"],
            "additionalProperties": False
        }

        system_prompt = """
        You are an expert audit researcher specializing in Corporate Intelligence and KYC.
        Your task is to research the given Client company and its direct network of influence.
        
        GOALS:
        1. Identify the current Key Management Personnel (KMP) and Directors of the Client.
        2. Identify companies associated with the Client (subsidiaries, parent companies) or its Directors (other directorships).
        3. Identify the Directors of those associated companies.
        
        For each individual or relevant relationship identified, provide:
        - Name: Person's full name.
        - Role: Their specific role (e.g., "Director", "CEO", "Shareholder").
        - Associated Companies: List of other companies they are currently associated with.
        - Country: Country of residence/registration.
        - Source URL: The specific web URL where this data was extracted (e.g., company website, LinkedIn, news, registry).
        """

        user_prompt = f"Perform deep research on '{self.customer_name}' and identify key personnel and corporate associations."

        try:
            service = LLMApiService(self.env, provider='openai')

            # Using request_llm which handles the API call
            # web_grounding=True enables search if supported/configured
            responses = service.request_llm(
                llm_model='gpt-4o',  # Or 'gpt-4-turbo'
                system_prompts=[system_prompt],
                user_prompts=[user_prompt],
                schema=schema,
                web_grounding=True,
                temperature=0
            )

            if not responses:
                raise UserError(_("No response received from AI."))

            # Parse response - LLMApiService with schema returns a JSON string
            content = responses[-1]
            _logger.info(f"AI RESEARCH Response: {content}")

            data = json.loads(content)

            # Clear and Populate
            self.key_management_ids.unlink()
            self.director_ids.unlink()

            def get_country_id(country_name):
                if not country_name:
                    return False
                country = self.env['res.country'].search([('name', '=ilike', country_name)], limit=1)
                return country.id if country else False

            for item in data.get('key_management', []):
                self.env['pkf.ac.relationship.person'].create({
                    'evaluation_id': self.id,
                    'type': 'key_management',
                    'name': item.get('name', 'Unknown'),
                    'role': item.get('role', ''),
                    'associated_companies': item.get('associated_companies', ''),
                    'country_id': get_country_id(item.get('country')),
                    'source_url': item.get('source_url', ''),
                })

            for item in data.get('directors', []):
                self.env['pkf.ac.relationship.person'].create({
                    'evaluation_id': self.id,
                    'type': 'director',
                    'name': item.get('name', 'Unknown'),
                    'role': item.get('role', ''),
                    'associated_companies': item.get('associated_companies', ''),
                    'country_id': get_country_id(item.get('country')),
                    'source_url': item.get('source_url', ''),
                })

            return True

        except Exception as e:
            _logger.error(f"AI Research Failed: {str(e)}")
            raise UserError(_(f"AI Research Failed: {str(e)}"))

    key_management_ids = fields.One2many(
        "pkf.ac.relationship.person",
        "evaluation_id",
        string="Key Management Personnel",
        domain=[("type", "=", "key_management")],
    )

    director_ids = fields.One2many(
        "pkf.ac.relationship.person",
        "evaluation_id",
        string="Directors",
        domain=[("type", "=", "director")],
    )


class PkfAcRelationshipPerson(models.Model):
    _name = "pkf.ac.relationship.person"
    _description = "A&C Relationship Person"
    _order = "id asc"

    evaluation_id = fields.Many2one(
        "pkf.ac.evaluation",
        string="Evaluation",
        required=True,
        ondelete="cascade",
    )

    type = fields.Selection(
        [
            ("key_management", "Key Management Personnel"),
            ("director", "Director"),
        ],
        string="Type",
        required=True,
        default="key_management",
    )

    name = fields.Char(string="Name", required=True)
    role = fields.Char(string="Role")
    associated_companies = fields.Text(string="Associated Companies")
    country_id = fields.Many2one("res.country", string="Country")
    source_url = fields.Char(string="Source")
