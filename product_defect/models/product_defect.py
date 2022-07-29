from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProductDefect(models.Model):
    _name = 'product.defect'

    name        = fields.Char(string='Defect')
    code        = fields.Char(string='Code')
    description = fields.Char(string='Description')
    is_active   = fields.Boolean(string='Active' ,default=True)
    
    _sql_constraints = [
        ('defect_uniq', 'unique(name)', 'Defect must be unique !')
    ]
    
    
    def name_get(self):
        result = []
        for defect in self:
            result.append((defect.id, str(defect.code) + ' - ' + str(defect.name)))
        return result
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res_search = False
        res = self.search([ '|',('name',operator,name),('code',operator,name)] + args, limit=limit)
        res_search = res.name_get()
        return res_search
