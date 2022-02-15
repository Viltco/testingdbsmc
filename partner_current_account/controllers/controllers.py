# -*- coding: utf-8 -*-
# from odoo import http


# class PartnerCurrentAccount(http.Controller):
#     @http.route('/partner_current_account/partner_current_account/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_current_account/partner_current_account/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_current_account.listing', {
#             'root': '/partner_current_account/partner_current_account',
#             'objects': http.request.env['partner_current_account.partner_current_account'].search([]),
#         })

#     @http.route('/partner_current_account/partner_current_account/objects/<model("partner_current_account.partner_current_account"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_current_account.object', {
#             'object': obj
#         })
