import uuid
from odoo import fields, models, api, _
from werkzeug.urls import url_join

class PkfAcTeamIndependence(models.Model):
    _name = "pkf.ac.team.independence"
    _description = "Team Independence"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    evaluation_id = fields.Many2one("pkf.ac.evaluation", string="Evaluation", ondelete="cascade")
    name = fields.Char(string="Name", tracking=True)
    email = fields.Char(string="Email", tracking=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    is_draft = fields.Boolean(string="Is Draft", default=True, help="True if created by the wizard but not yet sent.")
    confirmation = fields.Selection(
        [
            ("pending", "Pending"),
            ("accept", "Accept"),
            ("decline", "Decline"),
        ],
        string="Confirmation",
        default="pending",
        tracking=True,
    )
    date_of_confirmation = fields.Datetime(string="Date of Confirmation", tracking=True)
    access_token = fields.Char(string="Access Token", copy=False, readonly=True)

    def _ensure_access_token(self):
        for rec in self:
            if not rec.access_token:
                rec.access_token = str(uuid.uuid4())
        return True

    def _get_base_url(self):
        return self.env['ir.config_parameter'].sudo().get_param('web.base.url')

    def action_accept_url(self):
        self.ensure_one()
        self._ensure_access_token()
        base_url = self._get_base_url()
        return url_join(base_url, "/ac/team/accept/%s/%s" % (self.id, self.access_token))

    def action_decline_url(self):
        self.ensure_one()
        self._ensure_access_token()
        base_url = self._get_base_url()
        return url_join(base_url, "/ac/team/decline/%s/%s" % (self.id, self.access_token))

    def action_view_evaluation_url(self):
        """Generate a direct URL to open the A&C evaluation form view."""
        self.ensure_one()
        base_url = self._get_base_url()
        try:
            action_id = self.env.ref('pkf_ac.action_pkf_ac_evaluation').id
        except (ValueError, AttributeError):
            return base_url
        if not self.evaluation_id:
            return base_url
        return url_join(base_url, "/odoo/action-%s/%s" % (action_id, self.evaluation_id.id))
