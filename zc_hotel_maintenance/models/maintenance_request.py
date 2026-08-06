from odoo import api, fields, models


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    hotel_room_id = fields.Many2one('hotel.room', string='Hotel Room')


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    hotel_room_id = fields.Many2one('hotel.room', string='Hotel Room')
    block_room = fields.Boolean(
        string='Take Room Out of Service',
        help='While this request is open, the linked room is set out of service.')

    @api.model_create_multi
    def create(self, vals_list):
        requests = super().create(vals_list)
        requests._sync_room_out_of_service()
        return requests

    def write(self, vals):
        res = super().write(vals)
        if {'stage_id', 'block_room', 'hotel_room_id'} & set(vals):
            self._sync_room_out_of_service()
        return res

    def _sync_room_out_of_service(self):
        for req in self.filtered(lambda r: r.hotel_room_id and r.block_room):
            room = req.hotel_room_id
            if req.stage_id and req.stage_id.done:
                # Repair finished: send the room to cleaning before reuse.
                if room.state == 'out_of_service':
                    room.state = 'dirty'
            else:
                if room.state != 'occupied':
                    room.state = 'out_of_service'
