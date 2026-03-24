from odoo import api, fields, models


class Partner(models.Model):
    _name = "partner.partner"
    _description = "Partner"

    name = fields.Many2one("res.users",string="User",ondelete="cascade")
    country_id = fields.Many2one(related='name.partner_id.country_id', string="Country", readonly=True)
