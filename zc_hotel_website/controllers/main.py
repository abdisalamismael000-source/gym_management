from datetime import date, datetime

from odoo import fields, http
from odoo.http import request


class HotelBookingController(http.Controller):

    def _parse_date(self, value):
        if not value:
            return False
        try:
            return fields.Date.to_date(value)
        except (ValueError, TypeError):
            return False

    @http.route(['/hotel/rooms'], type='http', auth='public', website=True, sitemap=True)
    def hotel_rooms(self, **kw):
        room_types = request.env['hotel.room.type'].sudo().search(
            [('active', '=', True)])
        return request.render('zc_hotel_website.rooms_page', {
            'room_types': room_types,
        })

    @http.route(['/hotel/booking'], type='http', auth='public', website=True, sitemap=True)
    def hotel_booking(self, **kw):
        check_in = self._parse_date(kw.get('check_in'))
        check_out = self._parse_date(kw.get('check_out'))
        try:
            guests = int(kw.get('guests') or 1)
        except ValueError:
            guests = 1

        results = []
        error = None
        if check_in and check_out:
            if check_out <= check_in:
                error = "Check-out must be after check-in."
            elif check_in < date.today():
                error = "Check-in cannot be in the past."
            else:
                Reservation = request.env['hotel.reservation'].sudo()
                rooms = Reservation.get_available_rooms(check_in, check_out)
                # One offer per room type with a free room and enough capacity.
                by_type = {}
                for room in rooms:
                    rt = room.room_type_id
                    if rt.capacity < guests:
                        continue
                    if rt.id not in by_type:
                        nights = (check_out - check_in).days
                        rate = request.env['hotel.rate.plan'].sudo()._get_average_rate(
                            rt, check_in, check_out)
                        by_type[rt.id] = {
                            'room_type': rt,
                            'room': room,
                            'nights': nights,
                            'rate': rate,
                            'total': rate * nights,
                        }
                results = list(by_type.values())

        return request.render('zc_hotel_website.booking_page', {
            'check_in': check_in,
            'check_out': check_out,
            'guests': guests,
            'results': results,
            'error': error,
            'today': date.today(),
        })

    @http.route(['/hotel/booking/confirm'], type='http', auth='public',
                website=True, methods=['POST'], csrf=True)
    def hotel_booking_confirm(self, **post):
        check_in = self._parse_date(post.get('check_in'))
        check_out = self._parse_date(post.get('check_out'))
        room_id = int(post.get('room_id') or 0)
        name = (post.get('name') or '').strip()
        email = (post.get('email') or '').strip()

        if not (check_in and check_out and room_id and name and email):
            return request.render('zc_hotel_website.booking_error', {
                'message': "Missing information. Please complete the form.",
            })

        Reservation = request.env['hotel.reservation'].sudo()
        available = Reservation.get_available_rooms(check_in, check_out)
        room = request.env['hotel.room'].sudo().browse(room_id)
        if room not in available:
            return request.render('zc_hotel_website.booking_error', {
                'message': "Sorry, that room was just taken. Please search again.",
            })

        Partner = request.env['res.partner'].sudo()
        partner = Partner.search([('email', '=', email)], limit=1)
        if not partner:
            partner = Partner.create({
                'name': name, 'email': email, 'is_hotel_guest': True,
            })

        try:
            adults = max(int(post.get('guests') or 1), 1)
        except ValueError:
            adults = 1

        reservation = Reservation.create({
            'partner_id': partner.id,
            'room_id': room.id,
            'check_in': check_in,
            'check_out': check_out,
            'adults': adults,
            'source': 'website',
        })
        reservation.action_confirm()

        return request.render('zc_hotel_website.booking_thanks', {
            'reservation': reservation,
        })
