from odoo import fields, models


class HotelRoomType(models.Model):
    _name = 'hotel.room.type'
    _description = 'Hotel Room Type'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    code = fields.Char()
    sequence = fields.Integer(default=10)
    capacity = fields.Integer(string='Max Occupancy', default=2)
    list_price = fields.Monetary(string='Default Rate', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    product_id = fields.Many2one(
        'product.product', string='Room-night Product', required=True,
        domain=[('type', '=', 'service')],
        help='Product used to invoice a night in this room type.')
    room_ids = fields.One2many('hotel.room', 'room_type_id', string='Rooms')
    active = fields.Boolean(default=True)
