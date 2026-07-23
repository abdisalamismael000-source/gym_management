from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    # --- Guest profile / CRM ---------------------------------------------
    is_hotel_guest = fields.Boolean(string='Is a Hotel Guest')
    id_type = fields.Selection([
        ('passport', 'Passport'),
        ('national_id', 'National ID'),
        ('driving_license', 'Driving License'),
        ('other', 'Other'),
    ], string='ID Type')
    id_number = fields.Char(string='ID Number')
    nationality_id = fields.Many2one('res.country', string='Nationality')
    date_of_birth = fields.Date(string='Date of Birth')
    guest_preferences = fields.Text(
        string='Guest Preferences',
        help='Pillow type, floor preference, allergies, VIP notes, etc.')
    vip = fields.Boolean(string='VIP Guest')
    loyalty_points = fields.Integer(string='Loyalty Points', default=0)

    # Corporate account flag — a company that reservations can be billed to.
    is_corporate_account = fields.Boolean(string='Corporate Account')

    reservation_ids = fields.One2many(
        'hotel.reservation', 'partner_id', string='Reservations')
    reservation_count = fields.Integer(
        compute='_compute_reservation_stats', string='Reservations')
    stay_count = fields.Integer(
        compute='_compute_reservation_stats', string='Completed Stays')

    @api.depends('reservation_ids', 'reservation_ids.state')
    def _compute_reservation_stats(self):
        for partner in self:
            reservations = partner.reservation_ids
            partner.reservation_count = len(reservations)
            partner.stay_count = len(
                reservations.filtered(lambda r: r.state == 'checked_out'))

    def action_view_guest_reservations(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Reservations',
            'res_model': 'hotel.reservation',
            'view_mode': 'list,form',
            'domain': [('partner_id', '=', self.id)],
            'context': {'default_partner_id': self.id},
        }
