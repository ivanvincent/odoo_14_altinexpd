from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MRPRawRevistion(models.Model):
    _name = 'mrp.raw.revision'

    name          = fields.Char(string='Revision')
    date          = fields.Date(string='Date', default=fields.Date.today())
    production_id = fields.Many2one('mrp.production', string='Production')
    picking_id    = fields.Many2one('stock.picking', string='Stock Picking')
    greige_id     = fields.Many2one('product.product', string='Greige',domain=[('categ_id.name', '=', 'GREY')])
    product_id    = fields.Many2one('product.product', string='Greige Revision',domain=[('categ_id.name', '=', 'GREY')])
    uom_id        = fields.Many2one(related='greige_id.uom_id', string='Uom')
    quantity      = fields.Float(string='Quantity')
    
    note          = fields.Text(string='Note')
    move_raw_ids  = fields.Many2many('stock.move', string='Move Raw')
    user_id       = fields.Many2one('res.users', string='Requested By',default=lambda self: self.env.user.id)
    state         = fields.Selection([("draft","Draft"),('confirm',"Confirm"),("approved_lab"," Approved Lab"),('done','Done')], string='State')
    
    
    
    def action_confirm(self):
        self.state = 'confirm'
    
    def action_to_approve_lab(self):
        self.state = 'approved_lab'

    def action_done(self):
        self.state = 'done'
        
    
    
    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('mrp.raw.revision')
        vals['name'] = seq
        result = super(MRPRawRevistion, self).create(vals)
        return result
    