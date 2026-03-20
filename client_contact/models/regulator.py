from odoo import api, fields, models


class Regulator(models.Model):
    _name = "regulator.regulator"
    _description = "Regulator"

    name = fields.Char(string="Regulator")
