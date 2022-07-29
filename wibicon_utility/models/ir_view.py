from odoo import models, fields, api, _
from odoo.exceptions import UserError

class View(models.Model):
    _inherit = 'ir.ui.view'
    
    
    
    type = fields.Selection(  selection_add=[("wibiconlist", "Wibicon List"),("accordion","Accordion"),("owl_tree","Owl Tree")])
    
    
class IrActWindowView(models.Model):
    _inherit = 'ir.actions.act_window.view'

    view_mode = fields.Selection(selection_add=[('accordion', "Accordion")], ondelete={'accordion': 'cascade'})
    