from odoo import models, fields, api, _ ,SUPERUSER_ID
from odoo.exceptions import UserError

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
      
    
    



class MrpWorkOrderLine(models.Model):
    _name = 'mrp.workorder.line'
    
    
    #todo add parameter_ids secara actual

    name            = fields.Char(string='Number')
    workorder_id    = fields.Many2one('mrp.workorder', string='Workorder')
    production_id   = fields.Many2one( related='workorder_id.production_id', string='Production',store=True,)
    workcenter_id   = fields.Many2one('mrp.workcenter', string='Workcenter')
    machine_id      = fields.Many2one('mrp.machine', string='Machine')
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
    
    def _read(self, fields):
        res = super()._read(fields)
        if self.env.context.get('display_product_and_color') and 'machine_id' in self.env.context.get('group_by', []):
            name_field = self._fields['name']
            for record in self.with_user(SUPERUSER_ID):
                self.env.cache.set(record, name_field,' '+ record.workcenter_id.name + ' ' + record.production_id.name )
        return res
    