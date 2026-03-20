# -*- coding: utf-8 -*-
from odoo import http, fields, _
from odoo.http import request

class AcEvaluationController(http.Controller):

    @http.route('/ac/team/accept/<int:res_id>/<string:token>', type='http', auth='public', website=True)
    def ac_team_accept(self, res_id, token, **kwargs):
        team_member = request.env['pkf.ac.team.independence'].sudo().browse(res_id)
        if not team_member.exists() or team_member.access_token != token:
            return request.render('website.404')
        
        team_member.write({
            'confirmation': 'accept',
            'date_of_confirmation': fields.Datetime.now(),
        })
        team_member.evaluation_id.message_post(body=_("Independence Accepted by %s (%s).") % (team_member.name, team_member.email))
        return request.make_response(_("Thank you %s! Your independence acceptance has been recorded.") % team_member.name, [('Content-Type', 'text/plain')])

    @http.route('/ac/team/decline/<int:res_id>/<string:token>', type='http', auth='public', website=True)
    def ac_team_decline(self, res_id, token, **kwargs):
        team_member = request.env['pkf.ac.team.independence'].sudo().browse(res_id)
        if not team_member.exists() or team_member.access_token != token:
            return request.render('website.404')
        
        team_member.write({
            'confirmation': 'decline',
            'date_of_confirmation': fields.Datetime.now(),
        })
        team_member.evaluation_id.message_post(body=_("Independence Declined by %s (%s).") % (team_member.name, team_member.email))
        return request.make_response(_("Thank you %s! Your response has been recorded.") % team_member.name, [('Content-Type', 'text/plain')])
