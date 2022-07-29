from odoo import fields, models, api, _
from odoo.exceptions import UserError

class StockPointOrderLineWizard(models.TransientModel):

    _name = 'stock.point.order.line.wizard'
    
    request_id = fields.Many2one('mrp.request', string='Request',help="Existing Request",domain=[('state', '=', 'draft')])
    order_line_ids = fields.Many2many(
        comodel_name='stock.point.order.line', 
        relation='make_request_from_stock_point_order_rel',
        string='Details'
        )
    
    
    
    
    
    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_model = self.env.context.get("active_model", False)
        request_line_ids = []
        if active_model == "stock.point.order.line":
            request_line_ids += self.env.context.get("active_ids", [])
        if request_line_ids:
            res['order_line_ids'] = [(4,id) for id in request_line_ids ]
        return res





    

    def action_create_request(self):
        if not self.request_id:
            request_id = self.env['mrp.request'].create({"order_lines":[(6,0,self.order_line_ids.ids)]})
            if request_id:
                for line in self.order_line_ids:
                    line.write({"mrp_request_id":request_id.id})
            action = self.env.ref('mrp_request.mrp_request_action').read()[0]
            action['domain'] = [('id','=',request_id.id)]
            action['context'] = {}
            return action
            
        else:
            self.request_id.write({"order_lines":[(4,line.id) for line in self.order_line_ids]})
            if self.request_id:
                for line in self.order_line_ids:
                    line.write({"mrp_request_id":self.request_id.id})
            action = self.env.ref('mrp_request.mrp_request_action').read()[0]
            action['domain'] = [('id','=',self.request_id.id)]
            action['context'] = {}
            return action
