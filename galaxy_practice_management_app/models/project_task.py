# -*- coding: utf-8 -*-
from odoo import models, api, fields, _
from datetime import datetime, time

class ProjectTask(models.Model):
    _inherit = 'project.task'

    is_last_recurrence = fields.Boolean(compute='_compute_is_last_recurrence')
    invoice_ids = fields.Many2many('account.move', compute='_compute_invoice_ids', string="Invoices", copy=False)
    invoice_count = fields.Integer(compute='_compute_invoice_ids', string="Invoice Count")
    invoice_no = fields.Char(compute='_compute_invoice_ids', string="Invoice No", store=False)
    sub_task_invoice_nos = fields.Char(compute='_compute_sub_task_invoice_nos', string="Subtask Invoices", recursive=True)
    uninvoiced_hours = fields.Float(compute='_compute_uninvoiced_hours', string="Remaining to Invoice", recursive=True)
    total_uninvoiced_hours = fields.Float(compute='_compute_uninvoiced_hours', string="Total Remaining to Invoice",
                                          recursive=True)

    @api.depends('recurrence_id')
    def _compute_is_last_recurrence(self):
        for task in self:
            if not task.recurrence_id:
                task.is_last_recurrence = False
                continue
            last_task_id = task.recurrence_id._get_last_task_id_per_recurrence_id().get(task.recurrence_id.id)
            task.is_last_recurrence = (task.id == last_task_id)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('parent_id') and not vals.get('sale_line_id'):
                parent = self.browse(vals['parent_id'])
                if parent.sale_line_id:
                    vals['sale_line_id'] = parent.sale_line_id.id
        return super().create(vals_list)

    def write(self, vals):
        res = super().write(vals)
        if 'state' in vals and vals['state'] in ['1_done']:
            for task in self:
                if task.parent_id:
                    siblings = task.parent_id.child_ids
                    if all(t.state in ['1_done'] for t in siblings):
                        task.parent_id.state = '1_done'
        return res

    def action_log_timesheet(self):
        self.ensure_one()
        view_id = self.env.ref('hr_timesheet.timesheet_view_tree_user').id
        return {
            'name': 'Timesheets',
            'type': 'ir.actions.act_window',
            'res_model': 'account.analytic.line',
            'view_mode': 'list,form',
            'views': [(view_id, 'list'), (False, 'form')],
            'target': 'new',
            'domain': [('task_id', '=', self.id)],
            'context': {
                'default_task_id': self.id,
                'default_project_id': self.project_id.id,
                'default_name': '/',
                'is_timesheet': 1,
            },
        }

    @api.model
    def _cron_create_next_recurring_tasks(self):
        """
        Cron job to create the next recurring task if the deadline of the current
        latest recurrence is STRICTLY today.
        """
        today = fields.Date.today()
        # Create start and end of today for Datetime comparison
        start_of_day = datetime.combine(today, time.min)
        end_of_day = datetime.combine(today, time.max)

        # Search for tasks that:
        # 1. Have a recurrence
        # 2. Have a deadline strictly within today's range (00:00:00 to 23:59:59)
        tasks_to_check = self.search([
            ('recurrence_id', '!=', False),
            ('date_deadline', '>=', start_of_day),
            ('date_deadline', '<=', end_of_day),
        ])

        for task in tasks_to_check:
            # Only create if it's the latest task (to avoid duplicates)
            if task.is_last_recurrence:
                self.env['project.task.recurrence']._create_next_occurrences(task)

    def action_manual_recurrence(self):
        self.ensure_one()
        if self.recurrence_id:
            self.env['project.task.recurrence']._create_next_occurrences(self)
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('The next recurring task has been created.'),
                    'type': 'success',
                    'sticky': False,
                }
            }

    @api.depends('sale_order_id.invoice_ids', 'timesheet_ids.timesheet_invoice_id')
    def _compute_invoice_ids(self):
        for task in self:
            # Only include invoices that are linked to this task's timesheets
            invoices = task.timesheet_ids.mapped('timesheet_invoice_id').filtered(lambda inv: inv.state != 'cancel')
            task.invoice_ids = invoices
            task.invoice_count = len(invoices)
            task.invoice_no = ", ".join(n for n in invoices.mapped('name') if n) if invoices else ""

    @api.depends('timesheet_ids', 'timesheet_ids.timesheet_invoice_id', 'child_ids.uninvoiced_hours')
    def _compute_uninvoiced_hours(self):
        for task in self:
            # Current task uninvoiced hours
            uninvoiced_ts = task.timesheet_ids.filtered(lambda t: t._is_not_billed())
            task.uninvoiced_hours = sum(uninvoiced_ts.mapped('unit_amount'))

            # Recursive sum for total_uninvoiced_hours
            total = task.uninvoiced_hours + sum(task.child_ids.mapped('total_uninvoiced_hours'))
            task.total_uninvoiced_hours = total

    @api.depends('child_ids.invoice_no', 'child_ids.sub_task_invoice_nos')
    def _compute_sub_task_invoice_nos(self):
        for task in self:
            # Collect invoice numbers from direct subtasks and their subtasks
            sub_invoice_nos = set()
            for subtask in task.child_ids:
                if subtask.invoice_no:
                    sub_invoice_nos.update(n.strip() for n in subtask.invoice_no.split(",") if n.strip())
                if subtask.sub_task_invoice_nos:
                    sub_invoice_nos.update(n.strip() for n in subtask.sub_task_invoice_nos.split(",") if n.strip())

            task.sub_task_invoice_nos = ", ".join(sorted(sub_invoice_nos)) if sub_invoice_nos else ""

    def action_view_invoice(self):
        self.ensure_one()
        invoices = self.invoice_ids
        action = self.env.ref('account.action_move_out_invoice_type').sudo().read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action

    def _get_all_invoices(self):
        """ Recursively get invoices from task and its subtasks """
        self.ensure_one()
        invoices = self.invoice_ids
        for child in self.child_ids:
            invoices |= child._get_all_invoices()
        return invoices

    def action_view_all_invoices(self):
        """ Open view for all invoices related to task and subtasks """
        self.ensure_one()
        invoices = self._get_all_invoices()
        action = self.env.ref('account.action_move_out_invoice_type').sudo().read()[0]
        if len(invoices) > 1:
            action['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            form_view = [(self.env.ref('account.view_move_form').id, 'form')]
            if 'views' in action:
                action['views'] = form_view + [(state, view) for state, view in action['views'] if view != 'form']
            else:
                action['views'] = form_view
            action['res_id'] = invoices.id
        else:
            action = {'type': 'ir.actions.act_window_close'}
        return action
