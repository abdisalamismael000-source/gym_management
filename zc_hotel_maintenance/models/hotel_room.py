from odoo import api, fields, models


class HotelRoom(models.Model):
    _inherit = 'hotel.room'

    equipment_ids = fields.One2many(
        'maintenance.equipment', 'hotel_room_id', string='Equipment')
    maintenance_request_ids = fields.One2many(
        'maintenance.request', 'hotel_room_id', string='Maintenance Requests')
    open_request_count = fields.Integer(
        compute='_compute_open_request_count', string='Open Requests')

    @api.depends('maintenance_request_ids.stage_id.done')
    def _compute_open_request_count(self):
        for room in self:
            room.open_request_count = len(room.maintenance_request_ids.filtered(
                lambda r: not r.stage_id.done))

    def action_report_issue(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Report Issue',
            'res_model': 'maintenance.request',
            'view_mode': 'form',
            'target': 'current',
            'context': {
                'default_hotel_room_id': self.id,
                'default_name': 'Issue — Room %s' % self.name,
            },
        }

    def action_view_maintenance_requests(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Maintenance Requests',
            'res_model': 'maintenance.request',
            'view_mode': 'list,form',
            'domain': [('hotel_room_id', '=', self.id)],
            'context': {'default_hotel_room_id': self.id},
        }
