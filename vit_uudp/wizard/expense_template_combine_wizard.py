from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ExpenseTemplateCombineWizard(models.TransientModel):
    _name = 'expense.template.combine.wizard'
    _description = 'Expense Template Combine Wizard'
    
    name          = fields.Char(string='Template Kombinasi')
    ajuan_id = fields.Many2one('uudp', string='Ajuan')
    warehouse_ids = fields.Many2many(comodel_name='stock.warehouse', string='Stock Point')
    jalur_ids     = fields.Many2many(comodel_name='res.partner.jalur', string='Jalur')
    uudp_line_ids = fields.Many2many(comodel_name='uudp.detail', string='Details')
    
    def action_submit(self):
        template_id = self.env['expense.template.combine'].create({
            'name':self.name,
            'warehouse_ids':[(6,6,self.warehouse_ids.ids)],
            'jalur_ids':[(6,6,self.jalur_ids.ids)],
            'line_ids':[(0,0,{
                'product_id':line.product_id.id,
                'account_id':line.coa_debit.id,
                'nominal':line.unit_price,
                })for line in self.uudp_line_ids]
        })
        
        
        if template_id:
            self.ajuan_id.write({'template_comb_id':template_id.id})
            
        