from odoo import models, fields

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # Extend payroll security to allow our sensitive info group to read these fields
    # to prevent view access rights inconsistencies
    contract_date_start = fields.Date(groups="hr_payroll.group_hr_payroll_user,hr_recruitment_pkf.group_employee_sensitive_info")
    contract_date_end = fields.Date(groups="hr_payroll.group_hr_payroll_user,hr_recruitment_pkf.group_employee_sensitive_info")
