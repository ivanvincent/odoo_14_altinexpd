from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_log = logging.getLogger(__name__)

class MrpBom(models.Model):
    _inherit = 'mrp.bom'

    name = fields.Char(string='Name')
    labdip_id = fields.Many2one('labdip', string='Labdip', copy=False,
    #  domain="[('state', '=', 'done'), ('product_id', '=', product_tmpl_id)]"
     )
    mrp_first_compenent_ids = fields.One2many('mrp.first.component', 'bom_id', string='Components First')
    state = fields.Selection([("draft","Draft"),("confirm","Confirm")], string='State', default="draft")
    cost_ids 	= fields.One2many('mrp.bom.cost', 'bom_id', 'Variable Costs')
    product_qty = fields.Float(
        'Quantity', default=1.0,
    digits=(12,4), required=True)
    tot_biaya	= fields.Float('Variable Cost', compute='_compute_bom_cost')
    besar_waste	= fields.Float('Waste %',)
    standard_price = fields.Float('Total Price', compute='_compute_bom_cost')
    raw_cost	= fields.Float('Component Cost', compute='_compute_bom_cost')
    qty_weight	= fields.Float('Qty Weight', compute='_compute_bom_cost')

    flowprocess_id = fields.Many2one('master.flowprocess', string='Flowprocess')
    flowprocess_ids = fields.One2many('mrp.bom.flowprocess', 'bom_id', string='Flowprocess')
    total_price_flowprocess = fields.Float(compute='_compute_total', string='Total Price Flowprocess', store=False)
    total_price_var_cost = fields.Float(compute='_compute_total', string='Total Price Var Cost', store=False)
    total_unit_cost = fields.Float(compute='_compute_total', string='Total Unit Cost', store=False)
    td_id = fields.Many2one('test.development', string='TD', 
    # domain="[('product_id', '=', product_tmpl_id)]"
    )
    material_td_ids = fields.One2many('mrp.material.td', 'bom_id', string='Material TD')
    color_final_id = fields.Many2one('labdip.color.final', string='Color Final',domain="[('labdip_id', '=', labdip_id)]")
    # compute="_get_color_final"
    
    
    # def _get_color_final(self):
    #     for bom in self:
    #         final = self.env['labdip.color.final'].sudo().search([('labdip_id','=',bom.labdip_id.id),('color_id','=',bom.product_id.color_id.id)],limit = 1)
    #         if final:
    #             bom.color_final_id = final.id
    #         else:
    #             bom.color_final_id = False
        
    
    def name_get(self):
        if not self._context.get('production_dyeing'):
            return super(MrpBom, self).name_get()
        res = []
        for record in self:
            variant = record.product_id.product_template_attribute_value_ids._get_combination_name()
            res.append((record.id, record.product_id.name +' | ' +variant))
        return res

    
    @api.depends('cost_ids', 'flowprocess_ids')
    def _compute_total(self):
        for order_doc in self:
            order_doc.total_price_flowprocess = sum(order_doc.flowprocess_ids.mapped('price'))
            order_doc.total_price_var_cost = sum(order_doc.cost_ids.mapped('amount_cost'))
            bom = self.env['mrp.bom'].browse(order_doc.id)
            company = bom.company_id or self.env.company
            price = 0
            if order_doc.product_id.id:
                if order_doc.product_id.uom_id:
                    price = order_doc.product_id.uom_id._compute_price(order_doc.product_id.with_company(company).standard_price, bom.product_uom_id) * order_doc.product_qty
            else:
                # Use the product template instead of the variant
                if order_doc.product_id.uom_id:
                    price = bom.product_tmpl_id.uom_id._compute_price(bom.product_tmpl_id.with_company(company).standard_price, bom.product_uom_id) * order_doc.product_qty
            order_doc.total_unit_cost = price / order_doc.product_qty
            
    @api.model
    def create(self, val):
        seq = self.env['ir.sequence'].next_by_code('mrp.bom')
        val['name'] = seq
        res = super(MrpBom, self).create(val)
        return res

    def action_confirm(self):
        for bom in self:
            data = []
            if not bom.bom_line_ids:
                for td_material in bom.material_td_ids:
                    data.append((0, 0, {
                        'product_id' : td_material.product_id.id,
                        'product_qty' : td_material.quantity,
                        # 'product_qty' : td_material.quantity_finish,
                        'product_uom_id' : td_material.product_uom_id.id,
                        'location_id': td_material.location_id.id,
                        'kategori_id': td_material.workcenter_id.id,
                        'type': td_material.type
                    }))
                for first_comp in bom.mrp_first_compenent_ids:
                    _log.warning('='*40)
                    _log.warning('bom confirm')
                    _log.warning(first_comp.product_id.name)
                    _log.warning(first_comp.quantity_finish)
                    _log.warning('='*40)
                    data.append((0, 0, {
                        'product_id' : first_comp.product_id.id,
                        'product_qty' : first_comp.quantity_finish ,
                        # 'product_qty' : first_comp.quantity_finish if  first_comp.product_id.categ_id.name != 'GREY' else first_comp.quantity ,
                        'product_uom_id' : first_comp.product_uom_id.id,
                        'location_id': first_comp.location_id.id,
                        'kategori_obat': first_comp.kategori_obat
                    }))
                    
            
            bom.write({'bom_line_ids' : data, 'state' : 'confirm'})
    
    def action_set_to_draft(self):
        self.state = 'draft'
        self.material_td_ids = False
        self.mrp_first_compenent_ids = False
        self.bom_line_ids = False

    def _compute_bom_cost(self):
        for bom in self:
            total_raw = 0.0	
            if bom.product_qty != 0:
                bom.raw_cost = sum(line.total_price for line in bom.bom_line_ids) / bom.product_qty
                bom.tot_biaya = sum(line.amount_cost for line in bom.cost_ids) / bom.product_qty
                bom.standard_price = bom.raw_cost + bom.tot_biaya
                bom.qty_weight = (bom.product_tmpl_id.grm_greige * bom.product_tmpl_id.lbr_greige * bom.product_qty) / 1000
    
    def get_flowprocess(self):
        for rec in self:
            if rec.flowprocess_id:
                if rec.operation_ids:
                    rec.operation_ids = False
                data = []
                for a in rec.flowprocess_id.flowprocess_line_ids:
                    parameter_ids = [(0, 0, {'no_urut' : b.no_urut, 'parameter_id' : b.parameter_id.id, 'plan' : b.qty_plan, 'actual' : b.qty_actual, 'uom_id' : b.uom_id.id}) for b in a.parameter_ids]
                    chemical_ids = [(0, 0, {'no_urut' : c.no_urut, 'product_id' : c.product_id.id, 'quantity' : c.quantity, 'uom_id' : c.uom_id.id}) for c in a.chemical_ids]
                    data.append((0, 0, {
                        'workcenter_id' : a.workcenter_id.id,
                        'name': a.no_urut,
                        'mesin_id' : a.mesin_id.id,
                        'routing_parameter_ids': parameter_ids,
                        # 'process_type_id' :a.process_type_id.id,
                        # 'chemical_ids': chemical_ids,
                    }))
                rec.operation_ids = data
            else:
                rec.operation_ids = False

    def action_get_material_lab(self,location_id = None, prod = None):
        labdip_id = self.labdip_id
        # prod = {"qty_kg_greige":500}
        data = []       
        if labdip_id:
            # self.mrp_first_compenent_ids = False
            
            for obat in self.color_final_id.labdip_resep_warna_ids:
                prod_qty = (obat.conc * prod.get('qty_kg_greige') * 10 ) / 1000 if prod is not None else obat.conc
                _log.warning('='*40)
                _log.warning(prod_qty)
                _log.warning('='*40)
                data.append((0, 0, {
                    'product_id': obat.product_id.id,
                    'product_uom_id': obat.product_id.uom_id.id,
                    'quantity': obat.conc,
                    'quantity_finish': prod_qty,
                    # 'quantity_finish': obat.conc,
                    'location_id': labdip_id.location_id.id if location_id is None else location_id,
                    'kategori_obat': obat.kategori,
                    'kategori_id': self.env['mrp.workcenter'].search([('name', '=', 'DYEING/CELUP')]).id,
                    'type': obat.type,
                }))
        else:
            raise UserError('Tidak ada nomor labdip')
        self.mrp_first_compenent_ids = data

    def action_get_material_td(self,location_id = None,volume_air = None):
        td_id = self.td_id
        greige_id = td_id.product_id.id
        qty_greige = td_id.quantity
        uom_id = td_id.uom_id.id,
        location_greige = td_id.location_greige_id.id
        location_chemical = td_id.production_type.component_chemical_location.id
        data = []
        if td_id:
            self.material_td_ids = False
            self.operation_ids = False
            operation = []
            for td in td_id.final_ids:
                for chem in td.chemical_ids:
                    data.append((0, 0, {
                        'product_id': chem.product_id.id,
                        'product_uom_id': chem.product_id.uom_id.id,
                        'quantity': chem.quantity,
                        'location_id': location_chemical if location_id is None else location_id,
                        'workcenter_id': td.workcenter_id.id,                        
                        'type': chem.type,
                    }))
                parameter_ids = [(0, 0, {'no_urut' : b.no_urut, 'parameter_id' : b.parameter_id.id, 'plan' : b.plan,
                                'actual' : b.actual,'uom_id' : b.uom_id.id}) for b in td.parameter_ids]
                operation.append((0, 0, {
                    'workcenter_id' : td.workcenter_id.id,
                    'name': td.no_urut,
                    'mesin_id' : td.mesin_id.id,
                    'program_id' : td.program_id.id,
                    'routing_paramter_ids': parameter_ids,
                }))
            self.material_td_ids = data
            self.operation_ids = operation
        else:
            raise UserError('Tidak ada nomor TD')