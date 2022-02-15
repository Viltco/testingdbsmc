# -*- coding: utf-8 -*-
# from odoo import http


# class BranchActive(http.Controller):
#     @http.route('/branch_active/branch_active/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/branch_active/branch_active/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('branch_active.listing', {
#             'root': '/branch_active/branch_active',
#             'objects': http.request.env['branch_active.branch_active'].search([]),
#         })

#     @http.route('/branch_active/branch_active/objects/<model("branch_active.branch_active"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('branch_active.object', {
#             'object': obj
#         })
