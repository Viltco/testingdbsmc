# -*- coding: utf-8 -*-
# from odoo import http


# class PlastartField(http.Controller):
#     @http.route('/plastart_field/plastart_field/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/plastart_field/plastart_field/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('plastart_field.listing', {
#             'root': '/plastart_field/plastart_field',
#             'objects': http.request.env['plastart_field.plastart_field'].search([]),
#         })

#     @http.route('/plastart_field/plastart_field/objects/<model("plastart_field.plastart_field"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('plastart_field.object', {
#             'object': obj
#         })
