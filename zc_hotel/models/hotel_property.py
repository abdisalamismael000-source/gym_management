from odoo import api, fields, models


class HotelProperty(models.Model):
    _name = 'hotel.property'
    _description = 'Hotel Property'
    _order = 'name'

    name = fields.Char(required=True)
    code = fields.Char(help='Short code used as a prefix, e.g. GV for Grand Vista.')
    company_id = fields.Many2one(
        'res.company', string='Company', default=lambda self: self.env.company)
    partner_id = fields.Many2one(
        'res.partner', string='Address',
        help='Contact holding the property address and details.')
    room_ids = fields.One2many('hotel.room', 'property_id', string='Rooms')
    room_count = fields.Integer(compute='_compute_counts', string='Rooms')
    active = fields.Boolean(default=True)

    @api.depends('room_ids')
    def _compute_counts(self):
        for prop in self:
            prop.room_count = len(prop.room_ids)
