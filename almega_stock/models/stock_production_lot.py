from odoo import fields, api, models, _
from odoo.exceptions import Warning
import odoo.addons.decimal_precision as dp

class StockProductionLot(models.Model):
    _inherit = 'stock.production.lot'

    # @api.multi
    @api.depends('quant_ids.qty','quant_ids.location_id')
    def _get_qty(self):
        print('_get_qty')
        for me_id in self :
            me_id.product_sold = sum(quant.qty for quant in me_id.quant_ids.filtered(lambda quant: quant.location_id.usage == 'customer'))
            me_id.product_residue = sum(quant.qty for quant in me_id.quant_ids.filtered(lambda quant: quant.location_id.scrap_location))
            me_id.product_saldo = sum(quant.qty for quant in me_id.quant_ids.filtered(lambda quant: quant.location_id.usage == 'internal'))

    # @api.multi
    @api.depends('quant_ids.location_id','quant_ids.location_id.usage')
    def _get_warhouse(self):
        for lot in self :
            warehouse = False
            internal_loc_ids = lot.quant_ids.mapped('location_id').filtered(lambda loc: loc.usage == 'internal')
            for loc in internal_loc_ids :
                if not warehouse :
                    warehouse = loc.get_warehouse() and loc.get_warehouse().id or False
                    if not warehouse :
                        raise Warning("Tidak ditemukan warehouse untuk lokasi %s"%loc.name_get()[0][1])
            lot.warehouse_id = warehouse

    # @api.multi
    def ProductAgeLot(self):
        cr = self.env.cr
        cr.execute("update stock_production_lot SET product_age = current_date - product_date where product_saldo > 0")

    picking_in_id = fields.Many2one('stock.picking', 'Source Document')
    purchase_id = fields.Many2one('purchase.order', 'Purchase Order')
    picking_out_id = fields.Many2one('stock.picking', 'No SJ')
    default_code = fields.Char(string='Kode', related='product_id.default_code')
    warehouse_id = fields.Many2one('stock.warehouse', 'Warehouse', compute='_get_warhouse', store=True)
    product_date = fields.Date('Date', default=fields.Datetime.now, )
    
    # CUSTOM CODE
    product_age = fields.Integer('Age', store=True , readonly=True)
    # quant_ids = fields.One2many('stock.   quant', 'lot_id', 'Quants', readonly=True)

    # ORIGINAL CODE
    # product_age = fields.Integer('Age', compute='ProductAgeLot', store=True , readonly=True)
    
    product_bruto = fields.Float('Bruto')
    product_netto = fields.Float('Netto')
    # product_sold = fields.Float('Sold', compute='_get_qty', store=True)
    # product_residue = fields.Float('Scrap', compute='_get_qty', store=True)
    # product_saldo = fields.Float('Saldo Akhir', compute='_get_qty', store=True)
    product_sold = fields.Float('Sold', store=True)
    product_residue = fields.Float('Scrap', store=True)
    product_saldo = fields.Float('Saldo Akhir', store=True)
    product_scale = fields.Float('In Scale')
    product_uom_id = fields.Many2one('uom.uom', 'Uom')
    product_merk_id = fields.Many2one('makloon.merk', 'Merk')
    product_setting_id = fields.Many2one('makloon.setting', 'Setting')
    product_gramasi_id = fields.Many2one('makloon.gramasi', 'Gramasi')
    product_corak_id = fields.Many2one('makloon.corak', 'Corak')
    product_warna_id = fields.Many2one('makloon.warna', 'Warna')
    product_resep_warna_id = fields.Many2one('makloon.resep.warna', 'Resep Warna')
    product_lot_id = fields.Many2one('makloon.lot', 'Lot No')
    state = fields.Selection([('available', 'Available'),('broken', 'Broken'), ('sold', 'Sold'),('eceran', 'Eceran'), ],
                             string="Status", default='available')
    available_for_pos = fields.Boolean(string="Can Be POS", default=True,)
    no_sj = fields.Char('NO SJ')
    opname_date = fields.Date(string='Opname Date')
    opname_qty = fields.Float(string='Opname Qty', digits=dp.get_precision('Product Unit of Measure'))
    no_urut = fields.Char(string='No Urut')
    no_lot = fields.Char(string='No Lot')
    gulungan_ke = fields.Integer(string='Gulungan Ke')
    total_gulungan = fields.Integer(string='Total Gulungan')
    lot_parent_name = fields.Char(string='Lot Parent name')
    heat_number = fields.Char(string='Heat Number')

    # @api.onchange('product_bruto')
    # def bruto_change(self):
    #     if self.product_bruto :
    #         self.product_saldo = self.product_bruto

    # @api.onchange('product_residue','product_sold','product_saldo')
    # def sold_change(self):
    #     if self.product_bruto :
    #         self.product_saldo = self.product_bruto - self.product_sold - self.product_residue

    @api.model
    def create(self, vals):
        if 'name' not in vals :
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.production.lot')
        elif not vals.get('name', False):
            vals['name'] = self.env['ir.sequence'].next_by_code('stock.production.lot')
        return super(StockProductionLot, self).create(vals)

    # @api.multi
    # def action_split(self, new_qty):
    def action_split(self):
        view_id = self.env.ref('almega_stock.view_angkring_lot_wizard')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Split Lot'),
            'res_model': 'angkring.duplicate.lot',
            'view_mode': 'form',
            'view_id': view_id.id,
            'target': 'new',
        }
    
    def open_split_barcode_wizard_form(self):
        # warehouse_id = self.env['stock.warehouse'].sudo().search([('lot_stock_id','=',self.location_id.id)],limit=1).id  if self.location_id else False
        
        return {
            'type': 'ir.actions.act_window',
            'name': 'Split Barcode',
            'res_model': 'split.barcode.wizard',
            'view_mode': 'form',
            'context': {'default_picking_in_id':self.picking_in_id.id,
                        "default_warehouse_id":1,
                        'default_lot_id':self.id,
                        "default_quantity":self.product_qty,
                        # "default_location_id":self.location_id.id,
                        "default_move_line_id":self.id,
                        "active_model":self._name},
            'target': 'new',
        }
