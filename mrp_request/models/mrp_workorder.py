from odoo import models, fields, api, _ ,SUPERUSER_ID
from odoo.exceptions import UserError
from datetime import datetime,timedelta,time
from dateutil.relativedelta import relativedelta
from odoo.addons.mrp.models.mrp_workorder import MrpWorkorder as workorder

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'
    
    #todo add scrap ids/afkir , compute product uom qty at workorder_ids
    
    workorder_ids    = fields.One2many('mrp.workorder.line', 'workorder_id', 'Workorder Detail')
    # html_color       = fields.Char(related='production_id.html_color', string='Color',store=True,)
    machine_id       = fields.Many2one('mrp.machine', string='Machine')
    actual_qty       = fields.Float(compute='_get_actual_qty', string='Actual Qty', store=False)
    parameter_ids    = fields.One2many('mrp.operation.template.line.parameter', string='Parameters',related="operation_id.parameter_ids")
    satuan_id        = fields.Many2one('satuan.produksi', string='Satuan Produksi',related="production_id.satuan_id")
    production_qty   = fields.Float(string='Production Qty',related="production_id.mrp_qty_produksi")
    product_code     = fields.Char(related='product_id.default_code', string='Code')
    is_highrisk      = fields.Boolean(string='Highrish ?', related='production_id.is_highrisk', store=True,)
    rework_qty       = fields.Float(string='Rework Qty', compute='_compute_total_rework')
    setting_machine_ids = fields.One2many('setting.machine', 'workorder_id', 'Line')
    inputed_wo_daily = fields.Boolean(string='Inputed Wo Daily ?', default=False)
    no_urut          = fields.Integer(string='No Urut', compute='_compute_no_urut')
    date_hold        = fields.Date(string='Date Hold')
    date_unhold      = fields.Date(string='Date Unhold')
    
    @api.depends('workorder_ids')
    def _get_actual_qty(self):
        for workorder in self:
            production_qty = sum(workorder.workorder_ids.mapped('product_uom_qty'))
            workorder.actual_qty = production_qty

   

    def action_show_details(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Workorder Details',
            'res_model': 'mrp.workorder',
            'view_mode': 'form',
            'context':{'default_workorder_id':self.id},
            'target': 'new',
        }

    ########################################################################
    ### 
    ### override button start  method supaya tanggal planning tidak ke update
    ### 
    ########################################################################
    
    
    
    
    def button_start(self):
        self.ensure_one()
        # As button_start is automatically called in the new view
        if self.state in ('done', 'cancel'):
            return True
        
    
 
        if self.product_tracking == 'serial':
            self.qty_producing = 1.0

        self.env['mrp.workcenter.productivity'].create(
            self._prepare_timeline_vals(self.duration, datetime.now())
        )
        if self.production_id.state != 'progress' and not self.date_planned_start:
            self.production_id.write({
                'date_start': datetime.now(),
            })
        if self.state == 'progress':
            return True
        
       

        start_date = datetime.now()
        vals = {
            'state': 'progress',
            'date_start': start_date,
        }
        if not self.leave_id:
            leave = self.env['resource.calendar.leaves'].create({
                'name': self.display_name,
                'calendar_id': self.workcenter_id.resource_calendar_id.id,
                'date_from': start_date,
                'date_to': start_date + relativedelta(minutes=self.duration_expected),
                'resource_id': self.workcenter_id.resource_id.id,
                'time_type': 'other'
            })
            vals['leave_id'] = leave.id
            return self.write(vals)
        else:
            if self.date_planned_start > start_date and not self.date_planned_start and not self.workcenter_id.is_planning:
                vals['date_planned_start'] = start_date
            if self.date_planned_finished and self.date_planned_finished < start_date:
                vals['date_planned_finished'] = start_date
            return self.write(vals)
        
    @api.depends('name')
    def _compute_no_urut(self):
        for rec in self:
            rec.no_urut = int(rec.name)
        
    

    workorder.button_start = button_start

    def _compute_total_rework(self):
        for rec in self:
            rec.rework_qty = sum(rec.workorder_ids.mapped('qty_rework'))



class MrpWorkOrderLine(models.Model):
    _name = 'mrp.workorder.line'
    
    
    #todo add parameter_ids secara actual

    name            = fields.Char(string='Number')
    workorder_id    = fields.Many2one('mrp.workorder', string='Workorder')
    production_id   = fields.Many2one(related='workorder_id.production_id', string='Production',store=True,)
    workcenter_id   = fields.Many2one('mrp.workcenter', string='Workcenter')
    # machine_id      = fields.Many2one('mrp.machine', string='Machine')
    machine_ids     = fields.Many2many(comodel_name='mrp.machine', string='Machine')
    
    no_machine      = fields.Integer(string='No Machine')
    location_id     = fields.Many2one('stock.location', string='Location')
    product_uom_qty = fields.Float(string='Quantity',help="Quantity Actual")
    production_qty  = fields.Float(string='Quantity Target')
    shift           = fields.Selection([("pagi","Pagi"),("siang","Siang"),("malam","Malam")], string='Shift')
    employee_id     = fields.Many2one('hr.employee', string='Employee')
    date            = fields.Date(string='Date', default=fields.Date.today())
    waste_ids       = fields.One2many('mrp.waste', 'workorder_line_id', string='Waste')
    afkir_ids       = fields.One2many('mrp.afkir', 'workorder_line_id', string='Afkir')
    wo_daily_id     = fields.Many2one('workorder.daily', 'Workorder Daily')
    workorder_fat_ids = fields.One2many('workorder.fat', 'workorder_line_id', 'Line')
    is_rework       = fields.Boolean(string='Rework ?')
    qty_rework      = fields.Float(string='Qty Rework')
    resource_calendar_ids = fields.Many2one('resource.calendar', string='Working Hours',)
    time_standard   = fields.Float(string='Time Standard', related='workcenter_id.time_std', store=True,)
    parameter_id    = fields.Many2one('mrp.parameter', string='Parameter')
    
    def _read(self, fields):
        res = super()._read(fields)
        if self.env.context.get('display_product_and_color') and 'machine_id' in self.env.context.get('group_by', []):
            name_field = self._fields['name']
            for record in self.with_user(SUPERUSER_ID):
                self.env.cache.set(record, name_field,' '+ record.workcenter_id.name + ' ' + record.production_id.name )
        return res
    
    def action_open_detail_fat(self):
        action = self.env.ref('mrp_request.mrp_workorder_line_fat_action').read()[0]
        action['res_id'] = self.id
        return action