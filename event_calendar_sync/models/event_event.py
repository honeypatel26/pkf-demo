from odoo import models, fields, api


class EventEvent(models.Model):
    _inherit = 'event.event'

    calendar_event_id = fields.Many2one('calendar.event', string='Calendar Event', readonly=True, copy=False)

    @api.model_create_multi
    def create(self, vals_list):
        events = super(EventEvent, self).create(vals_list)
        for event in events:
            event._create_calendar_event()
        return events

    def write(self, vals):
        # Capture old responsible partners before change
        old_responsibles = {}
        if 'user_id' in vals:
            for event in self:
                if event.user_id:
                    old_responsibles[event.id] = event.user_id.partner_id.id

        res = super(EventEvent, self).write(vals)

        if 'name' in vals or 'date_begin' in vals or 'date_end' in vals or 'user_id' in vals:
            for event in self:
                if event.calendar_event_id:
                    # Remove old responsible from attendees if changed
                    if event.id in old_responsibles:
                        old_partner_id = old_responsibles[event.id]
                        if event.user_id.partner_id.id != old_partner_id:
                            event.calendar_event_id.write({
                                'partner_ids': [(3, old_partner_id)]
                            })

                    event._update_calendar_event()
                else:
                    event._create_calendar_event()
        return res

    def unlink(self):
        for event in self:
            if event.calendar_event_id:
                event.calendar_event_id.unlink()
        return super(EventEvent, self).unlink()

    def _create_calendar_event(self):
        self.ensure_one()
        if not self.calendar_event_id:
            vals = self._get_calendar_event_vals()
            calendar_event = self.env['calendar.event'].create(vals)
            self.calendar_event_id = calendar_event.id

    def _update_calendar_event(self):
        self.ensure_one()
        if self.calendar_event_id:
            vals = self._get_calendar_event_vals()
            self.calendar_event_id.write(vals)

    def _get_calendar_event_vals(self):
        self.ensure_one()
        vals = {
            'name': self.name,
            'start': self.date_begin,
            'stop': self.date_end,
            'user_id': self.user_id.id or self.create_uid.id or self.env.user.id,
            'description': 'Created from Event: %s' % self.name,
            'privacy': 'public',
            'event_id': self.id,
        }

        # Add responsible or creator as attendee without removing existing ones
        # Command (4, id) adds relationship, preserving other attendees
        if self.user_id and self.user_id.partner_id:
            vals['partner_ids'] = [(4, self.user_id.partner_id.id)]
        elif self.create_uid and self.create_uid.partner_id:
            vals['partner_ids'] = [(4, self.create_uid.partner_id.id)]

        return vals

    def action_view_calendar_event(self):
        self.ensure_one()
        return {
            'name': 'Calendar Event',
            'type': 'ir.actions.act_window',
            'res_model': 'calendar.event',
            'view_mode': 'form',
            'res_id': self.calendar_event_id.id,
            'target': 'current',
        }
