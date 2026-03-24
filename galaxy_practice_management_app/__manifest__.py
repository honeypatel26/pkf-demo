{
    "name": "GPMA",
    "version": "1.0.0",
    "category": "Custom Development",
    "summary": "Unified interface for CRM, Projects, Subscriptions, Sales, Helpdesk, Timesheets, Sign, Contacts, and Documents",
    "description": "All applications are accessible from one centralized menu, replacing the need to navigate between separate apps",
    "author": "PKF Antares",
    "website": "https://www.pkfantares.com",
    "license": "LGPL-3",
    "depends": ["contacts", "account_accountant", "crm", "project", "sale", "sale_subscription", "sign", "documents", "helpdesk", "timesheet_grid", "hr_timesheet", "sale_timesheet"],
    "data": [
        "data/project_task_cron.xml",
        "views/client_action.xml",
        "views/gpma_menu.xml",
        "views/project_task_views.xml",
        "views/payment_form_extension.xml",
    ],
    "assets": {
        'web.assets_backend': [
            'galaxy_practice_management_app/static/src/**/*',
        ],
    },
    "installable": True,
    "application": True,
    "auto_install": False,
}
