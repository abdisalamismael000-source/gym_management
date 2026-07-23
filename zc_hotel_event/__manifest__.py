{
    'name': 'Hotel Banquet & Events',
    'version': '19.0.1.0.0',
    'category': 'Services/Hotel',
    'summary': 'Book banquet halls and function rooms for weddings, conferences and events',
    'description': """
Hotel Banquet & Events
=====================

Manage the hotel's function rooms and banquet business:

* Define function rooms / banquet halls with capacity and hourly or day rate
* Book events (weddings, conferences, meetings) with no double-booking
* Track pax, setup style and status; invoice the organiser
""",
    'author': 'Zenith Consulting',
    'license': 'LGPL-3',
    'depends': ['zc_hotel'],
    'data': [
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'views/hotel_event_views.xml',
        'views/hotel_event_menus.xml',
    ],
    'demo': [
        'demo/event_demo.xml',
    ],
    'installable': True,
}
