# -*- coding: utf-8 -*-
# from odoo import http


# class LocationConstraint(http.Controller):
#     @http.route('/location_constraint/location_constraint/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/location_constraint/location_constraint/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('location_constraint.listing', {
#             'root': '/location_constraint/location_constraint',
#             'objects': http.request.env['location_constraint.location_constraint'].search([]),
#         })

#     @http.route('/location_constraint/location_constraint/objects/<model("location_constraint.location_constraint"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('location_constraint.object', {
#             'object': obj
#         })
