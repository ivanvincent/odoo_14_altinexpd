from odoo import api, fields, models, _

class Hr_contract(models.Model):
    _name = 'hr.contract'
    _inherit = 'hr.contract'

    name 					 = fields.Char('Contract Reference', required=True)
    employee_id 			 = fields.Many2one('hr.employee', string='Employee', required=True)
    cost_sharing			 = fields.Boolean("Cost Sharing")
    shift_working_schedule   = fields.Boolean(string="Shift Working Schedule")
    umk   					 = fields.Float(string="UMK")
    resign_date              = fields.Date(string="Resign Date")
    real_end_duration        = fields.Date(string="Real End Duration", compute="_get_date", store=True)


    @api.depends('resign_date')
    def _get_date(self):
        for date in self:
            if date.resign_date and date.date_end:
                
                date.real_end_duration = date.date_end
                # date.date_end = date.resign_date


    @api.depends('name', 'employee_id')
    def name_get(self):
    	#import pdb;pdb.set_trace()
        result = []
        for account in self:
            name = '['+ (account.name or '') + '] ' + (account.employee_id.name or '')
            result.append((account.id, name))
        return result
        
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if not recs:
            recs = self.search(['|', ('name', operator, name),('employee_id.name', operator, name)] + args, limit=limit)
        return recs.name_get() 