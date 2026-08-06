from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class HotelEventBooking(models.Model):
    _name = 'hotel.event.booking'
    _description = 'Event / Banquet Booking'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'start_datetime desc'

    name = fields.Char(string='Reference', required=True, copy=False,
                       readonly=True, default=lambda self: 'New')
    title = fields.Char(string='Event Title', required=True)
    partner_id = fields.Many2one('res.partner', string='Organiser', required=True)
    function_room_id = fields.Many2one(
        'hotel.function.room', string='Function Room', required=True)
    event_type = fields.Selection([
        ('wedding', 'Wedding'),
        ('conference', 'Conference'),
        ('meeting', 'Meeting'),
        ('party', 'Party'),
        ('other', 'Other'),
    ], default='conference', required=True)
    start_datetime = fields.Datetime(string='Start', required=True)
    end_datetime = fields.Datetime(string='End', required=True)
    pax = fields.Integer(string='Guests (pax)', default=1)
    setup_style = fields.Selection([
        ('theatre', 'Theatre'),
        ('classroom', 'Classroom'),
        ('banquet', 'Banquet'),
        ('ushape', 'U-Shape'),
        ('cocktail', 'Cocktail'),
    ], default='banquet')
    amount = fields.Monetary(string='Quoted Amount', currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'Enquiry'),
        ('confirmed', 'Confirmed'),
        ('done', 'Completed'),
        ('invoiced', 'Invoiced'),
        ('cancelled', 'Cancelled'),
    ], default='draft', required=True, tracking=True)
    move_id = fields.Many2one('account.move', string='Invoice', copy=False)
    notes = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.constrains('start_datetime', 'end_datetime')
    def _check_dates(self):
        for rec in self:
            if rec.start_datetime and rec.end_datetime \
                    and rec.end_datetime <= rec.start_datetime:
                raise ValidationError("Event end must be after its start.")

    @api.constrains('function_room_id', 'start_datetime', 'end_datetime', 'state')
    def _check_room_availability(self):
        blocking = ('draft', 'confirmed', 'done', 'invoiced')
        for rec in self:
            if rec.state not in blocking or not (rec.start_datetime and rec.end_datetime):
                continue
            conflict = self.search([
                ('id', '!=', rec.id),
                ('function_room_id', '=', rec.function_room_id.id),
                ('state', 'in', blocking),
                ('start_datetime', '<', rec.end_datetime),
                ('end_datetime', '>', rec.start_datetime),
            ], limit=1)
            if conflict:
                raise ValidationError(
                    "%(room)s is already booked for that slot by %(ref)s." % {
                        'room': rec.function_room_id.name, 'ref': conflict.name})

    @api.constrains('pax', 'function_room_id')
    def _check_capacity(self):
        for rec in self:
            if rec.function_room_id and rec.pax > rec.function_room_id.capacity:
                raise ValidationError(
                    "%(pax)s pax exceeds %(room)s capacity (%(cap)s)." % {
                        'pax': rec.pax, 'room': rec.function_room_id.name,
                        'cap': rec.function_room_id.capacity})

    @api.onchange('function_room_id')
    def _onchange_function_room(self):
        if self.function_room_id and not self.amount:
            self.amount = self.function_room_id.day_rate

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hotel.event.booking') or 'New'
        return super().create(vals_list)

    def action_confirm(self):
        self.write({'state': 'confirmed'})

    def action_done(self):
        self.write({'state': 'done'})

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def action_invoice(self):
        self.ensure_one()
        if self.move_id:
            raise UserError("This event is already invoiced.")
        product = self.function_room_id.product_id
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id if product else False,
                'name': '%s — %s' % (self.title, self.function_room_id.name),
                'quantity': 1,
                'price_unit': self.amount,
            })],
        })
        self.write({'move_id': move.id, 'state': 'invoiced'})
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
        }
