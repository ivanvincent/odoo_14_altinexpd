from odoo import models, fields, api

class MasterOpc(models.Model):
    _name = 'master.opc'

    name            = fields.Char(string='Name')
    fabric_code     = fields.Char(string='Fabric Code')
    category_design = fields.Char(string='Category Design')
    opc_id          = fields.Many2one('opc', string='Name Opc')
    line_ids        = fields.One2many('master.opc.line', 'master_opc_id', 'Line')
    type            = fields.Selection([("lab","Lab"),("finish","Finish")], string='Type')
    handling        = fields.Selection([("soft","Soft"),("medium","Medium"),("hard","Hard")], string='Handling')
    handling_id     = fields.Many2one('master.handling', string='Master Handling')

    @api.model
    def create(self, values):
        type = values.get('type')
        seq = False
        if type == 'lab':
            seq = self.env['ir.sequence'].next_by_code('opc.lab')
        else:
            seq = self.env['ir.sequence'].next_by_code('opc.finish')
        values['name'] = seq
        result = super(MasterOpc, self).create(values)
        return result

    # @api.model
    def name_get(self):
        result = []
        for rec in self:
            result.append((rec.id, str(rec.name) + ' - ' + str(rec.opc_id.name)))
        return result
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res_search = False
        res = self.search(['|',('name',operator,name),('opc_id.name', operator, name)] + args, limit=limit)
        res_search = res.name_get()
        return res_search

class MasterOpcLine(models.Model):
    _name = 'master.opc.line'

    name = fields.Char(string='Name')
    product_id = fields.Many2one('product.product', string='Item')
    qty = fields.Float(string='Qty', digits=(12,4))
    # uom_id = fields.Many2one('uom.uom', string='UoM', related='product_id.uom_id')
    master_opc_id = fields.Many2one('master.opc', 'Master')

class NameOpc(models.Model):
    _name = 'opc'

    name = fields.Char(string='Name')