# -*- coding: utf-8 -*-

from odoo import api, fields, models

class PkfAcBudgetLine(models.Model):
    _name = "pkf.ac.budget.line"
    _description = "A&C Budget Line"
    _order = "id asc"

    evaluation_id = fields.Many2one(
        "pkf.ac.evaluation",
        string="Evaluation",
        required=True,
        ondelete="cascade",
    )
    
    budget_type = fields.Selection(
        [
            ("current", "Current Budget"),
            ("prior_budget", "Prior Budget (Estimated)"),
            ("prior_actual", "Prior Actual"),
        ],
        string="Budget Type",
        required=True,
        default="current",
    )

    job_position_id = fields.Many2one(
        "pkf.ac.job.position",
        string="Job Position",
    )
    hourly_rate = fields.Monetary(string="Hourly Rate", currency_field="currency_id", compute="_compute_hourly_rate",
                                  store=True,readonly=False)
    hours = fields.Float(string="Hours", default=0.0)
    billable_amount = fields.Monetary(
        string="Billable amount",
        compute="_compute_billable_amount",
        store=True,
        currency_field="currency_id",
    )
    
    currency_id = fields.Many2one(
        "res.currency",
        related="evaluation_id.currency_id",
        string="Currency",
        readonly=True,
    )

    @api.depends("hourly_rate", "hours")
    def _compute_billable_amount(self):
        for rec in self:
            rec.billable_amount = rec.hourly_rate * rec.hours

    @api.depends("job_position_id.hourly_rate")
    def _compute_hourly_rate(self):
        for rec in self:
            if rec.job_position_id:
                rec.hourly_rate = rec.job_position_id.hourly_rate

class PkfAcEvaluationBudget(models.Model):
    _inherit = "pkf.ac.evaluation"

    # =========================
    # Current Budget
    # =========================
    current_budget_line_ids = fields.One2many(
        "pkf.ac.budget.line",
        "evaluation_id",
        string="Current Budget Lines",
        domain=[("budget_type", "=", "current")],
    )

    current_budget_file = fields.Binary(string="Upload Budget")
    current_budget_file_name = fields.Char(string="File Name")

    current_budget_discount = fields.Float(string="Discount")
    
    current_total_hours = fields.Float(
        string="Total Hours",
        compute="_compute_current_budget_totals",
        store=True,
    )
    current_total_billable = fields.Monetary(
        string="Total Billable",
        compute="_compute_current_budget_totals",
        store=True,
        currency_field="currency_id",
    )

    @api.depends("current_budget_line_ids.hours", "current_budget_line_ids.billable_amount", "current_budget_discount")
    def _compute_current_budget_totals(self):
        for rec in self:
            lines = rec.current_budget_line_ids
            rec.current_total_hours = sum(lines.mapped("hours"))
            total_billable = sum(lines.mapped("billable_amount"))
            rec.current_total_billable = total_billable + rec.current_budget_discount

    # =========================
    # Prior Budget (Estimated)
    # =========================
    show_prior_budget = fields.Boolean(string="Show Prior Budget", default=False)

    def action_toggle_prior_budget(self):
        for rec in self:
            rec.show_prior_budget = not rec.show_prior_budget

    prior_budget_line_ids = fields.One2many(
        "pkf.ac.budget.line",
        "evaluation_id",
        string="Prior Budget Lines",
        domain=[("budget_type", "=", "prior_budget")],
    )

    prior_budget_file = fields.Binary(string="Upload Budget")
    prior_budget_file_name = fields.Char(string="File Name")

    prior_budget_discount = fields.Float(string="Discount")
    
    prior_total_hours = fields.Float(
        string="Total Hours",
        compute="_compute_prior_budget_totals",
        store=True,
    )
    prior_total_billable = fields.Monetary(
        string="Total Billable",
        compute="_compute_prior_budget_totals",
        store=True,
        currency_field="currency_id",
    )

    @api.depends("prior_budget_line_ids.hours", "prior_budget_line_ids.billable_amount", "prior_budget_discount")
    def _compute_prior_budget_totals(self):
        for rec in self:
            lines = rec.prior_budget_line_ids
            rec.prior_total_hours = sum(lines.mapped("hours"))
            total_billable = sum(lines.mapped("billable_amount"))
            rec.prior_total_billable = total_billable + rec.prior_budget_discount

    # =========================
    # Prior Actual
    # =========================
    prior_actual_line_ids = fields.One2many(
        "pkf.ac.budget.line",
        "evaluation_id",
        string="Prior Actual Lines",
        domain=[("budget_type", "=", "prior_actual")],
    )

    prior_actual_file = fields.Binary(string="Upload Budget")
    prior_actual_file_name = fields.Char(string="File Name")

    prior_actual_discount = fields.Float(string="Discount")
    
    prior_actual_total_hours = fields.Float(
        string="Total Hours",
        compute="_compute_prior_actual_totals",
        store=True,
    )
    prior_actual_total_billable = fields.Monetary(
        string="Total Billable",
        compute="_compute_prior_actual_totals",
        store=True,
        currency_field="currency_id",
    )

    @api.depends("prior_actual_line_ids.hours", "prior_actual_line_ids.billable_amount", "prior_actual_discount")
    def _compute_prior_actual_totals(self):
        for rec in self:
            lines = rec.prior_actual_line_ids
            rec.prior_actual_total_hours = sum(lines.mapped("hours"))
            total_billable = sum(lines.mapped("billable_amount"))
            rec.prior_actual_total_billable = total_billable + rec.prior_actual_discount

    # =========================
    # Comparison (Prior Actual - Prior Budget)
    # =========================
    prior_budget_difference_amount = fields.Monetary(
        string="Difference($)",
        compute="_compute_prior_budget_difference",
        currency_field="currency_id",
    )
    prior_budget_difference_percent = fields.Char(
        string="Difference(%)",
        compute="_compute_prior_budget_difference",
    )

    @api.depends("prior_actual_total_billable", "prior_total_billable")
    def _compute_prior_budget_difference(self):
        for rec in self:
            diff = rec.prior_actual_total_billable - rec.prior_total_billable
            rec.prior_budget_difference_amount = diff
            
            if rec.prior_total_billable:
                percent = (diff / rec.prior_total_billable) * 100
                rec.prior_budget_difference_percent = f"{round(percent, 2)}%"
            else:
                rec.prior_budget_difference_percent = "0%"
