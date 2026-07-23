from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_hotel_charge_mode = fields.Selection(
        related='pos_config_id.hotel_charge_mode', readonly=False)
    pos_hotel_folio_payment_method_id = fields.Many2one(
        related='pos_config_id.hotel_folio_payment_method_id', readonly=False)
