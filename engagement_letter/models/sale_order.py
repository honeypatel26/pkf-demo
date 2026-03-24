from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    engagement_letter_id = fields.Many2one("engagement.letter", string="Engagement Letter", copy=False)

    def action_view_engagement_letter(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "engagement.letter",
            "res_id": self.engagement_letter_id.id,
            "view_mode": "form",
            "target": "current",
        }
