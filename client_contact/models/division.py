from odoo import api, fields, models


class Division(models.Model):
    _name = "division.division"
    _description = "Division"

    name = fields.Char(string="Division")
