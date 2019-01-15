# -*- coding: utf-8 -*-
from odoo import http

# class Insurance1(http.Controller):
#     @http.route('/insurance1/insurance1/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/insurance1/insurance1/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('insurance1.listing', {
#             'root': '/insurance1/insurance1',
#             'objects': http.request.env['insurance1.insurance1'].search([]),
#         })

#     @http.route('/insurance1/insurance1/objects/<model("insurance1.insurance1"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('insurance1.object', {
#             'object': obj
#         })