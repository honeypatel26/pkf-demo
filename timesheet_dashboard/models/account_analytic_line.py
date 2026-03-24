# -*- coding: utf-8 -*-
from odoo import models, fields, api

class AccountAnalyticLine(models.Model):
    _inherit = 'account.analytic.line'

    billable_category = fields.Selection([
        ('billable', 'Billable'),
        ('non_billable', 'Non-Billable')
    ], string="Billable Category", compute='_compute_billable_category', store=True)

    @api.depends('timesheet_invoice_type')
    def _compute_billable_category(self):
        for line in self:
            if not line.timesheet_invoice_type or line.timesheet_invoice_type in ['non_billable', 'other_costs', 'other_revenues']:
                line.billable_category = 'non_billable'
            else:
                line.billable_category = 'billable'
