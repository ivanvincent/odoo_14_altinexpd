from odoo import models, fields, api, _
from odoo.exceptions import UserError



class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    
    credit_limit      = fields.Float(string='Credit Limit')
    sisa_limit        = fields.Float(string='Sisa Limit',compute="_get_sisa_limit")
    reset_limit       = fields.Selection([("week","Week"),("month","Month"),("year","Year")], string='Reset Limit',default="month")
    
    
    def action_reset_limit(self):
        self.sisa_limit = self.credit_limit
            
    
    
    @api.depends('credit_limit')
    def _get_sisa_limit(self):
        for employee in self:
            if employee.credit_limit:
                employee.sisa_limit = employee.credit_limit
                ajuan_ids = self.env['uudp'].search([('employee_id','=',employee.id),('state','=','done')])
                if ajuan_ids:
                    total_pencairan = sum([item.total  for ajuan in ajuan_ids  for item in ajuan.uudp_ids])
                    employee.sisa_limit = employee.credit_limit - total_pencairan

            else:
                employee.sisa_limit = 0
            



class HRDepartment(models.Model):
    _inherit = 'hr.department'
    
    
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    
    
    

    