from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    
    type_id          = fields.Many2one('mrp.production.type', string='Type')
    request_id       = fields.Many2one('mrp.request', string='MRP Request')
    treatment_id     = fields.Many2one('treatment', string='Treatment')
    sales_id         = fields.Many2one('sale.order', string='Sale Order')
    shape            = fields.Char(string='Shape')
    # html_color       = fields.Char(related='product_id.html_color', string='Color',store=True,)
    satuan_id        = fields.Many2one(related='product_id.satuan_id', string='Satuan Produksi')
    mrp_qty_produksi = fields.Float(string='Quantity Produksi')
    splitted_wo      = fields.Boolean(string='Splitted Workorder ?')

    ukuran_tip       = fields.Char(string='Ukuran Tip/LBG')
    bentuk_tip       = fields.Char(string='Bentuk Tip')
    penandaan_tip    = fields.Char(string='Penandaan Tip')
    bahan            = fields.Char(string='Bahan')
    ukuran           = fields.Char(string='Ukuran')
    kode_bahan       = fields.Char(string='Kode Bahan')
    is_highrisk      = fields.Boolean(string='Is Highrisk?', default=False)
    
    
    def action_split_workorder(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Split Workorder',
            'res_model': 'mrp.workorder.split.wizard',
            'context':{'default_production_id':self.id},
            'view_mode': 'form',
            'target': 'new',
        }
        
        
    def action_cancel_split(self):
        self.splitted_wo  = False
        for line in self.workorder_ids:
            for workorder in line.workorder_ids:
                workorder.unlink()
        
       
    
    
    @api.onchange('type_id')
    def get_picking_type_id(self):
        if self.state == 'draft':
            self.picking_type_id = self.type_id.picking_type_id.id
            self.location_src_id = self.type_id.picking_type_id.default_location_src_id.id
            self.location_dest_id = self.type_id.picking_type_id.default_location_dest_id.id
   
    @api.model
    def create(self,vals):
        
        if not vals.get('name') and vals.get('type_id'):
            type_id = self.env['mrp.production.type'].browse(vals.get('type_id'))
            vals['name'] = type_id.sequence_id.next_by_id()
        
        res = super(MrpProduction, self).create(vals)
        return res

    
    def _create_workorder(self):
        for production in self:
            if not production.bom_id:
                continue
            workorders_values = []

            product_qty = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id)
            exploded_boms, dummy = production.bom_id.explode(production.product_id, product_qty / production.bom_id.product_qty, picking_type=production.bom_id.picking_type_id)

            for bom, bom_data in exploded_boms:
                # If the operations of the parent BoM and phantom BoM are the same, don't recreate work orders.
                if not (bom.operation_ids and (not bom_data['parent_line'] or bom_data['parent_line'].bom_id.operation_ids != bom.operation_ids)):
                    continue
                for operation in bom.operation_ids:
                    workorders_values += [{
                        'name': operation.name,
                        'production_id': production.id,
                        'workcenter_id': operation.workcenter_id.id,
                        'product_uom_id': production.product_uom_id.id,
                        'operation_id': operation.id,
                        'state': 'pending',
                        'consumption': production.consumption,
                        'machine_id': operation.machine_id.id,
                    }]
            production.workorder_ids = [(5, 0)] + [(0, 0, value) for value in workorders_values]
            for workorder in production.workorder_ids:
                workorder.duration_expected = workorder._get_duration_expected()

    def action_set_highrisk(self):
        ctx = self.env.context
        for mrp in self.env['mrp.production'].browse(ctx.get('active_ids', [])):
            mrp.write({'is_highrisk': True})

    def action_set_unhighrisk(self):
        ctx = self.env.context
        for mrp in self.env['mrp.production'].browse(ctx.get('active_ids', [])):
            mrp.write({'is_highrisk': False})
    
    # def button_mark_done(self):
    #     print('button_mark_done',self.product_qty)
    #     a = self.product_qty
    #     res = super(MrpProduction, self).button_mark_done()
    #     self.product_qty = a
    #     return res