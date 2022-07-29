from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class InspectReturnWizard(models.TransientModel):

    _name = 'inspect.return.wizard'
    
    
    inspect_id           = fields.Many2one('produksi.inspect', string='Inspect')
    production_id        = fields.Many2one('mrp.production', string='Production')
    line_ids             = fields.Many2many('stock.move.line.before', string='Details')
    description          = fields.Text(string='Reason')
    
    @api.model
    def default_get(self,fields):
        res = super(InspectReturnWizard,self).default_get(fields)
        inspect_id = self.env.context.get("default_inspect_id", False)
        inspect_id = self.env['produksi.inspect'].sudo().browse([inspect_id])
        res['line_ids'] = [(4,move.id) for move in inspect_id.moveline_before_ids.filtered(lambda x:x.state == 'produced' and x.lot_id)]
        return res
    

    def action_return(self):
        ids_to_change = self._context.get('active_ids')
        active_model = self._context.get('active_model')
        doc_ids = self.env[active_model].browse(ids_to_change)
