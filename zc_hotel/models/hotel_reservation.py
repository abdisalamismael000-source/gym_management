from odoo import api, fields, models
from odoo.exceptions import UserError


class HotelReservation(models.Model):
    _name = 'hotel.reservation'
    _description = 'Hotel Reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'check_in desc'

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: ('New'))
    partner_id = fields.Many2one('res.partner', string='Guest', required=True, tracking=True)
    room_id = fields.Many2one('hotel.room', string='Room', required=True, tracking=True)
    room_type_id = fields.Many2one(related='room_id.room_type_id', store=True)
    check_in = fields.Date(required=True, tracking=True)
    check_out = fields.Date(required=True, tracking=True)
    nights = fields.Integer(compute='_compute_nights', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
    ], default='draft', required=True, tracking=True)
    folio_id = fields.Many2one('hotel.folio', string='Folio', copy=False)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('check_in', 'check_out')
    def _compute_nights(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                rec.nights = max((rec.check_out - rec.check_in).days, 0)
            else:
                rec.nights = 0

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hotel.reservation') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_check_in(self):
        for rec in self:
            if rec.state not in ('draft', 'confirmed'):
                raise UserError(("Only draft or confirmed reservations can be checked in."))
            folio = rec.folio_id or self.env['hotel.folio'].create({
                'partner_id': rec.partner_id.id,
                'reservation_id': rec.id,
            })
            folio._add_room_charge(rec)
            rec.write({'state': 'checked_in', 'folio_id': folio.id})
            rec.room_id.state = 'occupied'
            folio.state = 'open'

    def action_check_out(self):
        for rec in self:
            if rec.state != 'checked_in':
                raise UserError(("Only checked-in reservations can be checked out."))
            rec.state = 'checked_out'
            rec.room_id.state = 'dirty'
            if rec.folio_id:
                rec.folio_id.action_close()

    def action_cancel(self):
        self.write({'state': 'cancelled'})
