# -*- coding: utf-8 -*-

from odoo import fields, models


class EngagementLetter(models.Model):
    _inherit = "engagement.letter"

    evaluation_id = fields.Many2one(
        "pkf.ac.evaluation",
        string="A&C Evaluation",
        tracking=True,
    )

    def action_view_ac_evaluation(self):
        self.ensure_one()
        if not self.evaluation_id:
            return
        return {
            "name": "A&C Evaluation",
            "type": "ir.actions.act_window",
            "res_model": "pkf.ac.evaluation",
            "res_id": self.evaluation_id.id,
            "view_mode": "form",
            "target": "current",
        }
