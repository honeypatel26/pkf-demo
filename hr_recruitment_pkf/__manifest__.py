# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'HR Recruitment PKF',
    'summary': 'HR Recruitment PKF',
    "version": "19.0.1.0",
    'website': 'https://www.pkfantares.com',
    'author': 'PKF Antares',
    'description': """
        HR Recruitment PKF
    """,
    'category': 'Custom Development',
    'depends': [
        'hr_recruitment',
        'website_hr_recruitment',
        'hr',
        'hr_payroll',
    ],
    'data': [
        'security/security.xml',
        'views/hr_applicant_views.xml',
        'views/hr_employee_views.xml',
        'views/website_hr_recruitment_templates.xml',
    ],
    'application': False,
    'installable': True,
    'auto_install': False,
    'license': 'OEEL-1',
}
