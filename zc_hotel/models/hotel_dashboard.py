from datetime import timedelta

from odoo import api, fields, models

# Palette used to give guest avatars a stable, pleasant colour.
_AVATAR_COLORS = ['#3E9E6E', '#4C86C6', '#B08733', '#D2695F', '#7C6BB0', '#D99A2B']


def _avatar(name):
    name = (name or '?').strip()
    parts = name.split()
    initials = (parts[0][:1] + (parts[-1][:1] if len(parts) > 1 else '')).upper() or '?'
    color = _AVATAR_COLORS[sum(ord(c) for c in name) % len(_AVATAR_COLORS)]
    return initials, color


class HotelDashboard(models.AbstractModel):
    """Service model exposing front-desk KPIs and worklists to the OWL dashboard."""
    _name = 'hotel.dashboard'
    _description = 'Hotel Front Desk Dashboard'

    @api.model
    def _trend_series(self, days=7):
        """Per-day room revenue for the KPI sparkline / area chart."""
        FolioLine = self.env['hotel.folio.line']
        today = fields.Date.context_today(self)
        revenue, labels = [], []
        for i in range(days - 1, -1, -1):
            day = today - timedelta(days=i)
            lines = FolioLine.search([
                ('charge_type', '=', 'room'),
                ('date', '>=', fields.Datetime.to_datetime(day)),
                ('date', '<', fields.Datetime.to_datetime(day + timedelta(days=1))),
            ])
            revenue.append(round(sum(lines.mapped('price_subtotal')), 2))
            labels.append(day.strftime('%a'))
        return revenue, labels

    @api.model
    def _delta(self, current, previous):
        """Percentage change vs a previous period, rounded; None if not comparable."""
        if not previous:
            return None
        return round((current - previous) / previous * 100, 1)

    @api.model
    def get_dashboard_data(self):
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        week_ago = today - timedelta(days=7)
        Reservation = self.env['hotel.reservation']
        Room = self.env['hotel.room']
        FolioLine = self.env['hotel.folio.line']
        currency = self.env.company.currency_id

        # --- Room inventory -----------------------------------------------
        sellable_rooms = Room.search_count([('active', '=', True)])
        out_of_service = Room.search_count([('state', '=', 'out_of_service')])
        available_rooms = Room.search_count([('state', '=', 'available')])
        dirty_rooms = Room.search_count([('state', '=', 'dirty')])
        occupied_rooms = Room.search_count([('state', '=', 'occupied')])

        # --- Movements ----------------------------------------------------
        in_house = Reservation.search_count([('state', '=', 'checked_in')])
        active_res = Reservation.search_count([('state', 'in', ('confirmed', 'checked_in'))])

        # --- Revenue ------------------------------------------------------
        room_lines_mtd = FolioLine.search([
            ('charge_type', '=', 'room'),
            ('date', '>=', fields.Datetime.to_datetime(month_start)),
        ])
        room_revenue = sum(room_lines_mtd.mapped('price_subtotal'))
        rooms_sold = sum(room_lines_mtd.mapped('quantity')) or 0
        total_revenue = sum(FolioLine.search([
            ('date', '>=', fields.Datetime.to_datetime(month_start)),
        ]).mapped('price_subtotal'))

        net_sellable = max(sellable_rooms - out_of_service, 0)
        occupancy_rate = (occupied_rooms / net_sellable * 100) if net_sellable else 0.0
        adr = (room_revenue / rooms_sold) if rooms_sold else 0.0
        days_elapsed = (today - month_start).days + 1
        revpar = (room_revenue / (net_sellable * days_elapsed)) if net_sellable else 0.0

        # --- Deltas (this week vs previous week) --------------------------
        rev_this_week = sum(FolioLine.search([
            ('date', '>=', fields.Datetime.to_datetime(week_ago))]).mapped('price_subtotal'))
        rev_prev_week = sum(FolioLine.search([
            ('date', '>=', fields.Datetime.to_datetime(week_ago - timedelta(days=7))),
            ('date', '<', fields.Datetime.to_datetime(week_ago))]).mapped('price_subtotal'))
        arr_this_week = Reservation.search_count([('check_in', '>=', week_ago)])
        arr_prev_week = Reservation.search_count([
            ('check_in', '>=', week_ago - timedelta(days=7)), ('check_in', '<', week_ago)])

        revenue_trend, trend_labels = self._trend_series(7)

        return {
            'currency_symbol': currency.symbol,
            'currency_position': currency.position,
            'company_name': self.env.company.name,
            'today_label': today.strftime('%d %b %Y'),
            # KPIs
            'total_revenue': round(total_revenue, 2),
            'room_revenue': round(room_revenue, 2),
            'occupancy_rate': round(occupancy_rate, 1),
            'adr': round(adr, 2),
            'revpar': round(revpar, 2),
            'active_reservations': active_res,
            'in_house': in_house,
            'delta_revenue': self._delta(rev_this_week, rev_prev_week),
            'delta_arrivals': self._delta(arr_this_week, arr_prev_week),
            # charts
            'revenue_trend': revenue_trend,
            'trend_labels': trend_labels,
            'status_breakdown': [
                {'label': 'Available', 'value': available_rooms, 'color': '#3E9E6E'},
                {'label': 'Occupied', 'value': occupied_rooms, 'color': '#D2695F'},
                {'label': 'Cleaning', 'value': dirty_rooms, 'color': '#D99A2B'},
                {'label': 'Out of Service', 'value': out_of_service, 'color': '#8A857A'},
            ],
            'sellable_rooms': sellable_rooms,
            # worklists
            'arrivals': self._arrivals(today),
            'departures': self._departures(today),
            'upcoming': self._upcoming(today),
            'recent_bookings': self._recent_bookings(),
        }

    # ------------------------------------------------------------------
    # Worklists
    # ------------------------------------------------------------------
    @api.model
    def _arrivals(self, today):
        res = self.env['hotel.reservation'].search([
            ('check_in', '=', today),
            ('state', 'in', ('draft', 'confirmed')),
        ], order='room_id', limit=8)
        out = []
        for r in res:
            initials, color = _avatar(r.partner_id.name)
            out.append({
                'id': r.id, 'name': r.partner_id.name, 'initials': initials, 'color': color,
                'room': r.room_id.name, 'room_type': r.room_type_id.name,
                'nights': r.nights,
            })
        return out

    @api.model
    def _departures(self, today):
        res = self.env['hotel.reservation'].search([
            ('check_out', '=', today),
            ('state', '=', 'checked_in'),
        ], order='room_id', limit=8)
        out = []
        for r in res:
            initials, color = _avatar(r.partner_id.name)
            out.append({
                'id': r.id, 'name': r.partner_id.name, 'initials': initials, 'color': color,
                'room': r.room_id.name, 'room_type': r.room_type_id.name,
                'balance': round(r.folio_id.balance_due, 2) if r.folio_id else 0.0,
            })
        return out

    @api.model
    def _upcoming(self, today):
        res = self.env['hotel.reservation'].search([
            ('check_in', '>', today),
            ('state', 'in', ('draft', 'confirmed')),
        ], order='check_in', limit=6)
        out = []
        for r in res:
            out.append({
                'id': r.id, 'name': r.partner_id.name,
                'day': r.check_in.strftime('%d'), 'month': r.check_in.strftime('%b'),
                'room_type': r.room_type_id.name, 'nights': r.nights,
                'state': r.state,
            })
        return out

    @api.model
    def _recent_bookings(self):
        res = self.env['hotel.reservation'].search([], order='create_date desc', limit=6)
        state_labels = dict(self.env['hotel.reservation']._fields['state'].selection)
        out = []
        for r in res:
            out.append({
                'id': r.id, 'name': r.partner_id.name, 'ref': r.name,
                'check_in': r.check_in and r.check_in.strftime('%b %d') or '',
                'check_out': r.check_out and r.check_out.strftime('%b %d') or '',
                'amount': round(r.amount_total, 2),
                'state': r.state, 'state_label': state_labels.get(r.state, r.state),
            })
        return out

    # ------------------------------------------------------------------
    # Inline actions from the worklists
    # ------------------------------------------------------------------
    @api.model
    def check_in(self, reservation_id):
        self.env['hotel.reservation'].browse(reservation_id).action_check_in()
        return True

    @api.model
    def check_out(self, reservation_id):
        self.env['hotel.reservation'].browse(reservation_id).action_check_out()
        return True
