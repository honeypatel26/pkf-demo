# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Contact Fields',
    'summary': 'Added mandatory fields inside the contact app',
    'version': '1.0',
    'license': 'LGPL-3',
    'author': 'PKF Antares',
    'depends': ['base', 'contacts', 'hr_expense', 'hr'],

    'data': [
        'security/ir.model.access.csv',
        'views/partner_views.xml',
        'views/regulator_views.xml',
        'views/office_responsible_views.xml',
        'views/division.xml',
        'views/hr_expense_view_form.xml',
        'views/client_type.xml',
        'views/contact_views.xml',
        'views/res_partner_view.xml',
    ],

    'installable': True,
    'application': False,
    'auto_install': False,
}
