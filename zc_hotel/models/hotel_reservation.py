from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class HotelReservation(models.Model):
    _name = 'hotel.reservation'
    _description = 'Hotel Reservation'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'check_in desc'

    name = fields.Char(
        string='Reference', required=True, copy=False, readonly=True,
        default=lambda self: ('New'))
    partner_id = fields.Many2one('res.partner', string='Guest', required=True, tracking=True)
    company_account_id = fields.Many2one(
        'res.partner', string='Corporate Account',
        domain=[('is_corporate_account', '=', True)],
        help='Company the stay is billed to, if different from the guest.')
    room_id = fields.Many2one('hotel.room', string='Room', required=True, tracking=True)
    room_type_id = fields.Many2one(related='room_id.room_type_id', store=True)
    check_in = fields.Date(required=True, tracking=True, default=fields.Date.context_today)
    check_out = fields.Date(required=True, tracking=True)
    arrival_time = fields.Char(string='Expected Arrival')
    nights = fields.Integer(compute='_compute_nights', store=True)
    adults = fields.Integer(default=1)
    children = fields.Integer(default=0)
    board_type = fields.Selection([
        ('ro', 'Room Only'),
        ('bb', 'Bed & Breakfast'),
        ('hb', 'Half Board'),
        ('fb', 'Full Board'),
    ], string='Board', default='ro')
    source = fields.Selection([
        ('direct', 'Direct / Walk-in'),
        ('phone', 'Phone'),
        ('website', 'Website'),
        ('ota', 'OTA / Channel'),
        ('corporate', 'Corporate'),
    ], default='direct', string='Source', tracking=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('no_show', 'No Show'),
        ('cancelled', 'Cancelled'),
    ], default='draft', required=True, tracking=True)
    folio_id = fields.Many2one('hotel.folio', string='Folio', copy=False)
    deposit_amount = fields.Monetary(string='Deposit', currency_field='currency_id')
    amount_total = fields.Monetary(
        compute='_compute_amount_total', string='Folio Total',
        currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('check_in', 'check_out')
    def _compute_nights(self):
        for rec in self:
            if rec.check_in and rec.check_out:
                rec.nights = max((rec.check_out - rec.check_in).days, 0)
            else:
                rec.nights = 0

    @api.depends('folio_id.amount_total')
    def _compute_amount_total(self):
        for rec in self:
            rec.amount_total = rec.folio_id.amount_total if rec.folio_id else 0.0

    # ------------------------------------------------------------------
    # Constraints — availability / integrity
    # ------------------------------------------------------------------
    @api.constrains('check_in', 'check_out')
    def _check_dates(self):
        for rec in self:
            if rec.check_in and rec.check_out and rec.check_out <= rec.check_in:
                raise ValidationError(
                    "Check-out (%(out)s) must be after check-in (%(in)s)." % {
                        'out': rec.check_out, 'in': rec.check_in})

    @api.constrains('room_id', 'check_in', 'check_out', 'state')
    def _check_room_availability(self):
        """Prevent double-booking the same room for overlapping dates.

        The checkout day of one stay may equal the check-in day of the next
        (same-day turnover), so overlap is strict: A.in < B.out AND A.out > B.in.
        """
        blocking_states = ('draft', 'confirmed', 'checked_in')
        for rec in self:
            if rec.state not in blocking_states or not (rec.check_in and rec.check_out):
                continue
            conflict = self.search([
                ('id', '!=', rec.id),
                ('room_id', '=', rec.room_id.id),
                ('state', 'in', blocking_states),
                ('check_in', '<', rec.check_out),
                ('check_out', '>', rec.check_in),
            ], limit=1)
            if conflict:
                raise ValidationError(
                    "Room %(room)s is already booked for those dates by %(ref)s "
                    "(%(cin)s → %(cout)s)." % {
                        'room': rec.room_id.name,
                        'ref': conflict.name,
                        'cin': conflict.check_in,
                        'cout': conflict.check_out,
                    })

    # ------------------------------------------------------------------
    # Availability helper — reused by dashboard, wizard and website
    # ------------------------------------------------------------------
    @api.model
    def get_available_rooms(self, check_in, check_out, room_type_id=None):
        """Return a hotel.room recordset free for the given window."""
        if isinstance(check_in, str):
            check_in = fields.Date.to_date(check_in)
        if isinstance(check_out, str):
            check_out = fields.Date.to_date(check_out)
        room_domain = [('active', '=', True), ('state', '!=', 'out_of_service')]
        if room_type_id:
            room_domain.append(('room_type_id', '=', room_type_id))
        rooms = self.env['hotel.room'].search(room_domain)
        if not (check_in and check_out):
            return rooms
        overlapping = self.search([
            ('state', 'in', ('draft', 'confirmed', 'checked_in')),
            ('check_in', '<', check_out),
            ('check_out', '>', check_in),
        ])
        booked_room_ids = overlapping.mapped('room_id').ids
        return rooms.filtered(lambda r: r.id not in booked_room_ids)

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hotel.reservation') or 'New'
            if vals.get('partner_id'):
                self.env['res.partner'].browse(vals['partner_id']).sudo().write(
                    {'is_hotel_guest': True})
        return super().create(vals_list)

    # ------------------------------------------------------------------
    # Workflow
    # ------------------------------------------------------------------
    def action_confirm(self):
        self.write({'state': 'confirmed'})
        template = self.env.ref(
            'zc_hotel.mail_template_reservation_confirmation',
            raise_if_not_found=False)
        if template:
            for rec in self.filtered(lambda r: r.partner_id.email):
                template.send_mail(rec.id, force_send=False)

    def action_check_in(self):
        for rec in self:
            if rec.state not in ('draft', 'confirmed'):
                raise UserError("Only draft or confirmed reservations can be checked in.")
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
                raise UserError("Only checked-in reservations can be checked out.")
            rec.state = 'checked_out'
            rec.room_id.state = 'dirty'
            # Award a simple loyalty point per night stayed.
            if rec.partner_id and rec.nights:
                rec.partner_id.sudo().loyalty_points += rec.nights
            if rec.folio_id:
                rec.folio_id.action_close()
            # Auto-create a housekeeping cleaning task for turnover.
            self.env['hotel.housekeeping'].sudo().create({
                'room_id': rec.room_id.id,
                'reservation_id': rec.id,
                'task_type': 'cleaning',
                'scheduled_date': fields.Date.context_today(rec),
            })

    def action_no_show(self):
        for rec in self:
            if rec.state not in ('draft', 'confirmed'):
                raise UserError("Only draft or confirmed reservations can be marked no-show.")
            rec.state = 'no_show'

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_view_folio(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.folio',
            'res_id': self.folio_id.id,
            'view_mode': 'form',
        }
