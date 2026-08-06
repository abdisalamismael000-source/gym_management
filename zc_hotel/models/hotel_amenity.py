from odoo import fields, models


class HotelAmenity(models.Model):
    _name = 'hotel.amenity'
    _description = 'Hotel Amenity'
    _order = 'sequence, name'

    name = fields.Char(required=True, translate=True)
    sequence = fields.Integer(default=10)
    icon = fields.Char(
        string='Font Awesome Icon',
        help="Optional Font Awesome class, e.g. 'fa-wifi' or 'fa-tv'.")
    active = fields.Boolean(default=True)
