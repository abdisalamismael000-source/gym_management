from odoo import api, fields, models


class HotelRatePlan(models.Model):
    _name = 'hotel.rate.plan'
    _description = 'Hotel Rate Plan'
    _order = 'date_start desc, room_type_id'

    name = fields.Char(required=True)
    room_type_id = fields.Many2one(
        'hotel.room.type', string='Room Type', required=True, ondelete='cascade')
    date_start = fields.Date(string='Valid From', required=True)
    date_end = fields.Date(string='Valid To', required=True)
    price = fields.Monetary(string='Nightly Rate', required=True,
                            currency_field='currency_id')
    currency_id = fields.Many2one(
        'res.currency', default=lambda self: self.env.company.currency_id)
    min_stay = fields.Integer(string='Minimum Nights', default=1)
    board_type = fields.Selection([
        ('ro', 'Room Only'),
        ('bb', 'Bed & Breakfast'),
        ('hb', 'Half Board'),
        ('fb', 'Full Board'),
    ], string='Board', default='ro')
    active = fields.Boolean(default=True)

    _sql_constraints = [
        ('price_positive', 'CHECK(price >= 0)', 'The nightly rate cannot be negative.'),
    ]

    @api.model
    def _get_rate(self, room_type, day):
        """Return the applicable nightly rate for a room type on a given date.

        Falls back to the room type's default rate when no plan matches.
        """
        if not room_type:
            return 0.0
        plan = self.search([
            ('room_type_id', '=', room_type.id),
            ('date_start', '<=', day),
            ('date_end', '>=', day),
            ('active', '=', True),
        ], order='price asc', limit=1)
        return plan.price if plan else room_type.list_price

    @api.model
    def _get_average_rate(self, room_type, check_in, check_out):
        """Average nightly rate across a stay (per-night rate-plan aware)."""
        if not room_type or not check_in or not check_out:
            return room_type.list_price if room_type else 0.0
        nights = (check_out - check_in).days
        if nights <= 0:
            return room_type.list_price
        total = 0.0
        day = check_in
        for _ in range(nights):
            total += self._get_rate(room_type, day)
            day = fields.Date.add(day, days=1)
        return total / nights
