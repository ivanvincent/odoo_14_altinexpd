from odoo import api, fields, models, _

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    no_po = fields.Many2one('purchase.order', 'PO')
    no_sj = fields.Char('No SJ',)
    no_sj_result = fields.Many2one('stock.picking', 'No SJ Result')

    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse')
    is_create_po = fields.Boolean(string='Create Po ?', default=False)


    # @api.multi
    def name_get(self):
        res = super(StockPicking, self).name_get()
        data = []
        for rec in self:
            display_value = ''
            display_value += rec.name or ""
            if rec.no_sj:
                display_value += ' ['
                display_value += rec.no_sj or ""
                display_value += ']'
            data.append((rec.id, display_value))
        return data

    def action_create_purchase(self):
        purchase = self.env['purchase.order'].create({
            "partner_id": self.partner_id.id,
            "purchase_category_id": self.makloon_order_id.purchase_category_id.id,
            "order_line": [(0, 0, {
                "product_id": sm.product_id.id,
                "name": sm.product_id.name,
                "specifications": "-",
                "product_qty": sm.quantity_done,
                "price_unit": sm.product_id.standard_price
            })for sm in self.move_ids_without_package]
        })
        self.no_po = purchase.id
        self.is_create_po = True

class StockMove(models.Model):
    _inherit = 'stock.move'

    # no_sj = fields.Many2one('makloon.surat.jalan','No SJ')
    # picking_list = fields.Many2one('makloon.picking.list', 'Picking List')
    # no_sj = fields.Char('makloon.surat.jalan','No SJ')
    no_po = fields.Many2one('purchase.order','No PO')

    

    # @api.multi
    def get_packing_list(self):
        for me_id in self :
            picking_list = self.env['makloon.picking.list'].search([
                ('picking_id', '=', me_id.picking_id.id),
                ('product_id', '=', me_id.product_id.id)
            ], limit=1)
            return picking_list

class StockPackOperation(models.Model):
    _inherit = 'stock.move'

    picking_list = fields.Many2one('makloon.picking.list','Picking List')
    # no_sj = fields.Many2one('makloon.surat.jalan','No SJ')
    no_po = fields.Many2one('purchase.order', 'No PO')

    # @api.multi
    def create_picking_list(self):
        self.ensure_one()
        picking = self.env['makloon.picking.list']
        data = {
            'picking_id': self.picking_id.id,
            'product_id': self.product_id.id
        }
        picking_id = picking.create(data)
        return picking_id

    # @api.multi
    def action_picking_list(self):
        action = self.env.ref('tj_makloon_custom.action_wizard_tj_makloon_picking_list').read()[0]
        picking = self.env['makloon.picking.list'].search(
            [('picking_id', '=', self.picking_id.id), ('product_id', '=', self.product_id.id)])
        if not picking :
            picking = self.create_picking_list()
        barcode_line = self.env['makloon.barcode.line'].search([
            ('order_id.source_document','=',self.picking_id.id),
            ('product_id','=',self.product_id.id),
        ])
        if barcode_line :
            if picking.picking_list :
                picking.picking_list.unlink()
            for line in barcode_line :
                picking.picking_list.create({
                    'barcode': line.name,
                    'qty_kg': line.product_bruto,
                    'order_id': picking.id,
                })
        action['views'] = [(self.env.ref('tj_makloon_custom.view_wizard_tj_makloon_custom_picking_list').id, 'form')]
        action['res_id'] = picking.id
        return action

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    product_category_warna_id = fields.Many2one('makloon.category.warna', 'Category Warna')
    