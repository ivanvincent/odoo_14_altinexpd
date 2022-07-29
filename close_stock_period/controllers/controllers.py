# -*- coding: utf-8 -*-
from odoo import http

# class CloseStockPeriod(http.Controller):
#     @http.route('/close_stock_period/close_stock_period/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/close_stock_period/close_stock_period/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('close_stock_period.listing', {
#             'root': '/close_stock_period/close_stock_period',
#             'objects': http.request.env['close_stock_period.close_stock_period'].search([]),
#         })

#     @http.route('/close_stock_period/close_stock_period/objects/<model("close_stock_period.close_stock_period"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('close_stock_period.object', {
#             'object': obj
#         })