{
    'name': 'Event Calendar Sync',
    'version': '1.0',
    'category': 'Marketing',
    'summary': 'Sync Events to Main Calendar',
    'description': """
        This module creates a Calendar Event automatically when an Event is created in the Events app.
        It keeps the Calendar Event synchronized with the Event's details (name, start/end time).
    """,
    'depends': ['event', 'calendar'],
    'data': [
        'views/event_event_views.xml',
        'views/calendar_event_views.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'LGPL-3',
}
