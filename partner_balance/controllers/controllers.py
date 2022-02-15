# -*- coding: utf-8 -*-
# from odoo import http


# class PartnerBalance(http.Controller):
#     @http.route('/partner_balance/partner_balance/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/partner_balance/partner_balance/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('partner_balance.listing', {
#             'root': '/partner_balance/partner_balance',
#             'objects': http.request.env['partner_balance.partner_balance'].search([]),
#         })

#     @http.route('/partner_balance/partner_balance/objects/<model("partner_balance.partner_balance"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('partner_balance.object', {
#             'object': obj
#         })
