from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)




class PengajuanWizard(models.TransientModel):
    _name = 'pengajuan.op.wizard'
    _description = 'Pengajuan Wizard'

    
    
    category_id = fields.Many2one('uudp.category', string='Category',default=1)
    date        = fields.Date(string='Required Date', default=fields.Date.today())
    end_date    = fields.Date(string='Due Date', default=fields.Date.today())
    line_ids    = fields.One2many('pengajuan.op.line.wizard', 'wizard_id', 'Details')
   
    
    @api.model
    def default_get(self,fields):
        res = super(PengajuanWizard,self).default_get(fields)
        context = self._context
        active_ids = context.get('active_ids')
        jalur_ids = self.env['res.partner.jalur'].browse(active_ids)
        
        if jalur_ids:
            res['line_ids'] = [(0,0,{
                "jalur_id":jalur.id,
                "warehouse_id":jalur.warehouse_id.id
                }) for jalur in jalur_ids]
            
        
        
        
        return res
        
    
    def create_pengajuan(self):
        uudp_ids = []
        
        if self.line_ids:
            for line in self.line_ids:
                if not line.warehouse_id:
                    raise UserError('Mohon maaf Stock Point / Warehouse tidak boleh kosong')
                if not line.vehicle_id:
                    raise UserError('Mohon maaf Vehicle tidak boleh kosong')
                if not line.employee_id:
                    raise UserError('Mohon maaf yang mengajukan tidak boleh kosong')
                if not line.driver_id:
                    raise UserError('Mohon maaf driver tidak boleh kosong')
                uudp_id = self.env['uudp'].create({
                    "category_id":self.category_id.id,
                    "type":'pengajuan',
                    "end_date": self.end_date,
                    "warehouse_ids":[(4,line.warehouse_id.id)],
                    "jalur_ids":[(4,line.jalur_id.id)],
                    "employee_id": line.employee_id.id,
                    "vehicle_id": line.vehicle_id.id,
                    "driver_id": line.driver_id.id,
                    "sales_id": line.sales_id.id,
                    "helper_id": line.helper_id.id,
                })
                if uudp_id:
                    uudp_id.get_end_date()
                    uudp_id.onchange_jalur_ids()
                    uudp_id._get_department()
                    uudp_ids += [uudp_id.id]
                
            action = self.env.ref('vit_uudp.action_uudp_pengajuan_list').read()[0]
            action['domain'] = [('id','in',uudp_ids)]
            action['context'] = {}
            return action
    
    
    

class PengajuanLineWizard(models.TransientModel):
    _name = 'pengajuan.op.line.wizard'
    
    
    wizard_id    = fields.Many2one('pengajuan.op.wizard', string='Wizard')
    warehouse_id = fields.Many2one('stock.warehouse', string='Stock Point')
    jalur_id     = fields.Many2one('res.partner.jalur', string='Jalur')
    employee_id  = fields.Many2one('hr.employee', string='Yang Mengajukan')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle')
    driver_id  = fields.Many2one('hr.employee', string='Driver')
    sales_id  = fields.Many2one('hr.employee', string='Sales')
    helper_id  = fields.Many2one('hr.employee', string='Helper')
    
    
    
