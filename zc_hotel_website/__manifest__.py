{
    'name': 'Hotel Online Booking',
    'version': '19.0.1.0.0',
    'category': 'Website/Website',
    'summary': 'Public room search and online booking engine for the Hotel PMS',
    'description': """
Hotel Online Booking
===================

A direct booking engine that saves OTA commissions:

* Public "Our Rooms" page built from the hotel room types
* Live availability search by dates and guests (no double-booking)
* Guest details form that creates a confirmed reservation (source = Website)
* "My Bookings" portal page for signed-in guests
""",
    'author': 'Zenith Consulting',
    'license': 'LGPL-3',
    'depends': ['zc_hotel', 'website', 'portal'],
    'data': [
        'views/website_templates.xml',
        'views/portal_templates.xml',
        'views/website_menus.xml',
    ],
    'installable': True,
}
