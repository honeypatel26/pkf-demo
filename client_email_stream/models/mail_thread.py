import re
from odoo import models, api

EMAIL_RE = re.compile(r"([A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})", re.I)

def extract_email(s: str) -> str:
    if not s:
        return ""
    m = EMAIL_RE.search(s)
    return (m.group(1) or "").strip().lower() if m else ""

class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    @api.model
    def message_process(self, model, message, custom_values=None):
        # If Odoo already knows the target (reply/alias), keep default behavior
        if custom_values and custom_values.get("res_id"):
            return super().message_process(model, message, custom_values)

        email_from = extract_email(message.get("from"))
        if email_from:
            partner = self.env["res.partner"].sudo().search(
                [("email", "=", email_from)],
                limit=1
            )
            if partner:
                # Link the incoming email to the contact itself
                model = "res.partner"
                custom_values = dict(custom_values or {})
                custom_values["res_id"] = partner.id

        return super().message_process(model, message, custom_values)
