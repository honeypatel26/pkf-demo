from odoo import api, fields, models


class ClientType(models.Model):
    _name = "client.type"
    _description = "client Type"


    name = fields.Char(string="client Type")

