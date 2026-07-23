from odoo import api, fields, models


class HotelDashboard(models.AbstractModel):
    """Service model exposing front-desk KPIs to the OWL dashboard."""
    _name = 'hotel.dashboard'
    _description = 'Hotel Front Desk Dashboard'

    @api.model
    def get_dashboard_data(self):
        today = fields.Date.context_today(self)
        month_start = today.replace(day=1)
        Reservation = self.env['hotel.reservation']
        Room = self.env['hotel.room']
        FolioLine = self.env['hotel.folio.line']

        # --- Room inventory ------------------------------------------------
        sellable_rooms = Room.search_count([('active', '=', True)])
        out_of_service = Room.search_count([('state', '=', 'out_of_service')])
        available_rooms = Room.search_count([('state', '=', 'available')])
        dirty_rooms = Room.search_count([('state', '=', 'dirty')])
        occupied_rooms = Room.search_count([('state', '=', 'occupied')])

        # --- Today's movements --------------------------------------------
        arrivals = Reservation.search_count([
            ('check_in', '=', today),
            ('state', 'in', ('draft', 'confirmed', 'checked_in')),
        ])
        departures = Reservation.search_count([
            ('check_out', '=', today),
            ('state', 'in', ('checked_in', 'checked_out')),
        ])
        in_house = Reservation.search_count([('state', '=', 'checked_in')])

        # --- Revenue metrics (month to date) ------------------------------
        room_lines = FolioLine.search([
            ('charge_type', '=', 'room'),
            ('date', '>=', fields.Datetime.to_datetime(month_start)),
        ])
        room_revenue = sum(room_lines.mapped('price_subtotal'))
        rooms_sold = sum(room_lines.mapped('quantity')) or 0
        total_revenue = sum(FolioLine.search([
            ('date', '>=', fields.Datetime.to_datetime(month_start)),
        ]).mapped('price_subtotal'))

        # --- KPIs ----------------------------------------------------------
        # Occupancy: rooms currently occupied / sellable rooms.
        net_sellable = max(sellable_rooms - out_of_service, 0)
        occupancy_rate = (occupied_rooms / net_sellable * 100) if net_sellable else 0.0
        # ADR: room revenue / room-nights sold.
        adr = (room_revenue / rooms_sold) if rooms_sold else 0.0
        # RevPAR: room revenue / available room-nights this month.
        days_elapsed = (today - month_start).days + 1
        available_room_nights = net_sellable * days_elapsed
        revpar = (room_revenue / available_room_nights) if available_room_nights else 0.0

        return {
            'currency_id': self.env.company.currency_id.id,
            'currency_symbol': self.env.company.currency_id.symbol,
            'sellable_rooms': sellable_rooms,
            'available_rooms': available_rooms,
            'occupied_rooms': occupied_rooms,
            'dirty_rooms': dirty_rooms,
            'out_of_service': out_of_service,
            'arrivals': arrivals,
            'departures': departures,
            'in_house': in_house,
            'occupancy_rate': round(occupancy_rate, 1),
            'adr': round(adr, 2),
            'revpar': round(revpar, 2),
            'room_revenue': round(room_revenue, 2),
            'total_revenue': round(total_revenue, 2),
        }
