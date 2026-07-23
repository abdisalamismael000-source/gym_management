from odoo import api, fields, models
from odoo.exceptions import UserError


class HotelFolio(models.Model):
    _name = 'hotel.folio'
    _description = 'Guest Folio'
    _inherit = ['mail.thread']
    _order = 'create_date desc'

    name = fields.Char(
        required=True, copy=False, readonly=True, default=lambda self: ('New'))
    partner_id = fields.Many2one('res.partner', string='Guest', required=True)
    reservation_id = fields.Many2one('hotel.reservation', string='Reservation')
    room_id = fields.Many2one(related='reservation_id.room_id', store=True)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('open', 'Open'),
        ('checked_out', 'Checked Out'),
        ('invoiced', 'Invoiced'),
        ('closed', 'Closed'),
    ], default='draft', required=True, tracking=True)
    charge_line_ids = fields.One2many('hotel.folio.line', 'folio_id', string='Charges')
    move_ids = fields.Many2many('account.move', string='Invoices', copy=False)
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    amount_total = fields.Monetary(compute='_compute_amounts', store=True)
    amount_invoiced = fields.Monetary(compute='_compute_amounts', store=True)
    amount_due = fields.Monetary(compute='_compute_amounts', store=True)

    @api.depends('charge_line_ids.price_subtotal', 'move_ids.amount_total',
                 'move_ids.payment_state')
    def _compute_amounts(self):
        for folio in self:
            total = sum(folio.charge_line_ids.mapped('price_subtotal'))
            invoiced = sum(folio.move_ids.filtered(
                lambda m: m.state == 'posted').mapped('amount_total'))
            folio.amount_total = total
            folio.amount_invoiced = invoiced
            folio.amount_due = total - invoiced

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hotel.folio') or 'New'
        return super().create(vals_list)

    def _add_room_charge(self, reservation):
        self.ensure_one()
        room_type = reservation.room_type_id
        if not room_type.product_id:
            raise UserError((
                "Room type %s has no room-night product configured.") % room_type.name)
        self.env['hotel.folio.line'].create({
            'folio_id': self.id,
            'product_id': room_type.product_id.id,
            'name': ("Room %(room)s — %(nights)s night(s)") % {
                'room': reservation.room_id.name,
                'nights': reservation.nights,
            },
            'quantity': reservation.nights or 1,
            'price_unit': room_type.list_price,
            'charge_type': 'room',
        })

    def action_close(self):
        self.write({'state': 'checked_out'})

    def action_invoice(self):
        self.ensure_one()
        if not self.charge_line_ids:
            raise UserError(("Nothing to invoice on this folio."))
        move_lines = []
        for line in self.charge_line_ids:
            move_lines.append((0, 0, {
                'product_id': line.product_id.id,
                'name': line.name,
                'quantity': line.quantity,
                'price_unit': line.price_unit,
                'tax_ids': [(6, 0, line.tax_ids.ids)],
            }))
        move = self.env['account.move'].create({
            'move_type': 'out_invoice',
            'partner_id': self.partner_id.id,
            'invoice_origin': self.name,
            'invoice_line_ids': move_lines,
        })
        self.move_ids = [(4, move.id)]
        self.state = 'invoiced'
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'account.move',
            'res_id': move.id,
            'view_mode': 'form',
        }


class HotelFolioLine(models.Model):
    _name = 'hotel.folio.line'
    _description = 'Folio Charge Line'
    _order = 'date, id'

    folio_id = fields.Many2one('hotel.folio', required=True, ondelete='cascade')
    partner_id = fields.Many2one(related='folio_id.partner_id', store=True)
    date = fields.Datetime(default=fields.Datetime.now)
    product_id = fields.Many2one('product.product', string='Product')
    name = fields.Char(string='Description', required=True)
    quantity = fields.Float(default=1.0)
    price_unit = fields.Monetary(currency_field='currency_id')
    tax_ids = fields.Many2many('account.tax', string='Taxes')
    price_subtotal = fields.Monetary(compute='_compute_subtotal', store=True,
                                     currency_field='currency_id')
    currency_id = fields.Many2one(related='folio_id.currency_id', store=True)
    charge_type = fields.Selection([
        ('room', 'Room'),
        ('restaurant', 'Restaurant'),
        ('minibar', 'Minibar'),
        ('service', 'Service'),
        ('other', 'Other'),
    ], default='other', required=True)

    @api.depends('quantity', 'price_unit')
    def _compute_subtotal(self):
        for line in self:
            line.price_subtotal = line.quantity * line.price_unit
