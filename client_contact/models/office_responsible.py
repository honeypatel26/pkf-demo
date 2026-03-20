from odoo import api, fields, models


class OfficeResponsible(models.Model):
    _name = "office.responsible"
    _description = "Office Responsible"

    name = fields.Char(string="Office Responsible")
