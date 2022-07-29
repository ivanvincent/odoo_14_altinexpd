from email.policy import default
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from ast import literal_eval


class RuteSaleLineGroup(models.Model):
    _name = 'rute.sale.line.group'
    
    
    
    rute_id        = fields.Many2one('rute.sale', string='Rute Sale',required=True,)
    line_ids       = fields.One2many('rute.sale.line', 'group_id', string='Rute Sale Line')
    product_id     = fields.Many2one('product.product', string='Product',required=True, )
    price_unit     = fields.Float(string='Price Unit',related="product_id.lst_price")
    default_code   = fields.Char('Code',related="product_id.default_code")
    product_uom_id = fields.Many2one(related='product_id.uom_id', string='Satuan')
    product_uom_qty = fields.Float(string='Quantity')
    
    
class RuteSaleLineExpense(models.Model):
    _name = 'rute.sale.line.expense'
    
    
    
    rute_id        = fields.Many2one('rute.sale', string='Rute Sale',required=True,)
    expense_id     = fields.Many2one('rute.sale.expense', string='Expense')
    quantity       = fields.Float(string='Quantity')



class RuteSaleLine(models.Model):
    _name = 'rute.sale.line'
    
    
    
    rute_id        = fields.Many2one('rute.sale', string='Rute Sale',required=True, )
    group_id       = fields.Many2one('rute.sale.line.group', string='Group')
    location_id    = fields.Many2one('stock.location', string='Location', compute="_get_default_location")
    fg_id          = fields.Many2one('rute.sale.line.fg', string='Finish Good')
    siba_id        = fields.Many2one('rute.sale.line.siba', string='SIBA')
    type           = fields.Selection([("fg","Finish Good"),("siba","Siba")], string='Type')
    product_id     = fields.Many2one('product.product', string='Product',required=True, )
    price_unit     = fields.Float(string='Price Unit',related="product_id.lst_price")
    default_code   = fields.Char('Code',related="product_id.default_code",store=True,)
    product_uom_id = fields.Many2one(related='product_id.uom_id', string='Satuan')
    product_uom_qty = fields.Float(string='Quantity')
    qty_onhand      = fields.Float(string='On Hand',compute="_compute_qty_onhand")
    
    def _get_default_location(self):
        for line in self:
            if line.type == 'fg':
                line.location_id = line.rute_id.config_id.default_location_fg_id.id
            elif line.type == 'siba':
                line.location_id = line.rute_id.config_id.default_location_siba_id.id
            else:
                line.location_id = False
    
    
    def _compute_qty_onhand(self):
        for line in self:
            domain = [('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id)]
            quant = self.env['stock.quant'].search(domain).mapped('quantity')
            line.qty_onhand = sum(quant)
    
    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        def create_group(rute_line):
            new_group = self.env['rute.sale.line.group'].create({
                "rute_id":rute_line.rute_id.id,
                "product_id":rute_line.product_id.id,
                "product_uom_qty":rute_line.product_uom_qty,
            })
            
            rute_line.group_id = new_group
            
        for rute_line in lines:
            rute = rute_line.rute_id.line_ids.filtered(lambda l:l.product_id == rute_line.product_id)
            create_group(rute_line)
            
        
        return lines
            






class RuteSaleLineFinishGood(models.Model):
    _name = 'rute.sale.line.fg'
    
    
    
    rute_id         = fields.Many2one('rute.sale', string='Rute Sale',required=True, )
    line_id         = fields.Many2one('rute.sale.line', string='Line')
    location_id     = fields.Many2one('stock.location', string='Location', compute="_get_default_location")
    product_id      = fields.Many2one('product.product', string='Product',required=True)
    image_1920      = fields.Image("Image", related="product_id.image_1920")
    image_512       = fields.Image("Image", related="product_id.image_512")
    image_128       = fields.Image("Image", related="product_id.image_128")
    default_code    = fields.Char('Code',related="product_id.default_code")
    product_uom_id  = fields.Many2one(related='product_id.uom_id', string='Satuan')
    product_uom_qty = fields.Float(string='Quantity')
    price_unit      = fields.Float(string='Price Unit',related="product_id.lst_price")
    qty_onhand      = fields.Float(string='On Hand',compute="_compute_qty_onhand")
    
    @api.model
    def create(self, vals):
        if vals.get('product_id'):
            rute_line = self.env['rute.sale.line'].create({
                "rute_id":vals.get('rute_id'),
                "fg_id":self._origin.id,
                "type":"fg",
                "product_id":vals.get('product_id'),
                "product_uom_qty":vals.get('product_uom_qty')
                
            })
            vals['line_id'] = rute_line.id
            
        return super(RuteSaleLineFinishGood, self).create(vals)
    
    @api.model
    def write(self, vals):
        product_id = vals.get('product_id') if vals.get('product_id') is not None else self.product_id.id
        quantity = vals.get('product_uom_qty') if vals.get('product_uom_qty') is not None else self.product_uom_qty
        line_id = vals.get('line_id') or self.line_id
        if product_id or quantity:
            do_line = self.env['rute.sale.line'].search([("rute_id",'=',self.rute_id.id),("id",'=',line_id.id),("type","=","fg")])
            if  do_line:
                do_line.write({
                    "product_uom_qty":quantity,
                    "product_id":product_id,
                })
        return super(RuteSaleLineFinishGood, self).write(vals)
    
    @api.model
    def unlink(self):
        self.mapped('line_id').unlink()
        res = super(RuteSaleLineFinishGood, self).unlink()
        return res
    
    
    @api.depends('product_id')
    def _compute_qty_onhand(self):
        for line in self:
            domain = [('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id)]
            quant = self.env['stock.quant'].search(domain).mapped('quantity')
            line.qty_onhand = sum(quant)
    
    def _get_default_location(self):
        for line in self:
            if line.rute_id.config_id:
                line.location_id = line.rute_id.config_id.default_location_fg_id.id
            else:
                line.location_id = False
    
class RuteSaleLineSiba(models.Model):
    _name = 'rute.sale.line.siba'
    
    
    
    rute_id        = fields.Many2one('rute.sale', string='Rute Sale',required=True, )
    line_id        = fields.Many2one('rute.sale.line', string='Line')
    location_id = fields.Many2one('stock.location', string='Location', compute="_get_default_location")
    default_code   = fields.Char('Code',related="product_id.default_code")
    product_id     = fields.Many2one('product.product', string='Product',required=True)
    product_uom_id = fields.Many2one(related='product_id.uom_id', string='Satuan')
    price_unit      = fields.Float(string='Price Unit',related="product_id.lst_price")
    product_uom_qty = fields.Float(string='Quantity')
    qty_onhand      = fields.Float(string='On Hand',compute="_compute_qty_onhand")
    
    
    @api.model
    def create(self, vals):
        if vals.get('product_id'):
            do_line = self.env['rute.sale.line'].create({
                "rute_id":vals.get('rute_id'),
                "siba_id":self._origin.id,
                "type":"siba",
                "product_id":vals.get('product_id'),
                "product_uom_qty":vals.get('product_uom_qty')
                
            })
            vals['line_id'] = do_line.id
            
        return super(RuteSaleLineSiba, self).create(vals)
    
    
    @api.model
    def write(self, vals):
        product_id = vals.get('product_id') if vals.get('product_id') is not None else self.product_id.id
        quantity = vals.get('product_uom_qty') if vals.get('product_uom_qty') is not None else self.product_uom_qty
        line_id = vals.get('line_id') or self.line_id
        if product_id or quantity:
            do_line = self.env['rute.sale.line'].search([("siba_id",'=',self.do_id.id),("id",'=',line_id.id),("type","=","siba")])
            if  do_line:
                do_line.write({
                    "product_uom_qty":quantity,
                    "product_id":product_id,
                })
        return super(RuteSaleLineSiba, self).write(vals)
    
    
    @api.model
    def unlink(self):
        self.mapped('line_id').unlink()
        res = super(RuteSaleLineSiba, self).unlink()
        return res

    
    
    @api.depends('product_id')
    def _compute_qty_onhand(self):
        for line in self:
            domain = [('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id)]
            quant = self.env['stock.quant'].search(domain).mapped('quantity')
            line.qty_onhand = sum(quant)
    
    def _get_default_location(self):
        for line in self:
            if line.rute_id.config_id:
                line.location_id = line.rute_id.config_id.default_location_siba_id.id
            else:
                line.location_id = False
    
    
    
class RuteSaleLineReturn(models.Model):
    _name = 'rute.sale.line.return'
    
    
    
    rute_id        = fields.Many2one('rute.sale', string='Rute Sale',required=True, )
    line_id        = fields.Many2one('rute.sale.line', string='Line')
    location_id    = fields.Many2one('stock.location', string='Location',compute="_get_default_location")
    default_code   = fields.Char('Code',related="product_id.default_code")
    product_id     = fields.Many2one('product.product', string='Product',required=True)
    price_unit      = fields.Float(string='Price Unit',related="product_id.lst_price")
    product_uom_id = fields.Many2one(related='product_id.uom_id', string='Satuan')
    product_uom_qty = fields.Float(string='Quantity')
    qty_onhand      = fields.Float(string='On Hand',compute="_compute_qty_onhand")
    
    @api.depends('product_id')
    def _compute_qty_onhand(self):
        for line in self:
            domain = [('product_id', '=', line.product_id.id), ('location_id', '=', line.location_id.id)]
            quant = self.env['stock.quant'].search(domain).mapped('quantity')
            line.qty_onhand = sum(quant)
    
    
    def _get_default_location(self):
        for line in self:
            if line.rute_id.config_id:
                line.location_id = line.rute_id.config_id.default_location_return_id.id
            else:
                line.location_id = False