from odoo import fields, api, models
from odoo.exceptions import Warning

class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_account_move_line(self, qty, cost, credit_account_id, debit_account_id):
        res = super(StockMove, self)._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id)
        if self.picking_type_id.code == 'outgoing' and self.location_dest_id.usage == 'customer' :
            partner_id = (self.picking_id.partner_id and self.env['res.partner']._find_accounting_partner(self.picking_id.partner_id).id) or False
            hpp_account_id = self.product_id.property_account_expense_id.id or self.product_id.categ_id.property_account_expense_categ_id.id
            persediaan_account_id = self.product_id.property_stock_account_output.id or self.product_id.categ_id.property_stock_account_output_categ_id.id
            if not hpp_account_id :
                raise Warning("Tidak ditemukan expense account di master product dan product category.")
            if not persediaan_account_id :
                raise Warning("Tidak ditemukan stock output account di master product dan product category.")
            hpp = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': self.picking_id.name,
                'partner_id': partner_id,
                'credit': 0,
                'debit': cost*qty,
                'account_id': hpp_account_id,
            }
            res.append((0, 0, hpp))
            persediaan = {
                'name': self.name,
                'product_id': self.product_id.id,
                'quantity': qty,
                'product_uom_id': self.product_id.uom_id.id,
                'ref': self.picking_id.name,
                'partner_id': partner_id,
                'credit': cost*qty,
                'debit': 0,
                'account_id': persediaan_account_id,
            }
            res.append((0, 0, persediaan))
        return res
