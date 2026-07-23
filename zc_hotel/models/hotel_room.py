from odoo import api, fields, models


class HotelRoom(models.Model):
    _name = 'hotel.room'
    _description = 'Hotel Room'
    _order = 'name'

    name = fields.Char(string='Room Number', required=True)
    room_type_id = fields.Many2one('hotel.room.type', string='Room Type', required=True)
    floor = fields.Char()
    capacity = fields.Integer(related='room_type_id.capacity', store=True,
                              string='Max Occupancy')
    amenity_ids = fields.Many2many('hotel.amenity', string='Amenities')
    state = fields.Selection([
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('dirty', 'Needs Cleaning'),
        ('out_of_service', 'Out of Service'),
    ], default='available', required=True, tracking=True)
    current_reservation_id = fields.Many2one(
        'hotel.reservation', string='Current Stay', compute='_compute_current_reservation')
    current_guest_id = fields.Many2one(
        'res.partner', string='Current Guest',
        related='current_reservation_id.partner_id')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('name_uniq', 'unique(name)', 'Room number must be unique.'),
    ]

    @api.depends('state')
    def _compute_current_reservation(self):
        for room in self:
            res = self.env['hotel.reservation'].search([
                ('room_id', '=', room.id),
                ('state', '=', 'checked_in'),
            ], limit=1)
            room.current_reservation_id = res

    def action_set_available(self):
        self.write({'state': 'available'})

    def action_set_dirty(self):
        self.write({'state': 'dirty'})

    def action_set_out_of_service(self):
        self.write({'state': 'out_of_service'})
