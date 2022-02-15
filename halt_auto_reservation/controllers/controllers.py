# -*- coding: utf-8 -*-
# from odoo import http


# class ForecastedReservation(http.Controller):
#     @http.route('/forecasted_reservation/forecasted_reservation/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/forecasted_reservation/forecasted_reservation/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('forecasted_reservation.listing', {
#             'root': '/forecasted_reservation/forecasted_reservation',
#             'objects': http.request.env['forecasted_reservation.forecasted_reservation'].search([]),
#         })

#     @http.route('/forecasted_reservation/forecasted_reservation/objects/<model("forecasted_reservation.forecasted_reservation"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('forecasted_reservation.object', {
#             'object': obj
#         })
