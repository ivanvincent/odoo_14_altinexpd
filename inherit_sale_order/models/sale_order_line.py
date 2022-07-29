from odoo import models, fields, api, _
from odoo.exceptions import UserError

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    color = fields.Many2one('makloon.warna', String='Color')
    color_no_labdip = fields.Many2one('labdip.warna','Color No')
    color_no   = fields.Char(string='Color no')
    partner_id = fields.Many2one('res.partner', string='Partner')
    labdip_id = fields.Many2one('labdip','Labdip No',)
    qty_weight = fields.Float('Qty (KG)',)
    qty_length = fields.Float('Qty Length (YARDS)', compute="_compute_konversi", invers=True)
    uom = fields.Many2one('uom.uom', String='UOM')
    description = fields.Char('Description')
    qty_remaining =  fields.Float('Qty Sisa',store=True)
    strikeoff_id = fields.Many2one('strikeoff', related="order_id.strike_off_id", string='Strike Off')
    sto_line_id = fields.Many2one('strikeoff.detail', string='Strike Line')
    batch = fields.Char(string='Batch')
    total_batch = fields.Float(string='Total Batch')
    qty_pcs = fields.Integer('Quantity Pcs')
    qty_meter = fields.Float('Quantity Meter', compute="_compute_konversi_mtr")
    meter_conv = fields.Float('Meter Conversion')
    mesin_id = fields.Char('Mesin Printing')
    wip_status = fields.Char('Wip Status')
    wip_date = fields.Date('Wip Date')
    wip_days = fields.Date('Wip Days')
    remarks = fields.Char('Remarks')
    kp_existed = fields.Boolean('Is KP existed?', default=False)
    contract_id = fields.Many2one(related='order_id.contract_id', store=True, string='No SC')
    wo_date = fields.Date(related='order_id.wo_date', store=True, string='Tanggal WO')
    delivery_date = fields.Date(related='order_id.delivery_date', required=True, string='Delivery Date')
    qty_process = fields.Float('Qty Proses',store=True)
    # kp_wo_line_ids = fields.One2many('kartu.proses','sodet_id',string='Kartu Proses')
    # image = fields.Binary(string='Image', related='order_id.strike_off_id.image')
    color_makloon_id   = fields.Many2one('makloon.warna',string='Color',)
    keterangan = fields.Text(string='Keterangan')
    ref_wo = fields.Char(related='order_id.origin', string='WO Ref')
    type_sc = fields.Selection(
        selection=[
            ('dyeing', 'Work Order Dyeing'),
            ('printing', 'Work Order Printing'),
            ],
        string='Type',)
    qty_minimum                = fields.Float(string='Qty Minimum',)
    color_customer_id          = fields.Many2one('makloon.warna', string='Color Customer')
    # variasi_id                 = fields.Many2one('tj.stock.variasi', string='Variation Name', related="order_id.hanger_code.variasi_id")
    # greige_code                = fields.Char(string='Greige Code', related="order_id.hanger_code.greige_code")
    quantity_roll = fields.Float(string='Roll')

    contract_line_id = fields.Many2one('sale.contract.line', string='Sale Contract Line', copy=False)
    standart_price = fields.Float(string='Standart Price', readonly=True, related="standart_price_temporary")
    standart_price_temporary = fields.Float(string='Standart Price',)
    kategori_so = fields.Selection([("kain","Kain"),("none_kain","Non Kain")], string='Kategori SO')
    jenis_proses = fields.Selection([("dyeing","Dyeing"),("printing","Printing")], string='Jenis Proses')
    # design_id = fields.Many2one('makloon.design', string='No Design')
    design_id = fields.Many2one(related='product_id.design_id', string='Design')
    employee_id = fields.Many2one('hr.employee', string='Sales Person', related='order_id.employee_id', store=True,)
    greige_id = fields.Many2one(string='Greige', related='order_id.greige_id', store=True,)
    on_hand_greige = fields.Float(string='On Hand Greige', compute='compute_onhand_greige')
    is_created_mo = fields.Boolean(string='Created  Mo?', compute='_compute_is_created_mo', store=True, compute_sudo=True)


    @api.model
    def create(self, vals):
        vals['qty_remaining'] = vals.get('product_uom_qty')
        res = super(SaleOrderLine, self).create(vals)
        return res

    @api.model
    def write(self, vals):
        if vals.get('product_uom_qty', 0) > 0:
            vals['qty_remaining'] = vals.get('product_uom_qty')
        res = super(SaleOrderLine, self).write(vals)
        return res
    
    def action_view_mo(self):
        print('action_view_mo')
    
    @api.depends('order_id')
    def _compute_is_created_mo(self):
        for rec in self:
            mo_obj = self.env['mrp.production'].search([('sale_id', '=', rec.order_id.id)])
            rec.is_created_mo = True if len(mo_obj) > 1 else False

    @api.depends('greige_id')
    def compute_onhand_greige(self):
        """
            location_id 1297 = GDGK
        """
        for rec in self:
            stock = self.env['stock.quant'].search([('location_id', '=', 1297), ('product_id', '=', rec.greige_id.id)])
            rec.on_hand_greige = sum(stock.mapped('quantity'))
            