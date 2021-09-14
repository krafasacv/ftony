# -*- coding: utf-8 -*-
# from odoo import http


# class Ftony(http.Controller):
#     @http.route('/ftony/ftony/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ftony/ftony/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ftony.listing', {
#             'root': '/ftony/ftony',
#             'objects': http.request.env['ftony.ftony'].search([]),
#         })

#     @http.route('/ftony/ftony/objects/<model("ftony.ftony"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ftony.object', {
#             'object': obj
#         })
