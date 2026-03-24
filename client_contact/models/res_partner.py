from odoo import models, fields

class ResPartner(models.Model):
    _inherit = 'res.partner'

    status = fields.Selection([
        ('lead', 'Lead'),
        ('active', 'Active'),
        ('vendor_partner', 'Vendor / Partner'),
        ('internal', 'Internal'),
    ], string="Current Status",copy=False,default="lead")
    division_id = fields.Many2one('division.division', string="Division",copy=False)
    year_end = fields.Date(string="Year End",copy=False)
    client_type_id = fields.Many2one('client.type', string="Client Type",copy=False)
    office_responsible_id = fields.Many2one('office.responsible', string="Office Responsible",copy=False)
    department_id = fields.Many2one('hr.department', string="Department",copy=False)
    regulator_id = fields.Many2one('regulator.regulator', string="Regulator",copy=False)
    partner_ids = fields.Many2many(
        'partner.partner',
        copy=False,
        string="Related Partners"
    )
    business_number = fields.Char(string="Business Number",copy=False)
    client_ref = fields.Char(string="Client ID", copy=False)
    source = fields.Char(string="Source")
