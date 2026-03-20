# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class AIAgent(models.Model):
    _inherit = 'ai.agent'

    visible_to_all = fields.Boolean('Visible to All Users', default=True)
    allowed_group_ids = fields.Many2many(
        'res.groups',
        'ai_agent_group_rel',
        'agent_id',
        'group_id',
        string='Allowed Groups'
    )

    def is_visible_to_user(self, user=None):
        """Check if AI agent is visible to specific user"""
        user = user or self.env.user

        # Hierarchy of visibility checks
        if self.visible_to_all:
            return True

        # Check group membership using group_ids field
        user_has_allowed_group = bool(
            self.allowed_group_ids and
            set(user.group_ids.ids) & set(self.allowed_group_ids.ids)
        )

        return user_has_allowed_group

    @api.model
    def get_visible_ai_agents(self):
        """Get AI agents visible to current user"""
        all_agents = self.search([])
        visible_agents = all_agents.filtered(lambda agent: agent.is_visible_to_user())
        return visible_agents

    def _get_or_create_ai_chat(self, channel_name=None):
        if not self.is_visible_to_user():
            raise UserError(_("You don't have access to this AI agent."))
        return super(AIAgent, self)._get_or_create_ai_chat(channel_name=channel_name)
