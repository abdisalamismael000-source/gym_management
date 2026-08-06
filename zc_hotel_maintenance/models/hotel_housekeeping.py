from odoo import models


class HotelHousekeeping(models.Model):
    _inherit = 'hotel.housekeeping'

    def action_report_issue(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Report Issue',
            'res_model': 'maintenance.request',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_hotel_room_id': self.room_id.id,
                'default_name': 'Issue — Room %s' % (self.room_id.name or ''),
                'default_block_room': True,
            },
        }
