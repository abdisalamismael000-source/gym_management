from odoo import api, fields, models


class PosOrder(models.Model):
    _inherit = 'pos.order'

    folio_id = fields.Many2one(
        'hotel.folio', string='Room Folio', index='btree_not_null', copy=False)

    @api.model
    def _load_pos_data_fields(self, config_id):
        fields_ = super()._load_pos_data_fields(config_id)
        if 'folio_id' not in fields_:
            fields_.append('folio_id')
        return fields_

    def _create_folio_charges(self):
        """Copy this order's lines onto the linked folio, tagged by outlet."""
        FolioLine = self.env['hotel.folio.line']
        for order in self.filtered('folio_id'):
            # Outlet type on the POS drives the folio charge category.
            charge_type = order.config_id.hotel_outlet_type or 'restaurant'
            if charge_type == 'other':
                charge_type = 'service'
            # Avoid duplicating charges if the order is processed twice.
            existing = FolioLine.search([('pos_order_line_id', 'in', order.lines.ids)])
            charged_lines = existing.mapped('pos_order_line_id')
            for line in order.lines - charged_lines:
                FolioLine.create({
                    'folio_id': order.folio_id.id,
                    'product_id': line.product_id.id,
                    'name': line.full_product_name or line.product_id.display_name,
                    'quantity': line.qty,
                    'price_unit': line.price_unit,
                    'tax_ids': [(6, 0, line.tax_ids.ids)],
                    'charge_type': charge_type,
                    'pos_order_line_id': line.id,
                })

    def _process_saved_order(self, draft):
        order = super()._process_saved_order(draft)
        if order.folio_id and order.config_id.hotel_charge_mode == 'folio':
            order._create_folio_charges()
        return order
