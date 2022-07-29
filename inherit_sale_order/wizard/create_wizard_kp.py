from odoo import fields, models, api, _
from odoo.exceptions import UserError

class CreateWizardKp(models.TransientModel):
    _name = 'create.wizard.kp'

    mesin_id = fields.Many2one('mrp.machine', string='Mesin', required=False, )
    date_kp = fields.Date(string='Date Produksi', required=True, )
    line_ids = fields.One2many('create.wizard.kp.line', 'create_wizard_kp_id', string='Line Ids')

    def action_create_kp(self):
        print('action_create_kp')
        mrp_production_obj = self.env['mrp.production']
        for a in self.line_ids:
            product_id = a.so_line_id.product_id
            bom = self.env['mrp.bom'].search([('product_id', '=', product_id.id)]).ids
            if not a.sale_id.hanger_code.id:
                raise UserError(_("Silahkan isi no hanger code untuk %s terlebih") % (a.sale_id.name))
            if len(bom) == 0:
                raise UserError(_("Tidak ada Bom untuk product %s ") % (product_id.name))
            hanger_code = a.sale_id.hanger_code         #TD
            mrp_production_obj.create({
                # 'type_id': self.env['mrp.type'].search([('name', '=', '	DYEING')]).id,                
                'type_id': 2,                
                'product_id' : product_id.id,
                'product_qty' : a.qty_proses,
                'product_uom_id' : a.so_line_id.product_uom.id,
                'date_planned_start' : self.date_kp,
                'jumlah_order' : a.qty_order,
                'sale_id' : a.sale_id.id,
                'sale_type' : a.sale_id.sale_type,
                'mesin_id' : self.mesin_id.id,
                'qty_process' : a.qty_proses,
                'greige_id': hanger_code.greige_id.id,
                'lebar_kain_finish' : hanger_code.lebar_target,
                'gramasi_kain_finish' : hanger_code.gramasi_target,
                'density_kain_finish' : hanger_code.density_target,
                'proses_ids' : [(6, 0, hanger_code.mapped('final_ids.id'))] 
            })
            a.so_line_id.write({'qty_remaining' : a.qty_sisa})

    
    
    @api.model
    def default_get(self, fields):
        res = super(CreateWizardKp, self).default_get(fields)
        context = self.env.context
        sale_obj = self.env['sale.order.line'].browse(context.get('active_ids'))
        data = [(0, 0, {'so_line_id' : a.id, 'qty_sisa' : a.qty_remaining}) for a in sale_obj]
        res.update({'line_ids' : data})
        return res


class CreateWizardKpLine(models.TransientModel):
    _name = 'create.wizard.kp.line'

    so_line_id = fields.Many2one('sale.order.line', string='SO Line')
    sale_id = fields.Many2one('sale.order', string='SO', related="so_line_id.order_id")
    qty_order = fields.Float(string='Qty Order', related="so_line_id.product_uom_qty")
    qty_proses = fields.Float(string='Qty Proses')
    qty_sisa = fields.Float(string='Qty Sisa')
    create_wizard_kp_id = fields.Many2one('create.wizard.kp', string='Wizard Kp ID')

    @api.onchange('qty_proses')
    def _onchange_qty_proses(self):
        for rec in self:
            if rec.qty_proses > rec.qty_sisa:
                raise UserError("Mohon maaf qty untuk diproses melebihi qty sisa")
            rec.qty_sisa = rec.qty_order - rec.qty_proses