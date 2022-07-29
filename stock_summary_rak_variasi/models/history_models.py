from odoo import models, fields, api, _
from odoo.exceptions import UserError

class HistoryReceipts(models.Model):
    _name = 'history.receipts'

    # order_in_id = fields.Many2one('tj.summary.rak.variasi')
    picking_id = fields.Many2one('stock.picking', 'No Transfer',)
    min_date  = fields.Datetime("Date")
    partner_id = fields.Many2one('res.partner', 'Partner',)
    location_id = fields.Many2one('stock.location', 'Source Location',)
    location_dest_id = fields.Many2one('stock.location', 'Destination',)
    picking_category = fields.Many2one('makloon.picking.category', string='Picking Type',)
    product_id = fields.Many2one('product.product', string='Product',)
    grade_id = fields.Many2one('makloon.grade', string='Grade')
    lot_id = fields.Many2one('stock.production.lot', string='Lot',)
    rak_id = fields.Many2one('makloon.rak', string='Lokasi')
    variasi_id = fields.Many2one('tj.stock.variasi', string='Variasi',)
    product_uom_id = fields.Many2one('product.uom', string='Uom',)
    qty = fields.Float(string='Qty',)
    pcs = fields.Float(string='pcs',)

    # _sql = """
    #         DELETE FROM tj_summary_rak_variasi_line_history;

    #         select a.id as picking_id,a.min_date,a.partner_id,a.location_id,a.location_dest_id,d.id as picking_category,b.product_id,c.lot_id,b.rak_id,b.variasi_id,b.product_uom_id,c.qty,1 as pcs from stock_picking a , stock_pack_operation b, stock_pack_operation_lot c, makloon_picking_category d where a.picking_category=d.id and a.id=b.picking_id and b.id=c.operation_id and a.state='done'
    
    #         """

class HistoryRelease(models.Model):
    _name = 'history.release'

    # order_in_id = fields.Many2one('tj.summary.rak.variasi')
    picking_id = fields.Many2one('stock.picking', 'No Transfer',)
    min_date  = fields.Datetime("Date")
    partner_id = fields.Many2one('res.partner', 'Partner',)
    location_id = fields.Many2one('stock.location', 'Source Location',)
    location_dest_id = fields.Many2one('stock.location', 'Destination',)
    picking_category = fields.Many2one('makloon.picking.category', string='Picking Type',)
    product_id = fields.Many2one('product.product', string='Product',)
    grade_id = fields.Many2one('makloon.grade', string='Grade')
    lot_id = fields.Many2one('stock.production.lot', string='Lot',)
    rak_id = fields.Many2one('makloon.rak', string='Lokasi')
    variasi_id = fields.Many2one('tj.stock.variasi', string='Variasi',)
    product_uom_id = fields.Many2one('product.uom', string='Uom',)
    qty = fields.Float(string='Qty',)
    pcs = fields.Float(string='pcs',)

    # _sql = """ """