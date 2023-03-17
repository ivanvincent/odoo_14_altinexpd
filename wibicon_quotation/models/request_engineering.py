from odoo import models, fields, api

class RequestEngineering(models.Model):
    _name = 'request.engineering'

    name = fields.Char(string='Name')
    state = fields.Selection([("draft","Draft"),("approve","Approve")], string='State', default='draft')
    line_ids = fields.One2many('request.engineering.line', 'request_engineering_id', 'Line')
    # type = fields.Selection([("from_quotation","Quotation"),("from_wo","Mor")], string='Type')
    type_id = fields.Many2one('request.engineering.type', string='Type')
    no_drawing = fields.Char(string='No. Drawing')
    uk_bahan = fields.Char(string='Ukuran Bahan')
    picking_id = fields.Many2one('stock.picking', string='Picking')
    quotation_id = fields.Many2one('quotation', string='Quotation')

    def action_approve(self):
        print("action_approve")
        type = self.type_id
        if not self.picking_id and self.state != 'approve':
            picking_obj = self.env['stock.picking'].create({
                'picking_type_id' : type.picking_type_id.id,
                'location_id'     : type.picking_type_id.default_location_src_id.id,
                'location_dest_id': type.picking_type_id.default_location_dest_id.id,
                "origin"          : self.quotation_id.name,
                'move_ids_without_package': [(0, 0, {
                    'type_material'   : l.name,
                    'name'            : l.product_id.name,
                    'product_id'      : l.product_id.id,
                    'product_uom_qty' : 1,
                    'product_uom'     : l.product_id.uom_id.id,
                    'location_id'     : type.picking_type_id.default_location_src_id.id,
                    'location_dest_id': type.picking_type_id.default_location_dest_id.id,
                }) for l in self.line_ids]
            })
            self.picking_id = picking_obj.id
            self.state = 'approve'


class RequestEngineeringLine(models.Model):
    _name = 'request.engineering.line'

    request_engineering_id = fields.Many2one('request.engineering', string='Engineering')
    name = fields.Char(string='Material')
    # value = fields.Char(string='Value')
    product_id = fields.Many2one('product.product', string='Value')

class RequestEngineeringType(models.Model):
    _name = 'request.engineering.type'

    name = fields.Char(string='Name')
    picking_type_id = fields.Many2one('stock.picking.type', string='Picking Type')