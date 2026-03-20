# -*- coding: utf-8 -*-

from odoo import api, models


class SignRequest(models.Model):
    _inherit = "sign.request"

    @api.model
    def create_with_creator(self, vals, creator_uid):
        """Create sign.request as a specific user for migration."""
        creator_uid = int(creator_uid) if creator_uid else False
        if not creator_uid:
            return self.create(vals).id
        record = self.sudo().with_user(creator_uid).create(vals)
        return record.id
