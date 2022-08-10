from odoo import fields, models, api, _
from odoo.exceptions import UserError

class MrpWorkorderSplitWizard(models.TransientModel):

    _name = 'mrp.workorder.split.wizard'
    
    
    production_id    = fields.Many2one('mrp.production', string='Production',required=True, )
    satuan_id        = fields.Many2one(related='production_id.satuan_id', string='Satuan Produksi')
    product_qty      = fields.Float(string='Quantity',related="production_id.product_qty")
    production_qty   = fields.Float(string='Qty Produksi',related="production_id.mrp_qty_produksi")
    product_uom_id   = fields.Many2one(string='Satuan',related="production_id.product_uom_id")
    split_qty        = fields.Integer(string='Qty Split ')
    qty_per_wo       = fields.Float(string='Quantiy Per Wo',compute="_get_qty_per_workoder")
    
    
    @api.onchange('split_qty')
    def onchange_split_qty(self):
        self._get_qty_per_workoder()
    
        
    
    @api.depends('split_qty')
    def _get_qty_per_workoder(self):
        self.qty_per_wo = 0 if self.split_qty < 1 else self.production_qty / self.split_qty
            
    
    
    
    

    def action_split_workorder(self):
        if self.split_qty < 1:
            raise UserError('Mohon maaf qty split tidak boleh bol')
        else:
            workorder_seq_ids = []
            for line in range(self.split_qty):
                ir_config        = self.env['ir.config_parameter'].sudo()
                wo_sequence_id  = ir_config.get_param('wo_sequence_id')
                if wo_sequence_id:
                    seq = self.env['ir.sequence'].browse(int(wo_sequence_id)).next_by_id()
                    workorder_seq_ids += [seq]
                    
            
            for workorder in self.production_id.workorder_ids:
                for line in workorder_seq_ids:
                    workorder_ids =  [(0,0,{
                        "workorder_id":workorder.id,
                        "name":line,
                        "workcenter_id":workorder.workcenter_id.id,
                        "production_qty":self.qty_per_wo,
                    })]
                    workorder.sudo().write({
                        'workorder_ids':workorder_ids
                    })
            

            self.production_id.write({"splitted_wo": True})
            action = self.env.ref('mrp_request.mrp_workorder_line_action').read()[0]
            action['domain'] = [('production_id','=',self.production_id.id)]
            action['context'] = {'group_by':['name']}
            return action