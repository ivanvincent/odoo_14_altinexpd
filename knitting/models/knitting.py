from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ProduksiKnitting(models.Model):
    _name = 'produksi.knitting'

    name = fields.Char(string='Name')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirm'),
        ], string='Status', default='draft')
    knitting_ids = fields.One2many('produksi.knitting.line', 'knitting_id', string='Knitting Line')
    date = fields.Date(string='Date')
    operator_id = fields.Many2one('hr.employee', string='Operator MC')
    tot_roll = fields.Integer(string='Total Roll', compute='_compute_quantity_all',)
    total_quantity = fields.Float(string='Total Quantity', compute='_compute_quantity_all',)
    keterangan = fields.Text(string='Keterangan')

    # Start Field Required For Device MQTT
    scale = fields.Char(string='Scale',)
    # device_id = fields.Many2one('wibicon.iot.device', string='Device', default=lambda self: int(self.env['ir.config_parameter'].sudo().get_param('wibicon_iot_box.mrp_device_id.id', default=0)))
    # topic = fields.Char(related='device_id.topic', string='Topic',store=True,)
    # broker = fields.Char(related='device_id.broker', string='Broker',store=True,)
    # End Field Required For Device MQTT

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('produksi.knitting')
        vals['name'] = seq
        result = super(ProduksiKnitting, self).create(vals)
        return result


    @api.depends('knitting_ids.qty')
    def _compute_quantity_all(self):
        for order in self:
            order.total_quantity = 0.0
            order.tot_roll = 0.0
            order.total_quantity = sum(line.qty for line in order.knitting_ids)
            order.tot_roll = len(order.knitting_ids)


    def action_confirm(self):
        for rec in self.knitting_ids:
            rec.lot_id.write({
                'knitting_line_id'  : rec.id,
            })
        self.write({"state": "confirm"})

class ProduksiKnittingLine(models.Model):
    _name = 'produksi.knitting.line'

    name = fields.Char(string='Name')
    knitting_id = fields.Many2one('produksi.knitting', string='Knitting')
    greige_id = fields.Many2one('product.product', string='Greige')
    shift = fields.Selection([("pagi","Pagi"),("sore","Sore"),("malam","Malam")], string='Shift')
    operator_id = fields.Many2one('hr.employee', string='Operator MC', related='knitting_id.operator_id')
    machine_id = fields.Many2one('mrp.machine', string='Machine')
    tanggal_potong = fields.Date(string='Tanggal Potong', related='knitting_id.date')
    no_potong = fields.Integer(string='No Potong')
    no_roll = fields.Integer(string='No Roll')
    lot_id = fields.Many2one('stock.production.lot', string='Barcode')
    qty = fields.Float(string='Quantity KG')

    mrp_id = fields.Many2one('mrp.production', string='MRP')
    barcode = fields.Char(string='Barcode')

    @api.model
    def create(self, vals):
        seq = self.env['ir.sequence'].next_by_code('produksi.knitting.line')
        vals['name'] = seq
        result = super(ProduksiKnittingLine, self).create(vals)
        return result

    @api.onchange('barcode')
    @api.depends('knitting_id.scale')
    def get_onchange_barcode_mrp(self):
        barcode_mrp = self.env['mrp.production']
        
        if self.barcode:
            lot = barcode_mrp.search([('name', '=', self.barcode)])
            self.mrp_id = lot.id
            self.greige_id = lot.product_id.id
            self.qty = self.knitting_id.scale
            self.action_generate_barcode_greige()
            

    def action_generate_barcode_greige(self):
        lotObj = self.env['stock.production.lot']
        for rec in self:
            newLotId = lotObj.create({
                'company_id'        : 1,
                'product_id'        : rec.greige_id.id,
                'bruto'             : rec.qty,
                'mrp_id'            : rec.mrp_id.id,
                # 'knitting_line_id'  : rec.id,
            })
            rec.write({
                'lot_id'        : newLotId.id,
            })