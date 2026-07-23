from odoo import api, fields, models


class HotelFolio(models.Model):
    # Extend the folio and make it loadable into the POS session bundle.
    _inherit = ['hotel.folio', 'pos.load.mixin']

    pos_order_ids = fields.One2many('pos.order', 'folio_id', string='POS Orders')

    @api.model
    def _load_pos_data_domain(self, data):
        # Only currently open stays are chargeable in POS.
        return [('state', '=', 'open')]

    @api.model
    def _load_pos_data_fields(self, config_id):
        return ['id', 'name', 'partner_id', 'room_id', 'state', 'amount_due']


class HotelFolioLine(models.Model):
    _inherit = 'hotel.folio.line'

    pos_order_line_id = fields.Many2one('pos.order.line', string='POS Line', copy=False)
