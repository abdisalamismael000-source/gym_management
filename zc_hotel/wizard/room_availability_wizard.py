from odoo import api, fields, models
from odoo.exceptions import UserError


class RoomAvailabilityWizard(models.TransientModel):
    _name = 'hotel.room.availability.wizard'
    _description = 'Check Room Availability'

    check_in = fields.Date(required=True, default=fields.Date.context_today)
    check_out = fields.Date(required=True)
    room_type_id = fields.Many2one('hotel.room.type', string='Room Type')
    partner_id = fields.Many2one('res.partner', string='Guest')
    available_room_ids = fields.Many2many(
        'hotel.room', compute='_compute_available_rooms', string='Available Rooms')
    available_count = fields.Integer(
        compute='_compute_available_rooms', string='Rooms Free')

    @api.depends('check_in', 'check_out', 'room_type_id')
    def _compute_available_rooms(self):
        for wiz in self:
            if wiz.check_in and wiz.check_out and wiz.check_out > wiz.check_in:
                rooms = self.env['hotel.reservation'].get_available_rooms(
                    wiz.check_in, wiz.check_out,
                    room_type_id=wiz.room_type_id.id or None)
            else:
                rooms = self.env['hotel.room'].browse()
            wiz.available_room_ids = rooms
            wiz.available_count = len(rooms)

    def action_create_reservation(self):
        self.ensure_one()
        if self.check_out <= self.check_in:
            raise UserError("Check-out must be after check-in.")
        return {
            'type': 'ir.actions.act_window',
            'name': 'New Reservation',
            'res_model': 'hotel.reservation',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_check_in': self.check_in,
                'default_check_out': self.check_out,
                'default_partner_id': self.partner_id.id,
            },
        }
