from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

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
    picking_finished_id = fields.Many2one('stock.picking', string='Picking Finished')
    picking_request_ids      = fields.Many2many('stock.picking', string='Picking Request',compute="_compute_picking_request")
    picking_request_count    = fields.Integer( string='Picking Request Amount',compute="_compute_picking_request")
    wo_altinex = fields.Char(string='Wo Altinex')
    
    
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


    def create_picking_finished(self):
        picking_finished_id = self.env['stock.picking'].sudo().create({
            'picking_type_id': self.type_id.picking_type_finished_id.id,
            'date': fields.Date.today(),
            'scheduled_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'production_id':self.id,
            'origin':self.name,
            "location_id":self.picking_type_id.default_location_dest_id.id,
            "location_dest_id":self.type_id.picking_type_finished_id.default_location_dest_id.id,
            'immediate_transfer': False,
            'move_line_nosuggest_ids': [(0,0,{
                    'product_id': self.product_id.id,
                    # 'lot_id': self.lot_producing_id.id,
                    # 'lot_name': self.lot_producing_id.name,
                    'product_uom_id': self.product_id.uom_id.id,
                    "location_id":self.picking_type_id.default_location_dest_id.id,
                    "location_dest_id":self.type_id.picking_type_finished_id.default_location_dest_id.id,
                    
                    # 'qty_done': self.qty_producing,
                    'qty_done': self.product_qty,
                    'company_id':self.env.company.id,
                })],
            'move_lines': [(0,0,{
                'name': self.product_id.name,
                'picking_type_id': self.type_id.picking_type_finished_id.id,
                'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'product_id': self.product_id.id,
                "location_id":self.picking_type_id.default_location_src_id.id,
                "location_dest_id":self.type_id.picking_type_finished_id.default_location_dest_id.id,
                'product_uom': self.product_id.uom_id.id,
                'product_uom_qty': self.product_qty,
                # 'product_uom_qty': self.qty_producing,
                'company_id': self.env.company.id,
                })],
            
        })
        
        # picking_finished_id.action_confirm()
        # picking_finished_id.button_validate()
        
        return picking_finished_id
    
    # def button_mark_done(self):
    #     print('button_mark_done',self.product_qty)
    #     a = self.product_qty
    #     res = super(MrpProduction, self).button_mark_done()
    #     self.product_qty = a
    #     return res

    def button_mark_done(self):
    #     if self.type_id.name == 'DYEING':
    #         ## UPDATE BOM
    #         self.bom_id.bom_line_ids = False
    #         self.bom_id.write({
    #             'bom_line_ids': [(0, 0, {
    #                 'product_id' : b.product_id.id,
    #                 'product_qty' : b.product_uom_qty,
    #                 'product_uom_id' : b.product_id.uom_id.id,
    #             }) for b in self.move_raw_ids]
    #         })
        res = super(MrpProduction, self).button_mark_done()
        
        
        if res is True and self.type_id:
            self.picking_finished_id = self.create_picking_finished()
            # self.picking_finished_id.action_confirm()
            # self.picking_finished_id.button_validate()
        return res
    
    def action_view_inspect(self):
        # _logger.warning('='*40)
        return {
            'res_model': 'produksi.inspect',
            'type': 'ir.actions.act_window',
            'name': _("Inspect Finish Goods"),
            'domain': [('production_id', '=', self.id)],
            'view_mode': 'tree,form',
        }

    def action_view_request_picking(self):
        result = self.env["ir.actions.actions"]._for_xml_id('stock.action_picking_tree_all')
        pick_ids = self.mapped('picking_request_ids')
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = pick_ids.id
        return result
    
    # @api.depends('mrp_request_id')
    def _compute_picking_request(self):
        for production in self:
            picking_ids = self.env['stock.picking'].search([('production_id','=',production.id)])
            # inspect_ids = self.env['produksi.inspect'].search([('production_id','=',production.id)])
            production.picking_request_count = len(picking_ids)
            production.picking_request_ids = [(4,picking.id) for picking in picking_ids] if picking_ids else False
            # production.inspect_ids         = [(4,inspect.id) for inspect in inspect_ids] if inspect_ids else False
            # production.inspected_qty         = sum(inspect_ids.mapped('panjang_jadi')) if inspect_ids else False