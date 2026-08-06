{
    'name': 'Hotel Maintenance',
    'version': '19.0.1.0.0',
    'category': 'Services/Hotel',
    'summary': 'Link hotel rooms to maintenance equipment and raise repair tickets',
    'description': """
Hotel Maintenance
=================

Connects the Hotel Management PMS with Odoo Maintenance:

* Attach maintenance equipment (AC, TV, plumbing...) to each room
* Raise a maintenance request straight from a room or housekeeping task
* A room with an open blocking request is automatically taken out of service
""",
    'author': 'Zenith Consulting',
    'license': 'LGPL-3',
    'depends': ['zc_hotel', 'maintenance'],
    'data': [
        'views/hotel_room_views.xml',
        'views/hotel_housekeeping_views.xml',
    ],
    'installable': True,
}
