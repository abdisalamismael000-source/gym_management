from odoo import fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'

    hotel_charge_mode = fields.Selection([
        ('folio', 'Post to room folio (settle at checkout)'),
        ('report', 'Link guest for reporting only'),
    ], string='Hotel Charge Mode', default='report',
        help="How restaurant/POS orders connect to a hotel guest.\n"
             "- Post to room folio: the order is charged to the guest's folio "
             "and settled at checkout.\n"
             "- Reporting only: the order is paid normally, the folio link is "
             "kept for reporting.")
    hotel_folio_payment_method_id = fields.Many2one(
        'pos.payment.method', string='Room Folio Payment Method',
        help="Customer-account payment method used to post an order to a guest "
             "folio. Configure it with the journal left blank and 'Identify "
             "Customer' enabled so it posts to the guest receivable.")
