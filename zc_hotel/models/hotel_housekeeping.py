from odoo import api, fields, models


class HotelHousekeeping(models.Model):
    _name = 'hotel.housekeeping'
    _description = 'Housekeeping Task'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'scheduled_date desc, id desc'

    name = fields.Char(string='Reference', compute='_compute_name', store=True)
    room_id = fields.Many2one('hotel.room', string='Room', required=True, tracking=True)
    reservation_id = fields.Many2one('hotel.reservation', string='Reservation')
    task_type = fields.Selection([
        ('cleaning', 'Cleaning'),
        ('turndown', 'Turndown'),
        ('inspection', 'Inspection'),
        ('deep_clean', 'Deep Clean'),
    ], default='cleaning', required=True, tracking=True)
    employee_id = fields.Many2one('hr.employee', string='Assigned To', tracking=True)
    scheduled_date = fields.Date(default=fields.Date.context_today)
    state = fields.Selection([
        ('todo', 'To Do'),
        ('in_progress', 'In Progress'),
        ('done', 'Done'),
        ('cancelled', 'Cancelled'),
    ], default='todo', required=True, tracking=True)
    priority = fields.Selection([
        ('0', 'Normal'),
        ('1', 'Urgent'),
    ], default='0')
    notes = fields.Text()
    company_id = fields.Many2one('res.company', default=lambda self: self.env.company)

    @api.depends('room_id', 'task_type')
    def _compute_name(self):
        type_labels = dict(self._fields['task_type'].selection)
        for rec in self:
            room = rec.room_id.name or '?'
            rec.name = "%s — %s" % (room, type_labels.get(rec.task_type, ''))

    def action_start(self):
        self.write({'state': 'in_progress'})

    def action_done(self):
        for rec in self:
            rec.state = 'done'
            # A completed cleaning/inspection frees the room for the next guest.
            if rec.task_type in ('cleaning', 'deep_clean', 'inspection') \
                    and rec.room_id.state == 'dirty':
                rec.room_id.state = 'available'

    def action_cancel(self):
        self.write({'state': 'cancelled'})
