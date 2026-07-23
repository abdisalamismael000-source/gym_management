from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class HotelPortal(CustomerPortal):

    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'booking_count' in counters:
            partner = request.env.user.partner_id
            values['booking_count'] = request.env['hotel.reservation'].search_count(
                [('partner_id', '=', partner.id)])
        return values

    @http.route(['/my/bookings'], type='http', auth='user', website=True)
    def portal_my_bookings(self, **kw):
        partner = request.env.user.partner_id
        reservations = request.env['hotel.reservation'].search(
            [('partner_id', '=', partner.id)], order='check_in desc')
        return request.render('zc_hotel_website.portal_my_bookings', {
            'reservations': reservations,
            'page_name': 'bookings',
        })
