from odoo import models, fields, api, _
from odoo.exceptions import UserError

class RequestRequisition(models.Model):
    _inherit = 'request.requisition'
    
    
    def print_rr(self):
        self.ensure_one()
        if self.env.user.has_group('request_requisition.group_request_requisition_print_user') and self.print_count == 0:
            self.print_count += 1
            return self.env.ref('report_print.action_print_request').report_action(self)
        elif self.env.user.has_group('request_requisition.group_request_requisition_print_manager') or self.env.user.id == 2:
            self.print_count += 1
            return self.env.ref('report_print.action_print_request').report_action(self)



    