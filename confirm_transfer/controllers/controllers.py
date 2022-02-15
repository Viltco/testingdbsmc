# -*- coding: utf-8 -*-
# from odoo import http


# class ConfirmTransfer(http.Controller):
#     @http.route('/confirm_transfer/confirm_transfer/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/confirm_transfer/confirm_transfer/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('confirm_transfer.listing', {
#             'root': '/confirm_transfer/confirm_transfer',
#             'objects': http.request.env['confirm_transfer.confirm_transfer'].search([]),
#         })

#     @http.route('/confirm_transfer/confirm_transfer/objects/<model("confirm_transfer.confirm_transfer"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('confirm_transfer.object', {
#             'object': obj
#         })
