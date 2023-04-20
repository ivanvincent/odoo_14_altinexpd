from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    
    operation_template_id = fields.Many2one('mrp.operation.template', string='Operation Template')
    cost_ids 	= fields.One2many('mrp.bom.cost', 'bom_id', 'Variable Costs')
    product_qty = fields.Float(
        'Quantity', default=1.0,
    digits=(12,4), required=True)
    tot_biaya	= fields.Float('Variable Cost', compute='_compute_bom_cost')
    besar_waste	= fields.Float('Waste %',)
    standard_price = fields.Float('Total Price', compute='_compute_bom_cost')
    raw_cost	= fields.Float('Component Cost', compute='_compute_bom_cost')
    qty_weight	= fields.Float('Qty Weight', compute='_compute_bom_cost')
    # total_price_var_cost = fields.Float(compute='_compute_total', string='Total Price Var Cost', store=False)
    # total_unit_cost = fields.Float(compute='_compute_total', string='Total Unit Cost', store=False)
    
    @api.onchange('operation_template_id')
    def _get_operations(self, picking_ids, workcenter_engineering):
        operation_ids = []
        self.operation_ids = False
        for line in self.operation_template_id.line_ids:
            operation_ids+= [(0,0,{'name':line.sequence,'template_line_id':line.id,'workcenter_id':line.workcenter_id.id,'machine_id':line.machine_id.id})]
        # for line in workcenter_engineering.workcenter_ids:
        #     operation_ids+= [(0,0,{'name':line.sequence, 'workcenter_id':line.workcenter_id.id,})]
        self.operation_ids = operation_ids
        # Get Component
        component_ids = []
        self.bom_line_ids = False

        # for c in self.operation_template_id.line_ids.parameter_ids.mrp_operation_template_line_parameter_tool_ids:
        #     component_ids+= [(0,0,{'product_id':c.product_id.id,'product_qty':c.qty})]

        for c in self.env['stock.picking'].browse(picking_ids).move_ids_without_package:
            component_ids+= [(0,0,{'product_id':c.product_id.id,'product_qty':c.quantity_done})]

        self.bom_line_ids = component_ids

    def name_get(self):
        # if not self._context.get('production_dyeing'):
        #     return super(MrpBom, self).name_get()
        res = []
        for record in self:
            variant = record.product_id.product_template_attribute_value_ids._get_combination_name() or ''
            res.append((record.id, record.product_id.name +' | ' +variant))
        return res

    # @api.depends('cost_ids', 'flowprocess_ids')
    # def _compute_total(self):
    #     for order_doc in self:
    #         order_doc.total_price_flowprocess = sum(order_doc.flowprocess_ids.mapped('price'))
    #         order_doc.total_price_var_cost = sum(order_doc.cost_ids.mapped('amount_cost'))
    #         bom = self.env['mrp.bom'].browse(order_doc.id)
    #         company = bom.company_id or self.env.company
    #         price = 0
    #         if order_doc.product_id.id:
    #             if order_doc.product_id.uom_id:
    #                 price = order_doc.product_id.uom_id._compute_price(order_doc.product_id.with_company(company).standard_price, bom.product_uom_id) * order_doc.product_qty
    #         else:
    #             # Use the product template instead of the variant
    #             if order_doc.product_id.uom_id:
    #                 price = bom.product_tmpl_id.uom_id._compute_price(bom.product_tmpl_id.with_company(company).standard_price, bom.product_uom_id) * order_doc.product_qty
    #         order_doc.total_unit_cost = price / order_doc.product_qty

    def _compute_bom_cost(self):
        for bom in self:
            total_raw = 0.0	
            if bom.product_qty != 0:
                bom.raw_cost = sum(line.total_price for line in bom.bom_line_ids) / bom.product_qty
                bom.tot_biaya = sum(line.amount_cost for line in bom.cost_ids) / bom.product_qty
                bom.standard_price = bom.raw_cost + bom.tot_biaya
                # bom.qty_weight = (bom.product_tmpl_id.grm_greige * bom.product_tmpl_id.lbr_greige * bom.product_qty) / 1000
                bom.qty_weight = 0

class MrpRoutingWorkcenter(models.Model):
    _inherit = 'mrp.routing.workcenter'
    
    machine_id       = fields.Many2one('mrp.machine', string='Machine')
    template_line_id = fields.Many2one('mrp.operation.template.line', string='Template Line')
    parameter_ids    = fields.One2many('mrp.operation.template.line.parameter', string='Parameters',related="template_line_id.parameter_ids")

