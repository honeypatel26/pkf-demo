from odoo import models, fields

class CalendarEvent(models.Model):
    _inherit = 'calendar.event'

    event_id = fields.Many2one('event.event', string='Related Event', readonly=True)

    def action_view_event(self):
        self.ensure_one()
        return {
            'name': 'Event',
            'type': 'ir.actions.act_window',
            'res_model': 'event.event',
            'view_mode': 'form',
            'res_id': self.event_id.id,
            'target': 'current',
        }

