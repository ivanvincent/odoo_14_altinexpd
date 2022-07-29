from odoo import models, fields, api, _
from odoo.exceptions import UserError,ValidationError


class StockMove(models.Model):
    _inherit = 'stock.move'
        
    
    
    @api.onchange('quantity_done')
    def _check_allowance(self):
        if self.purchase_line_id:
            quantity_allowance = self.product_uom_qty + (self.product_uom_qty * self.product_id.allowance / 100)
            if self.product_id.allowance == 0 and self.quantity_done > self.product_uom_qty:
                raise ValidationError('Mohon Maaf Allowance Belum Ditentukan ,\nQuantity Terima Melebihi Quantity PO \n Silahkan Hubungi Administrator')
            elif self.product_id.allowance > 0 and self.quantity_done > quantity_allowance:
                raise ValidationError('Mohon Maaf Quantity Terima Melebihi Allowance Yang Ditentukan\n Silahkan Hubungi Administrator')
                

    
    