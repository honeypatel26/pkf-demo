# -*- coding: utf-8 -*-

from odoo import models, api, _
from odoo.exceptions import AccessError


class DiscussChannel(models.Model):
    _inherit = 'discuss.channel'

    @api.model
    def chat_with_ai_agent(self, ai_agent_id, channel_title=None):
        ai_agent = self.env['ai.agent'].browse(ai_agent_id)
        if not ai_agent:
            raise AccessError(_("AI not reachable, AI Agent not found."))

        # ✅ Access check
        if not ai_agent.is_visible_to_user():
            raise AccessError(_("You don't have access to this AI agent."))

        return super(DiscussChannel, self).chat_with_ai_agent(ai_agent_id, channel_title=channel_title)

    @api.model
    def _init_messaging(self):
        """Override to filter AI agents based on user access"""
        result = super(DiscussChannel, self)._init_messaging()

        # Filter AI agents based on visibility in the store initialization
        if 'ai_agents' in result:
            visible_agents = self.env['ai.agent'].get_visible_ai_agents()
            result['ai_agents'] = [agent for agent in result['ai_agents'] if agent['id'] in visible_agents.ids]

        return result
