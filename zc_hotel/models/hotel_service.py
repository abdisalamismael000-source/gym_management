from odoo import api, fields, models
from odoo.exceptions import UserError


class HotelServiceBooking(models.Model):
    """Scheduled extra services — spa, airport transfer, tours, late checkout.

    Booking a service can post its price straight to the guest's open folio,
    so everything settles together at check-out.
    """
    _name = 'hotel.service.booking'
    _description = 'Guest Service Booking'
    _inherit = ['mail.thread']
    _order = 'scheduled_date desc, id desc'

    name = fields.Char(string='Reference', required=True, copy=False,
                       readonly=True, default=lambda self: 'New')
    partner_id = fields.Many2one('res.partner', string='Guest', required=True)
    reservation_id = fields.Many2one('hotel.reservation', string='Reservation')
    folio_id = fields.Many2one('hotel.folio', string='Folio')
    service_type = fields.Selection([
        ('spa', 'Spa & Wellness'),
        ('transfer', 'Airport Transfer'),
        ('tour', 'Tour / Excursion'),
        ('laundry', 'Laundry'),
        ('late_checkout', 'Late Check-out'),
        ('other', 'Other'),
    ], default='spa', required=True, string='Service')
    product_id = fields.Many2one(
        'product.product', string='Product',
        domain=[('type', '=', 'service')])
    employee_id = fields.Many2one('hr.employee', string='Assigned Staff')
    scheduled_date = fields.Datetime(default=fields.Datetime.now)
    quantity = fields.Float(default=1.0)
    price_unit = fields.Monetary(currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('booked', 'Booked'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='draft', required=True, tracking=True)
    charged = fields.Boolean(string='Posted to Folio', copy=False)
    notes = fields.Text()

    @api.onchange('product_id')
    def _onchange_product_id(self):
        if self.product_id:
            self.price_unit = self.product_id.list_price

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code(
                    'hotel.service.booking') or 'New'
            # Default the folio from the reservation when possible.
            if vals.get('reservation_id') and not vals.get('folio_id'):
                res = self.env['hotel.reservation'].browse(vals['reservation_id'])
                if res.folio_id:
                    vals['folio_id'] = res.folio_id.id
        return super().create(vals_list)

    def action_book(self):
        self.write({'state': 'booked'})

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            rec._post_to_folio()

    def action_cancel(self):
        self.write({'state': 'cancelled'})

    def _post_to_folio(self):
        self.ensure_one()
        folio = self.folio_id or self.reservation_id.folio_id
        if not folio:
            raise UserError(
                "No open folio for this guest. Check the guest in first, or "
                "link a folio before posting the charge.")
        if self.charged:
            return
        charge_type = 'spa' if self.service_type == 'spa' else (
            'laundry' if self.service_type == 'laundry' else 'service')
        self.env['hotel.folio.line'].create({
            'folio_id': folio.id,
            'product_id': self.product_id.id if self.product_id else False,
            'name': '%s — %s' % (dict(self._fields['service_type'].selection).get(
                self.service_type), self.name),
            'quantity': self.quantity,
            'price_unit': self.price_unit,
            'charge_type': charge_type,
        })
        self.write({'charged': True, 'folio_id': folio.id})
