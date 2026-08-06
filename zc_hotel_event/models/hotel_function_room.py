from odoo import fields, models


class HotelFunctionRoom(models.Model):
    _name = 'hotel.function.room'
    _description = 'Function Room / Banquet Hall'
    _order = 'name'

    name = fields.Char(required=True)
    property_id = fields.Many2one('hotel.property', string='Property')
    capacity = fields.Integer(string='Max Capacity (pax)', default=50)
    day_rate = fields.Monetary(string='Day Rate', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    product_id = fields.Many2one(
        'product.product', string='Hire Product',
        domain=[('type', '=', 'service')],
        help='Service product used to invoice hire of this hall.')
    amenity_ids = fields.Many2many('hotel.amenity', string='Facilities')
    active = fields.Boolean(default=True)
