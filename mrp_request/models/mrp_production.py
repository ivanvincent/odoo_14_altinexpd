from email.policy import default
from odoo import models, fields, api, _,SUPERUSER_ID
from odoo.exceptions import UserError
from datetime import datetime

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    
    type_id          = fields.Many2one('mrp.production.type', string='Type')
    request_id       = fields.Many2one('mrp.request', string='MRP Request')
    treatment_id     = fields.Many2one('treatment', string='Heat Treatment')
    # treatment_id     = fields.Many2one(string='Heat Treatment')
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
    picking_finished_id      = fields.Many2one('stock.picking', string='Picking Finished')
    picking_request_ids      = fields.Many2many('stock.picking', string='Picking Request',compute="_compute_picking_request")
    picking_request_count    = fields.Integer( string='Picking Request Amount',compute="_compute_picking_request")
    wo_altinex          = fields.Char(string='Wo Altinex')
    due_date_produksi   = fields.Date(related='request_id.due_date_produksi' , string='Due Date Produksi')
    no_sample           = fields.Char(related='request_id.no_sample', string='No Sample')
    note_so             = fields.Char(related='request_id.note_so', string='Note')
    kd_bahan            = fields.Char('Kode Bahan')
    lapisan             = fields.Char('Surface Finish')
    partner_id          = fields.Many2one('res.partner', string='Customer', )
    process_terkini     = fields.Many2one('mrp.workcenter', string='Process Terkini')
    parameter_terkini   = fields.Many2one('mrp.parameter', string='Parameter Terkini')
    option_vip      = fields.Selection([("VIP","VIP"),("HIGH RISK","HIGH RISK"), ("BIASA", "BIASA"), ("MAKLOON", "MAKLOON")], string='HighRisk / VIP', ondelete='cascade', 
    related='request_id.option_vip', 
    store=True,)
    billing_address  = fields.Char(string='Billing Address')
    shipping_address = fields.Many2one('res.partner', string='Shipping Address', required=True)
    ref_so_id        = fields.Many2one('sale.order', string='Ref SO')
    dqups_id         = fields.Many2one('quotation.request.form', string='D-QUPS')
    
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
   
    # @api.model
    # def create(self,vals):
        
    #     if not vals.get('name') and vals.get('type_id'):
    #         type_id = self.env['mrp.production.type'].browse(vals.get('type_id'))
    #         product_id = self.env['product.product'].browse(vals.get('product_id'))
    #         years = datetime.now().strftime('%y')
    #         shape = str(product_id.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.name == 'SHAPE').name)[0]
    #         no_urut_mor = str(self.env['mrp.request'].browse(vals.get('request_id')).name).split("/")[3]
    #         running_number = type_id.sequence_id.next_by_id()
    #         vals['name'] = '%s%s%s%s' % (years, shape, no_urut_mor, running_number)
        
    #     res = super(MrpProduction, self).create(vals)
    #     return res

    
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

                list_parameter = []
                for l in production.bom_id.operation_template_id.line_ids:
                    for p in l.parameter_ids:
                        list_parameter.append((0, 0, 
                            {'sequence': p.sequence, 'parameter_id': p.parameter_id.id, 'factor': p.factor, 'machine_id': p.machine_id.id }
                        ))

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
                        'parameter_ids': list_parameter

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
        prod_qty = self.product_qty
        res = super(MrpProduction, self).button_mark_done()
        # for mv in self.move_finished_ids.filtered(lambda x: x.state != 'cancel' and x.product_id.id == self.product_id.id):
        #     mv.quantity_done = self.product_qty
        self.product_qty = prod_qty
        self.dqups_id.state == 'sj_upload'
        # self.ref_so_id.action_confirm()
        
        
        # if res is True and self.type_id:
            # self.picking_finished_id = self.create_picking_finished()
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

    # def _read(self, fields):
    #     # untuk kebutuhan view gantt planning production
    #     res = super()._read(fields)
    #     if self.env.context.get('display_product_and_color') and 'mesin_id' in self.env.context.get('group_by', []):
    #         name_field = self._fields['name']
    #         for record in self.with_user(SUPERUSER_ID):
    #             # variant = record.product_id.product_template_attribute_value_ids._get_combination_name()
    #             self.env.cache.set(record, name_field,record.name +' ' + record.product_id.name + ' ' + ' ' + record.sale_id.name + record.partner_id.name + ' ' + record.color_id.name)
    #     return res