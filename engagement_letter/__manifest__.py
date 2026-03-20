# engagement_letter/__manifest__.py
{
    "name": "Engagement Letter",
    "version": "19.0.1.0.0",
    "category": "Sales",
    "summary": "Engagement Letters with multiple templates selection (ordered) and PDF preview",
    "author": "PKF-Jake H",
    "license": "LGPL-3",
    "depends": [
        "base",
        "mail",
        "contacts",
        "sale_management",
        "sign",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/sequence.xml",
        "data/mail_templates.xml",
        "views/sale_order_views.xml",
        "views/engagement_letter_views.xml",
        "views/engagement_template_views.xml",
        "views/menu.xml",
        "report/engagement_letter_report.xml",
    ],
    "application": True,
    "installable": True,
}
