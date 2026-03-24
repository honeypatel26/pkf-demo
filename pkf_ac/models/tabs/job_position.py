# -*- coding: utf-8 -*-

from odoo import fields, models
from odoo.models import Constraint


class PkfAcJobPosition(models.Model):
    _name = "pkf.ac.job.position"
    _description = "A&C Job Position"
    _order = "name asc"

    name = fields.Char(string="Job Position", required=True)

    _constraints = [Constraint(["name"], "unique")]


    hourly_rate = fields.Monetary(
    string="Hourly Rate",
    currency_field="currency_id",
)

    currency_id = fields.Many2one(
    "res.currency",
    default=lambda self: self.env.company.currency_id.id,
)


