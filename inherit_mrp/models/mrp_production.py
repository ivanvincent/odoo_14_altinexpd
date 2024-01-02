from itertools import product
from multiprocessing.dummy import active_children
from operator import length_hint
from odoo import models, fields, api, _ ,SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.tools import float_compare
import logging
from datetime import timedelta,time,datetime
import math
_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    
    @api.depends('product_id','workorder_ids','workorder_ids.state')
    def _work_in_progress(self):
        for production in self:
            if production.workorder_ids and production.type_id.id == 2 and production.state == 'progress' or production.state == 'to_close':
                workcenter_on_progress = production.workorder_ids.filtered(lambda x:x.state == 'progress').mapped('workcenter_id')
                workcenter_finished    = production.workorder_ids.filtered(lambda x:x.state == 'done').mapped('workcenter_id')
                workorder = production.workorder_ids.filtered(lambda x:x.state == 'progress')
                
                if len(workcenter_on_progress) >= 1:
                    production.workcenter_on_progress = workcenter_on_progress[0].id
                    production.workorder_id = workorder.id
                elif len(workcenter_on_progress) == 0  and len(workcenter_finished) > 1:
                    production.workcenter_on_progress = workcenter_finished[len(workcenter_finished) - 1].id
                    production.workorder_id = workorder.id
                elif len(workcenter_on_progress) == 0  and len(workcenter_finished) == 0:
                    production.workcenter_on_progress = False
                    production.workorder_id = workorder.id
                
            else:
                production.workcenter_on_progress = False
                
        
    @api.depends('product_id','workorder_ids','workorder_ids.qc_pass')
    def _get_qc_pass(self):
        for production in self:
            if production.workorder_ids and production.type_id.id == 2 and production.state == 'progress' or production.state == 'to_close':
                workcenter_finished    = production.workorder_ids.filtered(lambda x:x.state == 'done').mapped('workcenter_id')
                wo_qc_on_finished      = production.workorder_ids.filtered(lambda x:x.state == 'done').mapped('qc_pass')
                if len(workcenter_finished) >= 1:
                    qc_passed =  wo_qc_on_finished[len(wo_qc_on_finished) - 1]
                    production.qc_pass = qc_passed
                        
                elif len(workcenter_finished) == 0:
                    production.qc_pass = ''
                    
                
            else:
                production.workcenter_on_progress = False
                production.qc_pass = ''
        
        
        
    #order
    sale_id                    = fields.Many2one('sale.order', string='Sale')
    partner_id                 = fields.Many2one( related="sale_id.partner_id", string='Customer')
    sale_line_id               = fields.Many2one('sale.order.line', string='sale Order Line')
    td_id                      = fields.Many2one('test.development', related='bom_id.td_id', string='TD')
    # process_type               = fields.Many2one('master.opc',string='Process Type')
    process_category_id        = fields.Many2one('process.chemical.type',string='Process Category')
    labdip_id                  = fields.Many2one('labdip', related='bom_id.labdip_id', string='Labdip')
    chemical_process_type_id   = fields.Many2one( related='labdip_id.chemical_process_type_id', string='Process Type', store=True,)
    qc_pass                    = fields.Char(string='QC Pass' ,compute="_get_qc_pass",store=True)
    remaining_qty              = fields.Float(related='sale_line_id.qty_remaining', string='Remaining Quantity')
    handling                   = fields.Selection(string='Handling',related='sale_id.handling')
    handling_id                = fields.Many2one('master.handling', string='Master Handling', related='sale_id.handling_id')
    jumlah_order               = fields.Integer(string='Jumlah Order')
    sale_type                  = fields.Selection(related="sale_id.sale_type", string='Sale type')
    process_id                 = fields.Many2one('master.proses', string='Process Terkini')
    mesin_id                   = fields.Many2one('mrp.machine', string='Mesin')
    volume_air                 = fields.Float(string="Volume Air",related="mesin_id.volume_air")
    max_batch                  = fields.Integer(related='mesin_id.max_batch', string='Max Batch Machine')
    workcenter_on_progress     = fields.Many2one('mrp.workcenter',compute="_work_in_progress", string='On Progress',store=True,)
    workorder_id               = fields.Many2one('mrp.workorder',compute="_work_in_progress", string='Workorder',store=True,)
    html_color                 = fields.Char(string='Color Visualitation',related="bom_id.color_final_id.html_color")
    design_id                  = fields.Many2one( related='product_id.design_id', string='Design')
    program_ids                = fields.Many2many(comodel_name='mrp.program', string='Program')
    amount_duration            = fields.Float(compute='_compute_duration', string='Duration Expected', store=False)
    planned_hours              = fields.Float(compute='_compute_duration', string='Scheduled Hours', store=False)
    lot_ids_count              = fields.Float(compute='_compute_lot_ids', string='Total', store=False)
    is_request_extra_chemical  = fields.Boolean(string='Is Request extra Chemical ?')    
    is_request_extra_component = fields.Boolean(string='Is Request extra COmponent ?')    
    labdip_extra_ids           = fields.Many2many(comodel_name='labdip.extra', string='Extra Chemical')
    labdip_extra_count         = fields.Integer(string='Labdip Extra Count',compute="_get_extra_labdip")
    no_urut_labdip_final       = fields.Char(string='No Urut Labdip final')
    color_id                   = fields.Many2one(related='product_id.color_id', string='Color', store=True,)
    labdip_warna_obj           = fields.Many2one('labdip.warna', string='Labdip Warna',compute='get_labdip_warna',)
    labdip_warna_id            = fields.Many2one('labdip.warna', string='Labdip Warna', related='labdip_warna_obj', store=True,)
    is_dyeing_failed           = fields.Boolean(string='Is Dyeing Failed ?',compute="_compute_dyeing_failed",store=True,)
    returned_finished_ids      = fields.Many2many('mrp.production.return', string='Returned Production')
    picking_finished_id        = fields.Many2one('stock.picking', string='Picking Finished')
    state                      = fields.Selection( selection_add=[("return", "Return")],string='State')
    
    
    
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
                    'lot_id': self.lot_producing_id.id,
                    'lot_name': self.lot_producing_id.name,
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
    
    
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        
        
        # if res is True and not self.production_origin_id:
        #     self.picking_finished_id = self.create_picking_finished()
        #     self.picking_finished_id.action_confirm()
        #     self.picking_finished_id.button_validate()
            
        
        
        return res
        
    
    @api.depends('workorder_ids','workorder_ids.qc_pass')
    def _compute_dyeing_failed(self):
        for rec in self:
            rec.is_dyeing_failed = len(self.workorder_ids.filtered(lambda x :x.workcenter_id.name == "DYEING" and x.qc_pass == 'fail')) >= 1
    
    @api.depends('color_id', 'labdip_id')
    def get_labdip_warna(self):
        for rec in self:
            labdip_warna_obj = self.env['labdip.warna'].search([('labdip_id','=',rec.labdip_id.id),('color_id','=',rec.color_id.id)], limit=1)
            rec.labdip_warna_obj = labdip_warna_obj.id
    
    
    def action_view_chemical_extra(self):
        _logger.warning('='*40)
        action = self.env.ref('inherit_mrp.open_labdip_extra_action').read()[0]
        action['domain'] = [('production_id', '=', self.id)]
        action['context'] = {}
        return action
         
         
    def _get_extra_labdip(self):
        for production in self:
            production.labdip_extra_count = len(production.labdip_extra_ids)
    
    
    def load_opc(self):
        if self.state == 'draft':
            opc_ids = []
            for move in self.move_raw_ids.filtered(lambda x: x.type == 'opc'):
                move._action_cancel()
                move.action_back_to_draft()
                move.unlink()
                
            for auxiliaries in self.process_type.line_ids:
                opc_ids += [(0, 0, {
                        # 'kategori': 'aux',
                        "name":auxiliaries.product_id.name,
                        'product_id': auxiliaries.product_id.id,
                        'chemical_conc': auxiliaries.qty,
                        'product_uom_qty': auxiliaries.qty,
                        "product_uom":auxiliaries.product_id.uom_id.id,
                        "location_id":self.location_src_id.id,
                        "location_dest_id":15,
                        'type': 'opc'
                    })]
                
            self.write({
                "move_raw_ids": opc_ids
            })
    
    def action_requst_extra_chemical(self):
        color_final = self.env['labdip.color.final'].sudo().search([('labdip_id','=',self.labdip_id.id),('color_id','=',self.product_id.color_id.id)],limit=1)
        color_final.sudo().write({"is_failed":True})
        color_final.sudo().write({"production_id":self.id})
        self.is_request_extra_chemical = True
        title = _("Warning")
        message = _("Request Extra Chemical Has been sent!!")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'sticky': True,
                'type': 'success',
            }
        }
        
        
    
    
    def action_confirm(self):
        res = super(MrpProduction, self).action_confirm()
        for production in self:
            if not production.bom_id.labdip_id and production.type_id.name == 'DYEING':
                raise UserError('Labdip cannot be empty !!!')
            if not production.bom_id.td_id and production.type_id.name == 'DYEING':
                raise UserError('TD cannont be empty  !!!')
                
        return res
        
    
    @api.onchange('program_ids')
    def onchange_program(self):
        dt = timedelta(minutes=self.amount_duration)
        self.write({"date_planned_finished": self.date_planned_start + dt})
    
    
    @api.depends('move_finished_ids')
    def _compute_lot_ids(self):
        for production in self:
            production.lot_ids_count = len([moveline.lot_id.id for moveline in move.move_line_ids  for move in production.move_finished_ids])
    
    
    @api.depends('program_ids')
    def _compute_duration(self):
        for production in self:
            amount_duration = sum(production.program_ids.mapped('duration'))
            production.amount_duration = amount_duration
            production.planned_hours =  production.amount_duration / 60.0
            
    
    
    # progress = fields.Float('Progress Done (%)', digits=(16, 2), compute='_compute_progress')
    

    production_origin_id   = fields.Many2one('mrp.production', string='Repeat Production')
    
    #Design
    warna = fields.Char(string='Warna', compute="_compute_warna")

    #greige
    greige_id           = fields.Many2one('product.product', string='Greige Name')
    std_potong          =  fields.Float(string='Std Potong',related="greige_id.std_potong")
    greige_code         =  fields.Char(string='Greige Code',related="greige_id.default_code")
    
    lebar_kain_finish   = fields.Float(string='Lebar Kain Finish')
    gramasi_kain_finish = fields.Float(string='Gramasi Kain Finish')
    density_kain_finish = fields.Float(string='Density Kain Finish')
    mkt_id              = fields.Many2one('marketing.order', string='Marketing Order',track_visibility='onchange')
    mkt_production_id   = fields.Many2one('mkt.production.line', string='Mkt Production')
    qty_mkt             = fields.Float(string='Total Order')
    
    component_chemical_has_request = fields.Boolean(string='Component chemical Requested ?',default=False)

    #Quantity Greige
    qty_roll_kp = fields.Float(string='Qty Roll Kp')
    qty_kg_kp = fields.Float(string='Qty Kg',compute="_compute_quantity")
    qty_yard_kp = fields.Float(string='Qty Yard')
    qty_meter_kp = fields.Float(string='Qty Meter',compute="_compute_quantity")

    #WIP
    qty_process = fields.Float(string='Qty Process')
    susut = fields.Float(string='Susut')
    ref_volume_mesin = fields.Float(string='Ref volume mesin')
    volume_mesin = fields.Float(string='Volume mesin')

    #inspect
    kategori_id = fields.Many2one('type.ship', string='Kategori')
    grading = fields.Selection([("10","10 Points"),("4","4 Points")], string='Grading')
    piece_length = fields.Integer(string='Piece Length')
    acessories_id = fields.Many2one('acessories', string='Acessories')
    hangtag_id = fields.Many2one('hangtag', string='Hangtag')

    proses_ids = fields.One2many('test.development.final', 'mrp_production_id', string='Flow Proses')

    #Start Field kebutuhan MO Sizing
    unit_sizing = fields.Char(string='Unit Sizing')
    location_id = fields.Many2one('stock.location', string='Location')
    kd_benang = fields.Char(string='Kode Benang')
    jenis_benang  = fields.Char(string='Jenis Benang')
    qty_benang = fields.Float(string='Berat Benang')
    sc_id = fields.Many2one('sale.contract', string='Kontrak', readonly=True,)
    
    nama_design = fields.Char(string='Nama Design')
    sisir_id = fields.Many2one('master.sisir', string='Sisir')
    total_end = fields.Float(string='Total End')
    jml_beam_stand = fields.Float(string='Jumlah Beam Stand')
    beaming_ids = fields.One2many('mrp.beaming', 'production_id', string='Beaming', readonly=False,)
    #End Field kebutuhan MO Sizing

    # Start Field Kebutuhan MO Weaving
    # lot_id          = fields.Many2one('stock.production.lot', string='Kartu Beam')
    # beam_id         = fields.Many2one('mrp.production.beam', related='lot_id.beam_id',string='No Beam')
    # beam_type_id    = fields.Many2one('mrp.production.beam.type', string='Beam Type')
    kode_test       = fields.Char(string='Kode Test')
    total_lusi      = fields.Float(string='Total Lusi')
    pick_in_greige  = fields.Float(string='Pick In Greige')
    jarum           = fields.Float(string='Jarum')
    pakan           = fields.Float(string='Pakan')
    rpm             = fields.Integer(string='Rpm')
    tgl_naik_beam   = fields.Date(string='Tanggal Naik Beam')
    tgl_hbs_beam    = fields.Date(string='Tanggal Habis Beam')
    date_selesai_proofing = fields.Date(string='Selesai Proofing')
    note            = fields.Text(string='Note')
    # End Field Kebutuhan MO Weaving

    # Start Field kebutuhan MO Twisting
    qty_penarikan_sw    = fields.Char(string='Penarikan Sw')
    no_om               = fields.Char(string='No SO')
    jenis_order         = fields.Selection([("lusi","Lusi"),("pakan","Pakan")], string='Jenis Order')
    jenis_mesin         = fields.Selection([("wjl","WJL"),("shuttle","Shuttle")], string='Jenis Mesin Weaving')
    revisi              = fields.Integer(string='Revisi')
    order_penarikan_sw  = fields.Float(string='Order Penarikan Sw')
    # End Field kebutuhan MO Twisting
    
    type_id = fields.Many2one('mrp.type', string='Order Type',required=True, track_visibility='onchange')
    is_permintaan_kain = fields.Boolean(string='Is Permintaan Kain ?')
    journal_count = fields.Integer(string='Journal Count', compute="compute_journal_count")
    employee_id = fields.Many2one('hr.employee', string='Pegawai')
    waste = fields.Float(string='Waste')
    
    is_inspected = fields.Boolean(string='Is Inspected',default=False)



    @api.onchange('mkt_production_id')
    def get_mkt_production_id(self):
        for rec in self:
            rec.qty_mkt = rec.mkt_production_id.quantity
    
    def action_chemical_excomponent_request(self):
        move_raw_ids = []
        move_chemical_request_ids = []
        if len(self.labdip_extra_ids) > 0:
            for component in self.labdip_extra_ids:
                product_qty = (component.conc * self.qty_kg_kp * 10 ) / 1000 if component.kategori == 'dye' else (component.conc * self.volume_air ) / 1000
                move_raw_ids.append((0,0,{
                    "name":component.product_id.name,
                    "product_id":component.product_id.id,
                    "product_uom_qty":product_qty,
                    "product_uom":component.product_id.uom_id.id,
                    "is_extra":True,
                    "location_id":self.type_id.component_location.id,
                    "location_dest_id":15,
                }))
            self.move_raw_ids = move_raw_ids
            for move_raw in self.move_raw_ids.filtered(lambda x: x.product_id.categ_id.name != 'GREY' and x.is_extra):
                    move_chemical_request_ids.append((0,0,{
                        "name":move_raw.product_id.name,
                        "product_id":move_raw.product_id.id,
                        "product_uom_qty":move_raw.product_uom_qty,
                        "product_uom":move_raw.product_id.uom_id.id,
                        "location_id":self.type_id.component_chemical_location.id,
                        "location_dest_id":self.type_id.component_location.id,
                        "move_dest_ids":[(4,move.id) for move in self.move_raw_ids.filtered(lambda x: x.product_id.categ_id.name != 'GREY')]
                    }))
                    
            
            self.env['stock.picking'].sudo().create({
                    "picking_type_id":self.type_id.component_chemical_picking_type_id.id,
                    "location_id":self.type_id.component_chemical_location.id,
                    "location_dest_id":self.type_id.component_location.id,
                    "mrp_request_id": self.mrp_request_id.id,
                    "production_id": self.id,
                    "origin": self.name,
                    "note": "Extra Obat",
                    "move_ids_without_package":move_chemical_request_ids
                })
                
            self.write({"is_request_extra_component":True})
            
                        
    
                        
    
    def action_chemical_component_request(self,qty_greige):
        move_raw_ids = []
        move_chemical_request_ids = []
        if self.labdip_id:
            labdip_final_ids = self.labdip_id.labdip_color_final_ids.filtered(lambda x: x.color_id.id == self.product_id.color_id.id)
            qty_kg_greige =  (self.gramasi_kain_finish / 1000 * self.lebar_kain_finish / 100) * 0.9144 * qty_greige 
            if self.move_raw_ids:
                # for lab in labdip_final_ids:
                #     for component in lab.labdip_resep_warna_ids:
                #         # product_qty = (component.conc * self.qty_kg_kp * 10 ) if component.kategori == 'dye' else (component.conc * self.volume_air ) / 1000
                #         product_qty = (component.conc * qty_kg_greige * 10 ) / 1000 if component.kategori == 'dye' else (component.conc * self.volume_air ) / 1000
                #         move_raw_ids.append((0,0,{
                #             "name":component.product_id.name,
                #             "product_id":component.product_id.id,
                #             "product_uom_qty":product_qty,
                #             "chemical_conc":component.conc,
                #             "product_uom":component.product_id.uom_id.id,
                #             "location_id":self.picking_type_id.default_location_src_id.id,
                #             # "location_id":self.type_id.component_location.id,
                #             "location_dest_id":15,
                #         }))
                
                        
                self.move_raw_ids = move_raw_ids
                for move_raw in self.move_raw_ids.filtered(lambda x: x.product_id.categ_id.name != 'GREY'):
                    # product_qty = (component.conc * qty_kg_greige * 10 ) / 1000 if component.kategori == 'dye' else (component.conc * self.volume_air ) / 1000
                    
                    move_chemical_request_ids.append((0,0,{
                        "name":move_raw.product_id.name,
                        "product_id":move_raw.product_id.id,
                        "product_uom_qty":move_raw.product_uom_qty,
                        "product_uom":move_raw.product_id.uom_id.id,
                        "chemical_conc":move_raw.chemical_conc,
                        "location_id":self.type_id.component_chemical_location.id,
                        "location_dest_id":self.picking_type_id.default_location_src_id.id,
                        # "location_dest_id":self.type_id.component_location.id,
                        "move_dest_ids":[(4,move.id) for move in self.move_raw_ids.filtered(lambda x: x.product_id.categ_id.name != 'GREY' and x.product_id.id == move_raw.product_id.id)]
                    }))
                    
            
                self.env['stock.picking'].sudo().create({
                    "picking_type_id":self.type_id.component_chemical_picking_type_id.id,
                    "location_id":self.type_id.component_chemical_location.id,
                    "location_dest_id":self.picking_type_id.default_location_src_id.id,
                    "mrp_request_id": self.mrp_request_id.id,
                    "production_id": self.id,
                    "origin": self.name,
                    "greige_qty_req":self.product_qty,
                    "move_ids_without_package":move_chemical_request_ids
                })
                
                self.write({"component_chemical_has_request":True})
            
                
            
                    
                    
            
    
    def _compute_quantity(self):
        for production in self:
            production.qty_meter_kp = production.product_qty * 0.9144
            production.qty_kg_kp =  (production.gramasi_kain_finish / 1000 * production.lebar_kain_finish / 100) * 0.9144 * production.mrp_request_id.quantity_shrinkage
            
    
    
    def _read(self, fields):
        # untuk kebutuhan view gantt planning production
        res = super()._read(fields)
        if self.env.context.get('display_product_and_color') and 'mesin_id' in self.env.context.get('group_by', []):
            name_field = self._fields['name']
            for record in self.with_user(SUPERUSER_ID):
                # variant = record.product_id.product_template_attribute_value_ids._get_combination_name()
                self.env.cache.set(record, name_field,record.name +' ' + record.product_id.name + ' ' + record.partner_id.name)
        return res
    
    @api.model
    def create(self, vals):
        type_id = self.env['mrp.type'].browse(vals.get('type_id'))
        if not vals.get('name'):
            vals['name'] = type_id.production_sequence_id.next_by_id()
        result = super(MrpProduction, self).create(vals)
        return result


    def action_change_src_location(self):
        bom_line_dict = {rec.product_id.id: rec.location_id.id for rec in self.bom_id.bom_line_ids}
        for rec in self.move_raw_ids:
            rec.write({'location_id' : bom_line_dict.get(rec.product_id.id)})
    
    @api.onchange('bom_id')
    def onchange_bom_id(self):
        print('onchange_bom_id')
        self.location_dest_id = self.bom_id.location_dest_id.id

    def _compute_warna(self):
        for a in self:
            for b in a.product_id:
                a.warna = b.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.name == 'WARNA').name
                break
    
    def get_parameter_process(self):
        data = {}
        for a in self.bom_id.operation_ids:
            data[a.workcenter_id.id] = [{'parameter_id': b.parameter_id.id, 'no_urut':b.no_urut, 'plan':b.plan,
            'actual':b.actual, 'uom_id':b.uom_id.id} for b in a.routing_paramter_ids]
        
        for rec in self.workorder_ids:
            rec.parameter_ids = False
            for x in data[rec.workcenter_id.id]:
                rec.parameter_ids = [(0, 0, x)]
                
    
    def get_last_wo(self):
        query = """
                SELECT  max(date_planned_finished)  as date_planned_finished 
                FROM mrp_workorder
                WHERE state != 'done' and
                is_planning = true
            """
        self._cr.execute(query)
        result = self._cr.dictfetchone()
        return result.get('date_planned_finished')
                
                
    def check_wo_planning(self):
        query = """
                SELECT id,production_id,date_planned_start 
                FROM mrp_workorder
                WHERE date_planned_start = '%s' and is_planning = true ORDER by date_planned_finished
            """%(fields.Datetime.add(fields.Datetime.now(), hours=7))
        self._cr.execute(query)
        result = self._cr.dictfetchall()
        if len(result) > 0:
            return True
        return False            
    
    
    
    
    # Start Overiding from base odoo
    def _create_workorder(self):
        sync_time = timedelta(hours=7)
        
        for production in self:
            if not production.bom_id:
                continue
            
            workorders_values = []
            filled = None
            if self.check_wo_planning():
                filled = True
            else:
                filled = False
            

            product_qty = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id)
            exploded_boms, dummy = production.bom_id.explode(production.product_id, product_qty / production.bom_id.product_qty, picking_type=production.bom_id.picking_type_id)

            for bom, bom_data in exploded_boms:
                # If the operations of the parent BoM and phantom BoM are the same, don't recreate work orders.
                if not (bom.operation_ids and (not bom_data['parent_line'] or bom_data['parent_line'].bom_id.operation_ids != bom.operation_ids)):
                    continue
                for idx,operation in enumerate(bom.operation_ids):
                    prev = workorders_values[idx - 1] if idx >= 1 else None
                    
                    duration = operation.program_id.duration
                    dt = timedelta(minutes=duration) if operation.program_id and operation.workcenter_id.is_planning else False
                    
                    dt_start = datetime.combine(self.date_planned_start.date(), datetime.min.time()) 
                    dt_finished = None
                    
                    if operation.program_id and operation.workcenter_id.is_planning and not  prev.get('date_planned_finished'):
                        dt_start = datetime.combine(self.date_planned_start.date(), datetime.min.time())
                        dt_finished = dt_start + dt if operation.program_id and operation.workcenter_id.is_planning else False
                        start_working = timedelta(hours=6,minutes=30) 
                        dt_start =  dt_start + start_working  if operation.program_id and operation.workcenter_id.is_planning else False
                        dt_start = dt_start - sync_time if not filled and operation.program_id and operation.workcenter_id.is_planning else dt_finished 
                    
                    elif operation.program_id and operation.workcenter_id.is_planning and idx > 0 and prev and prev.get('date_planned_finished'):
                        dt_start = prev.get('date_planned_finished')
                        dt_finished = dt_start + dt
                                
                        
            
                    
                    workorders_values += [{
                        'name': operation.name,
                        'production_id': production.id,
                        'workcenter_id': operation.workcenter_id.id,
                        'product_uom_id': production.product_uom_id.id,
                        "date_planned_start":dt_start if operation.workcenter_id.is_planning else False,
                        "date_planned_finished":dt_finished if operation.workcenter_id.is_planning else False,
                        'operation_id': operation.id,
                        'state': 'pending',
                        'consumption': production.consumption,
                        'mesin_id': operation.mesin_id.id,
                        'program_id': operation.program_id.id,
                    }]
            production.workorder_ids = [(5, 0)] + [(0, 0, value) for value in workorders_values]
            for workorder in production.workorder_ids:
                workorder.duration_expected = workorder._get_duration_expected()
    # End Overiding from base odoo

    def _get_move_raw_values(self, product_id, product_uom_qty, product_uom, operation_id=False, bom_line=False):
        res = super(MrpProduction, self)._get_move_raw_values(product_id, product_uom_qty, product_uom, operation_id=False, bom_line=False)
        if self.state == 'draft':
            self.move_raw_ids = False
        to_consume = 0
        # if self.type_id.name == 'DYEING':
        #     kateg_obat = bom_line.kategori_obat
        #     if kateg_obat:
        #         if kateg_obat == 'dye':
        #             to_consume = res.get('product_uom_qty', 0) * self.product_qty
        #         else:
        #             to_consume = res.get('product_uom_qty', 0) * self.kapasitas_mesin
        #     else:
        #         to_consume = res.get('product_uom_qty', 0) * self.product_qty
        # else:
        # to_consume = res.get('product_uom_qty', 0) * self.product_qty

        res['kategori_id'] = bom_line.kategori_id.id
        # res['product_uom_qty'] = to_consume # Customize To Consume
        res['location_id'] = bom_line.location_id.id
        res['kategori_obat'] = bom_line.kategori_obat
        res['kode_benang'] = bom_line.product_id.default_code
        res['lot_id'] = bom_line.lot_id.id
        res['type'] = bom_line.type
        # res['move_line_ids'] = [(0, 0, {'lot_id': bom_line.lot_id.id, 'location_id': self.location_src_id, ''})]
        print('resss', res)
        return res

    @api.onchange('type_id')
    def onchange_type_id(self):
        type = self.type_id
        # if type.id:
   
        res = {}
        res['domain'] = {'product_id': [('categ_id', 'in', type.finished_product_category_ids.ids)],"mkt_id":[('type_marketing','=','manufacture'),('production_type','=',self.type_id.id),('state','=','confirm')]}
        return res
    
    @api.onchange('mkt_id')
    def onchange_mkt_id(self):
        type = self.type_id
        if self.type_id.id == 4 and self.mkt_id:
            self.picking_type_id = type.picking_type_id.id
            self.location_dest_id = type.finished_location.id
            self.location_src_id = type.component_location.id
            self.product_id = self.mkt_id.yarn_id.id
            self.product_qty = self.mkt_id.quantity
            self.order_penarikan_sw = self.mkt_id.order_pull_sw
            self.jenis_order = self.mkt_id.yarn_type
            self.jenis_mesin = self.mkt_id.weaving_mc_type
            self.note = self.mkt_id.note
        elif self.type_id.id == 6 and self.mkt_id:
            self.picking_type_id = type.picking_type_id.id
            self.location_dest_id = type.finished_location.id
            self.location_src_id = type.component_location.id
            self.product_id = self.mkt_id.yarn_id.id
            self.greige_id = self.mkt_id.greige_id.id
            self.location_id = self.mkt_id.location_id.id
            self.product_qty = self.mkt_id.quantity
            self.order_penarikan_sw = self.mkt_id.order_pull_sw
            self.note = self.mkt_id.note

    @api.onchange('bom_id')
    def onchange_bom_id(self):
        type = self.type_id
        if type:
            self.picking_type_id = type.picking_type_id.id
            self.location_dest_id = type.finished_location.id
            self.location_src_id = type.component_location.id
        
    
    def action_view_journal(self):
        action = self.env.ref('account.action_move_journal_line').read()[0]
        action['domain'] = [('ref', 'ilike', self.name)]
        action['context'] = {}
        return action

    
    def compute_journal_count(self):
        count = self.env['account.move'].search_count([('ref', 'ilike', self.name)])
        self.journal_count = count
    
    def split_list_id(self, table):
        wo_ids = self.workorder_ids.mapped('parameter_ids.id')
        count_id = len(wo_ids)
        split = round(count_id / 2)
        if table == 'table_1':
            return wo_ids[0:split]
        if table == 'table_2':
            return wo_ids[split:]

    def action_print_resep(self):
        ctx = self.env.context
        # active_ids = ctx.get('active_ids')
        # url = "/report/pdf/inherit_mrp.report_mrp_print_resep/%s" % (','.join(list(map(str, active_ids))))
        # return {
        #     'name': 'Print Resep',
        #     'type': 'ir.actions.act_url',
        #     'url': url,
        #     'target': 'new',
        # }
        # print('action_print_resep==================')
        # ctx = self.env.context
        # active_ids = ctx.get('active_ids')
        # print('active_ids', active_ids)
        # url = "/report/pdf/inherit_mrp.report_mrp_print_resep/%s" % (','.join(list(map(str, active_ids))))
        # return {
        #     'name': 'Print Resep',
        #     'type': 'ir.actions.act_url',
        #     'url': url,
        #     'target': 'new',
        # }
        return self.env.ref('inherit_mrp.action_mrp_production_resep').report_action(self)

    def group_by_resep(self):
        query = """
                    select
                    sm.type as type
                    from stock_move sm
                    where raw_material_production_id = %s and type is not null
                    GROUP BY sm.type
                    ORDER BY sm.type
                """ % (self.id)
        self._cr.execute(query)
        res = self._cr.dictfetchall()
        return res
    
    def action_reprocess(self):
        print('action_reprocess')
        
    # @api.onchange('jenis_order')
    # def ganti_domain_product(self):
    #     if self.jenis_order:
    #         self.product_id = False
    #         return {'domain':{'product_id': [('categ_id', '=', 164 if self.jenis_order == 'lusi' else 162)]},} #BENANG LUSI TWISTING


    
    def action_view_stock_move_line(self):
        # _logger.warning('='*40)
        return {
            'res_model' : 'stock.move.line',
            'type'      : 'ir.actions.act_window',
            'name'      : _("Stock Move Line"),
            'domain'    : [('production_id', '=', self.id)],
            'view_mode' : 'tree,form',
        }