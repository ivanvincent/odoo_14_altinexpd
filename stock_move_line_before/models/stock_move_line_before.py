from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockMoveLineBefore(models.Model):
    _name = 'stock.move.line.before'

    name                 = fields.Char(string='Stock Move Line Before')
    date                 = fields.Date(string='Date', default=fields.Date.today())
    lot_id               = fields.Many2one('stock.production.lot', string='Barcode')
    lot_parent_name      = fields.Char(string='Barcode Parent')
    lot_name             = fields.Char(string='Lot Name')
    product_id           = fields.Many2one('product.product', string='Product' )
    product_uom_id       = fields.Many2one(related='product_id.uom_id', string='Uom')
    production_id        = fields.Many2one('mrp.production', string='Production')
    machine_id           = fields.Many2one('mrp.machine', string='Machine',related="production_id.mesin_id")
    production_type_id   = fields.Many2one('mrp.type', related='production_id.type_id' ,string='Production Type')
    sj_pro_app           = fields.Char(string='SJ Pro App')
    lot_prepare_id       = fields.Many2one('stock.production.lot', string='Lot Of Beam')
    quantity             = fields.Float(string='Quantity')
    employee_id          = fields.Many2one('hr.employee', string='Employee',)
    ka_shift_id          = fields.Many2one('hr.employee', string='Ka Shift')
    maintenance_id       = fields.Many2one('hr.employee', string='Mtc')
    pic                  = fields.Integer(string='Pic')
    rpm                  = fields.Integer(string='Rpm')
    work_time            = fields.Float(string='Jam Kerja')
    grade_id             = fields.Many2one('makloon.grade', string='Grade',default=1)
    move_id              = fields.Many2one('stock.move', string='Move')
    location_id          = fields.Many2one('stock.location', string='Location')
    shift                = fields.Selection(selection=[('a', 'A'),('b', 'B'),('c', 'C'),],string='Shift' )
    type_dopping         = fields.Selection([("pw","PW"),("tfo","TFO"),("vhs","VHS"),("jumbo","Jumbo")], string='Type Dopping')
    # defect_ids           = fields.One2many('stock.move.line.defect', 'move_id', string='Defect Ids')
    defect_ids           = fields.Many2many('product.defect', string='Defect')
    
    state                = fields.Selection(selection=[('production', 'Production'),('inspecting', 'Inspecting'),('produced', 'Produced'),('transfer', 'Transferred'),('split','Splitted')],string='State',default="production")
    is_inspected         = fields.Boolean(string='Inspected ?', default=False,help="When enable record has been hide on display count" )

    move_ids             = fields.One2many('stock.move', 'move_before_id', string='Stock Move')
    type_transfer        = fields.Selection([("in","In"),("out","Out")], string='In/Out')
    

class StockMoveLineDefect(models.Model):
    _name = 'stock.move.line.defect'
    
    date        = fields.Date(string='Date', default=fields.Date.today())
    defect_id   = fields.Many2one('product.defect', string='Defect')
    move_id     = fields.Many2one('stock.move.line.before', string='Stock Move Line Before')
    start_with  = fields.Float(string='Start With',help="to describe when defects were discovered",)
    end_with    = fields.Float(string='End With',help="to describe when the defect was not found")


class StockMove(models.Model):
    _inherit = 'stock.move'

    move_before_id = fields.Many2one('stock.move.line.before', string='Stock Move Line Before')

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    move_line_before_ids            = fields.One2many('stock.move.line.before', 'production_id', string='Inspecting')

    pw_move_line_before_ids         = fields.One2many('stock.move.line.before', 'production_id', string='Line Dopping', domain=[('type_dopping', '=', 'pw')])
    tfo_move_line_before_ids        = fields.One2many('stock.move.line.before', 'production_id', string='Line Dopping', domain=[('type_dopping', '=', 'tfo')])
    vhs_move_line_before_ids        = fields.One2many('stock.move.line.before', 'production_id', string='Line Dopping', domain=[('type_dopping', '=', 'vhs')])
    jumbo_move_line_before_ids      = fields.One2many('stock.move.line.before', 'production_id', string='Line Dopping', domain=[('type_dopping', '=', 'jumbo')])
    interlace_move_line_before_ids  = fields.One2many('stock.move.line.before', 'production_id', string='Line Dopping', domain=[('type_dopping', '=', 'interlace')])

    total_pw_in                     = fields.Float(compute='_compute_total_twisting', string='Total Masuk PW', store=False)
    total_pw_out                    = fields.Float(compute='_compute_total_twisting', string='Total Hasil PW', store=False)
    total_tfo_in                    = fields.Float(compute='_compute_total_twisting', string='Total Masuk TFO', store=False)
    total_tfo_out                   = fields.Float(compute='_compute_total_twisting', string='Total Hasil TFO', store=False)
    total_vhs_in                    = fields.Float(compute='_compute_total_twisting', string='Total Masuk VHS', store=False)
    total_vhs_out                   = fields.Float(compute='_compute_total_twisting', string='Total Hasil VHS', store=False)
    total_jumbo_in                  = fields.Float(compute='_compute_total_twisting', string='Total Masuk Jumbo', store=False)
    total_jumbo_out                 = fields.Float(compute='_compute_total_twisting', string='Total Hasil Jumbo', store=False)
    total_interlace_in              = fields.Float(compute='_compute_total_twisting', string='Total Masuk Interlace', store=False)
    total_interlace_out             = fields.Float(compute='_compute_total_twisting', string='Total Hasil Interlace', store=False)
    progress_production_twisting    = fields.Float('Progress', compute="_get_progress", copy=False)

    @api.depends('move_line_before_ids')
    def _get_progress(self):
        for rec in self:
            if rec.type_id.code == 'TFO':
                if rec.jenis_order == 'lusi':
                    rec.progress_production_twisting = rec.total_vhs_out / rec.product_qty * 100
                else:
                    rec.progress_production_twisting = rec.total_jumbo_out / rec.product_qty * 100
            elif rec.type_id.code == 'ITW':
                rec.progress_production_twisting = rec.total_interlace_out / rec.product_qty * 100
    
    @api.depends('pw_move_line_before_ids','tfo_move_line_before_ids','vhs_move_line_before_ids','jumbo_move_line_before_ids')
    def _compute_total_twisting(self):
        for rec in self:
            rec.total_pw_in         = sum(rec.pw_move_line_before_ids.filtered(lambda x: x.type_transfer == 'in').mapped('quantity'))
            rec.total_pw_out        = sum(rec.pw_move_line_before_ids.filtered(lambda x: x.type_transfer == 'out').mapped('quantity'))
            rec.total_tfo_in        = sum(rec.tfo_move_line_before_ids.filtered(lambda x: x.type_transfer == 'in').mapped('quantity'))
            rec.total_tfo_out       = sum(rec.tfo_move_line_before_ids.filtered(lambda x: x.type_transfer == 'out').mapped('quantity'))
            rec.total_vhs_in        = sum(rec.vhs_move_line_before_ids.filtered(lambda x: x.type_transfer == 'in').mapped('quantity'))
            rec.total_vhs_out       = sum(rec.vhs_move_line_before_ids.filtered(lambda x: x.type_transfer == 'out').mapped('quantity'))
            rec.total_jumbo_in      = sum(rec.jumbo_move_line_before_ids.filtered(lambda x: x.type_transfer == 'in').mapped('quantity'))
            rec.total_jumbo_out     = sum(rec.jumbo_move_line_before_ids.filtered(lambda x: x.type_transfer == 'out').mapped('quantity'))
            rec.total_interlace_in  = sum(rec.interlace_move_line_before_ids.filtered(lambda x: x.type_transfer == 'in').mapped('quantity'))
            rec.total_interlace_out = sum(rec.interlace_move_line_before_ids.filtered(lambda x: x.type_transfer == 'out').mapped('quantity'))

    is_inspecting        = fields.Integer(compute='_compute_inspecting', string='Total', store=False)
    
    def action_dopping(self):
        return {
            'type'      : 'ir.actions.act_window',
            'name'      : 'Dopping',
            'res_model' : 'mrp.dopping.wizard',
            'view_mode' : 'form',
            'context'   : {'default_mrp_id' : self.id,'default_product_id' : self.product_id.id,'default_type_id' : self.type_id.id},
            'target'    : 'new',
        }
   
    
    @api.depends('move_line_before_ids')
    def _compute_inspecting(self):
        self.is_inspecting = self.move_line_before_ids.filtered(lambda x: x.is_inspected != True)
        
        
    def action_view_inspecting(self):
        action = self.env["ir.actions.actions"]._for_xml_id("stock_move_line_before.stock_move_line_before_action")
        # template_ids = self.mapped('product_tmpl_id').ids
        # bom specific to this variant or global to template
        # action['context'] = {
        #     'default_product_tmpl_id': template_ids[0],
        #     'default_product_id': self.ids[0],
        # }
        # action['domain'] = ['|', ('product_id', 'in', self.ids), '&', ('product_id', '=', False), ('product_tmpl_id', 'in', template_ids)]
        return action
    
  
    