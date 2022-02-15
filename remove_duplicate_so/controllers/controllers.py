# -*- coding: utf-8 -*-
# from odoo import http


# class RemoveDuplicateSo(http.Controller):
#     @http.route('/remove_duplicate_so/remove_duplicate_so/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/remove_duplicate_so/remove_duplicate_so/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('remove_duplicate_so.listing', {
#             'root': '/remove_duplicate_so/remove_duplicate_so',
#             'objects': http.request.env['remove_duplicate_so.remove_duplicate_so'].search([]),
#         })

#     @http.route('/remove_duplicate_so/remove_duplicate_so/objects/<model("remove_duplicate_so.remove_duplicate_so"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('remove_duplicate_so.object', {
#             'object': obj
#         })
