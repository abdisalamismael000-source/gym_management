from odoo import fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    hotel_city_tax_per_night = fields.Monetary(
        string='City Tax per Night',
        help='Fixed tourism / city tax added to each folio per night stayed. '
             'Set to 0 to disable.')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    hotel_city_tax_per_night = fields.Monetary(
        related='company_id.hotel_city_tax_per_night', readonly=False)
