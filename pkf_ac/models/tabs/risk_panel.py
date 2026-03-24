# -*- coding: utf-8 -*-
from odoo import fields, models,api

class RiskPanel(models.Model):
    _inherit = "pkf.ac.evaluation"

    select_review_type = fields.Selection(
            [
                ('internal', 'Internal'),
                ('external', 'External'),
            ],
            string="Select Type",
            store=True,
            copy=True,
        )

    committee_member_ids = fields.Many2many(
            comodel_name='res.users',
            relation='pkf_ac_eval_committee_rel',
            column1='evaluation_id',
            column2='user_id',
            string="Internal Member(s)",
            store=True,
            copy=True,
            domain=lambda self: [('all_group_ids', 'in', self.env.ref('pkf_ac.group_pkf_ac_partner').id)])


    risk_score = fields.Selection(
            [
                ('n_a', 'N/A'),
                ('low', '1 - Low'),
                ('medium', '2 - Medium'),
                ('high', '3 - High'),
            ],
            string="Risk Score",
            store=True,
            tracking=True,
            copy=True,
        )

    override_explanation_reasoning = fields.Text(
            string="Override Explanation/ Reasoning",
            store=True,
            copy=True,
        )

    external_member = fields.Many2one(
        comodel_name='res.partner',
        string="External Member",
        copy=True,
    )
