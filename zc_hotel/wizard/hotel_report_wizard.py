from odoo import api, fields, models


class HotelReportWizard(models.TransientModel):
    _name = 'hotel.report.wizard'
    _description = 'Hotel Management Reports'

    report_type = fields.Selection([
        ('flash', 'Manager Flash / Daily Report'),
        ('arrivals', 'Arrivals'),
        ('departures', 'Departures'),
        ('in_house', 'In-house Guests'),
        ('room_status', 'Room / Housekeeping Status'),
        ('guest_ledger', 'Guest Ledger (Outstanding)'),
        ('revenue_type', 'Revenue by Room Type'),
        ('occupancy', 'Occupancy (range)'),
        ('no_show', 'No-show / Cancellation'),
        ('police', 'Police / Guest Registration'),
    ], default='flash', required=True, string='Report')
    date_from = fields.Date(default=fields.Date.context_today, required=True)
    date_to = fields.Date(default=fields.Date.context_today, required=True)

    def action_print(self):
        self.ensure_one()
        return self.env.ref('zc_hotel.action_report_night_audit').report_action(self)

    # ------------------------------------------------------------------
    # Data helpers used by the QWeb report template
    # ------------------------------------------------------------------
    def _reservations_between(self, field, states):
        return self.env['hotel.reservation'].search([
            (field, '>=', self.date_from),
            (field, '<=', self.date_to),
            ('state', 'in', states),
        ], order=field)

    def get_report_values(self):
        self.ensure_one()
        Reservation = self.env['hotel.reservation']
        Room = self.env['hotel.room']
        FolioLine = self.env['hotel.folio.line']
        rtype = self.report_type
        values = {'wizard': self, 'rtype': rtype}

        if rtype == 'arrivals':
            values['reservations'] = self._reservations_between(
                'check_in', ('draft', 'confirmed', 'checked_in'))
        elif rtype == 'departures':
            values['reservations'] = self._reservations_between(
                'check_out', ('checked_in', 'checked_out'))
        elif rtype == 'in_house':
            values['reservations'] = Reservation.search(
                [('state', '=', 'checked_in')], order='room_id')
        elif rtype == 'no_show':
            values['reservations'] = Reservation.search([
                ('state', 'in', ('no_show', 'cancelled')),
                ('check_in', '>=', self.date_from),
                ('check_in', '<=', self.date_to),
            ], order='check_in')
        elif rtype == 'police':
            values['reservations'] = self._reservations_between(
                'check_in', ('confirmed', 'checked_in', 'checked_out'))
        elif rtype == 'room_status':
            values['rooms'] = Room.search([('active', '=', True)], order='name')
        elif rtype == 'guest_ledger':
            values['folios'] = self.env['hotel.folio'].search([
                ('amount_due', '>', 0),
            ], order='partner_id')
        elif rtype == 'revenue_type':
            domain = [
                ('charge_type', '=', 'room'),
                ('date', '>=', fields.Datetime.to_datetime(self.date_from)),
                ('date', '<=', fields.Datetime.to_datetime(self.date_to)),
            ]
            lines = FolioLine.search(domain)
            buckets = {}
            for line in lines:
                rt = line.folio_id.room_id.room_type_id
                key = rt.name or 'Undefined'
                bucket = buckets.setdefault(key, {'nights': 0.0, 'revenue': 0.0})
                bucket['nights'] += line.quantity
                bucket['revenue'] += line.price_subtotal
            values['revenue_rows'] = buckets
        elif rtype in ('flash', 'occupancy'):
            values.update(self._get_flash_values())
        return values

    def _get_flash_values(self):
        Reservation = self.env['hotel.reservation']
        Room = self.env['hotel.room']
        FolioLine = self.env['hotel.folio.line']
        today = self.date_to

        total_rooms = Room.search_count([('active', '=', True)])
        out_of_service = Room.search_count([('state', '=', 'out_of_service')])
        occupied = Room.search_count([('state', '=', 'occupied')])
        net_sellable = max(total_rooms - out_of_service, 0)

        room_lines = FolioLine.search([
            ('charge_type', '=', 'room'),
            ('date', '>=', fields.Datetime.to_datetime(self.date_from)),
            ('date', '<=', fields.Datetime.to_datetime(today)),
        ])
        pos_lines = FolioLine.search([
            ('charge_type', 'in', ('restaurant', 'bar', 'spa', 'minibar')),
            ('date', '>=', fields.Datetime.to_datetime(self.date_from)),
            ('date', '<=', fields.Datetime.to_datetime(today)),
        ])
        room_revenue = sum(room_lines.mapped('price_subtotal'))
        pos_revenue = sum(pos_lines.mapped('price_subtotal'))
        rooms_sold = sum(room_lines.mapped('quantity')) or 0

        occupancy = (occupied / net_sellable * 100) if net_sellable else 0.0
        adr = (room_revenue / rooms_sold) if rooms_sold else 0.0
        revpar = (room_revenue / net_sellable) if net_sellable else 0.0

        return {
            'total_rooms': total_rooms,
            'occupied': occupied,
            'available': Room.search_count([('state', '=', 'available')]),
            'dirty': Room.search_count([('state', '=', 'dirty')]),
            'out_of_service': out_of_service,
            'no_shows': Reservation.search_count([
                ('state', '=', 'no_show'),
                ('check_in', '>=', self.date_from),
                ('check_in', '<=', today)]),
            'room_revenue': room_revenue,
            'pos_revenue': pos_revenue,
            'total_revenue': room_revenue + pos_revenue,
            'occupancy': round(occupancy, 1),
            'adr': round(adr, 2),
            'revpar': round(revpar, 2),
            'company': self.env.company,
        }
