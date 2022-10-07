from collections import namedtuple, defaultdict
# from collections import defaultdict
import json
import time

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.float_utils import float_compare
# from odoo.addons.procurement.models import procurement
from odoo.exceptions import UserError


class Picking(models.Model):
    _inherit = "stock.picking"


    makloon_order_id = fields.Many2one("makloon.order", "Makloon Order")

class StockLocation(models.Model):
    _inherit = 'stock.location'

    partner_id = fields.Many2one('res.partner', string='Partner')


# class StockQuant(models.Model):
#     _inherit = "stock.quant"
#
#     def _account_entry_move(self, move):
#         print "INI BERLAKU DI MAKLOON STOCK QUANT..., UNTUK KHUSUS BARANG HASIL MAKLOON "
#
#         # if move.picking_id.makloon_order_id and move.picking_id.picking_type_id.code=='incoming':
#
#         result_ids = [x.product_id.id for x in move.picking_id.makloon_order_id.result_ids]
#         if result_ids:
#
#             if move.product_id.type != 'product' or move.product_id.valuation != 'real_time':
#                 return False
#             if any(quant.owner_id or quant.qty <= 0 for quant in self):
#                 return False
#
#             # location_from = move.location_id
#             location_to = move.location_dest_id
#             # company_from = location_from.usage == 'internal' and location_from.company_id or False
#             company_to = location_to and (location_to.usage == 'internal') and location_to.company_id or False
#             print "COMPANY TOO...., ... ", company_to
#             if move.product_id.id in result_ids:
#                 if company_to and (move.location_id.usage == 'production' and move.location_dest_id.usage =='internal'):
#                     journal_id, acc_src, acc_dest, acc_valuation = move._get_accounting_data_for_valuation()
#                     print "JOURNAL ID ...,  ", journal_id, " ACC SRC,... ", acc_src, "   ACC DEST .., ", acc_dest, "   ACC VALUATION .., ", acc_valuation
#                     print "DISINI TERLAKSANAKAH?...."
#                     if move.picking_id.makloon_order_id:
#                         print "DAN DISINI JUGA KAH?..."
#                         print "NILAI STOCK MOVE ...,  ", move.price_unit
#
#                         self.with_context(force_company=company_to.id)._create_account_move_line(move, acc_src, acc_valuation,  journal_id)
#
#         # else:
#         #     super(StockQuant, self)._account_entry_move(move)
#
#         else:
#
#             super(StockQuant, self)._account_entry_move(move)
#
#




# class StockMove(models.Model):
#     _inherit = "stock.move"
#
#
#
#









    # @api.multi
    # def product_price_update_before_done(self):
    #
    #     if self.picking_id.makloon_order_id:
    #         tmpl_dict = defaultdict(lambda: 0.0)
    #         # adapt standard price on incomming moves if the product cost_method is 'average'
    #         std_price_update = {}
    #         for move in self.filtered(lambda move: move.location_id.usage in ('supplier', 'production') and move.product_id.cost_method == 'average'):
    #             product_tot_qty_available = move.product_id.qty_available + tmpl_dict[move.product_id.id]
    #
    #             # if the incoming move is for a purchase order with foreign currency, need to call this to get the same value that the quant will use.
    #             if product_tot_qty_available <= 0:
    #                 new_std_price = move.get_price_unit()
    #             else:
    #                 # Get the standard price
    #                 amount_unit = std_price_update.get((move.company_id.id, move.product_id.id)) or move.product_id.standard_price
    #                 new_std_price = ((amount_unit * product_tot_qty_available) + (move.get_price_unit() * move.product_qty)) / (product_tot_qty_available + move.product_qty)
    #
    #             tmpl_dict[move.product_id.id] += move.product_qty
    #             # Write the standard price, as SUPERUSER_ID because a warehouse manager may not have the right to write on products
    #             move.product_id.with_context(force_company=move.company_id.id).sudo().write({'standard_price': new_std_price})
    #             std_price_update[move.company_id.id, move.product_id.id] = new_std_price
    #
    #     else:
    #         super(StockMove, self).product_price_update_before_done()

