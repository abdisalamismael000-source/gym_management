{
    'name': 'Hotel Management',
    'version': '19.0.2.0.0',
    'category': 'Services/Hotel',
    'summary': 'Complete hotel PMS: reservations, availability, front-desk dashboard, '
               'housekeeping, rate plans, guest CRM, folios and night-audit reports',
    'description': """
Hotel Management
================

A complete Property Management System (PMS) for hotels, resorts and guesthouses:

* Reservations with real availability (no double-booking) and a calendar planner
* Front-desk dashboard with Occupancy, ADR and RevPAR KPIs
* Housekeeping task board integrated with room status
* Seasonal rate plans and board types (RO/BB/HB/FB)
* Guest CRM with ID, nationality, preferences and loyalty points
* Guest folios, city tax, deposits and one-click invoicing
* Owner report pack: manager flash, arrivals, departures, in-house,
  room status, guest ledger, revenue by room type, occupancy and no-show
""",
    'author': 'Zenith Consulting',
    'website': 'https://www.example.com',
    'license': 'LGPL-3',
    'depends': [
        'base', 'mail', 'account', 'product', 'stock', 'hr', 'contacts',
    ],
    'data': [
        'security/hotel_security.xml',
        'security/ir.model.access.csv',
        'data/ir_sequence.xml',
        'data/mail_template.xml',
        'report/hotel_report_actions.xml',
        'report/hotel_folio_report.xml',
        'report/hotel_registration_report.xml',
        'report/hotel_night_audit_report.xml',
        'views/hotel_property_views.xml',
        'views/hotel_room_views.xml',
        'views/hotel_amenity_views.xml',
        'views/hotel_rate_plan_views.xml',
        'views/hotel_reservation_views.xml',
        'views/hotel_folio_views.xml',
        'views/hotel_housekeeping_views.xml',
        'views/hotel_service_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'wizard/room_availability_wizard_views.xml',
        'wizard/hotel_report_wizard_views.xml',
        'views/hotel_dashboard_views.xml',
        'views/hotel_menus.xml',
    ],
    'demo': [
        'demo/hotel_demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'zc_hotel/static/src/dashboard/**/*',
        ],
    },
    'installable': True,
    'application': True,
}
