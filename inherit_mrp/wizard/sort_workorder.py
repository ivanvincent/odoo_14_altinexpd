from odoo import fields, models, api, _
from odoo.exceptions import UserError

class SortWorkOrderWizard(models.TransientModel):

    _name = 'sort.workorder.wizard'
    
    
    date_start   = fields.Date(string='Date', default=fields.Date.today())
    date_finished = fields.Date(string='Date Finished', default=fields.Date.today())

    def need_to_sort(self):
        return self.date_start
