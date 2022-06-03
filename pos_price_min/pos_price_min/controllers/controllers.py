# -*- coding: utf-8 -*-
# from odoo import http


# class PosPriceMin(http.Controller):
#     @http.route('/pos_price_min/pos_price_min/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/pos_price_min/pos_price_min/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('pos_price_min.listing', {
#             'root': '/pos_price_min/pos_price_min',
#             'objects': http.request.env['pos_price_min.pos_price_min'].search([]),
#         })

#     @http.route('/pos_price_min/pos_price_min/objects/<model("pos_price_min.pos_price_min"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('pos_price_min.object', {
#             'object': obj
#         })
