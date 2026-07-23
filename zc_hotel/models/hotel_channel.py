from odoo import fields, models


class HotelChannel(models.Model):
    """OTA / distribution channel.

    This is a *scaffold*: it models the channels a hotel distributes through
    (Booking.com, Expedia, Airbnb, direct...) and lets reservations record
    their origin channel and external reference for reconciliation. Live
    two-way synchronisation with an OTA requires that provider's paid API and
    is intentionally left as an integration point (`_sync`) rather than a
    working connector.
    """
    _name = 'hotel.channel'
    _description = 'Distribution Channel'
    _order = 'sequence, name'

    name = fields.Char(required=True)
    sequence = fields.Integer(default=10)
    channel_type = fields.Selection([
        ('direct', 'Direct'),
        ('booking', 'Booking.com'),
        ('expedia', 'Expedia'),
        ('airbnb', 'Airbnb'),
        ('other', 'Other OTA'),
    ], default='other', required=True)
    commission_pct = fields.Float(
        string='Commission %',
        help='Commission charged by this channel, used in channel reporting.')
    active = fields.Boolean(default=True)

    def action_sync(self):
        """Placeholder for a live OTA sync.

        A real connector would push availability/rates and pull reservations
        through the provider API here. Left unimplemented on purpose — see the
        module README for how to wire a channel manager.
        """
        self.ensure_one()
        return False
