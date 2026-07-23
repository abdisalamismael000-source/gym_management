{
    'name': 'Hotel POS Folio Integration',
    'version': '19.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Charge Point of Sale orders to a hotel guest room folio',
    'author': 'Zenith Consulting',
    'license': 'LGPL-3',
    'depends': ['zc_hotel', 'point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'views/pos_config_views.xml',
        'views/hotel_folio_views.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'zc_hotel_pos/static/src/js/**/*.js',
            'zc_hotel_pos/static/src/xml/**/*.xml',
        ],
    },
    'installable': True,
}
