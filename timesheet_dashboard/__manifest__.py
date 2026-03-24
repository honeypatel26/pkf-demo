{
    'name': 'Timesheet Dashboard',
    'version': '1.0',
    'summary': 'Graphical representation of timesheets with billable status',
    'description': """
        This module adds a dashboard to the Timesheet Reporting section.
        It provides:
        - Total hours by Employee
        - Billable vs Non-Billable breakdown
        - Filters by Date (Year, Month)
        - Graph and Pivot views
    """,
    'category': 'Services/Timesheets',
    'author': 'PKF Antares',
    'depends': ['hr_timesheet', 'sale_timesheet', 'project'],
    'data': [
        'views/timesheet_dashboard_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
