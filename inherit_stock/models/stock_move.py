from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class StockMove(models.Model):
    _inherit = 'stock.move'

    grade_id   = fields.Many2one('makloon.grade', string='Grade')
    machine_id = fields.Many2one('mrp.machine', string='Mesin')
    machine_no = fields.Char(related='machine_id.number', string='No Mesin', store=True,)
    id_partai  = fields.Char(string='Partai')
    hand3      = fields.Char(string='Hand')
    kd_proses  = fields.Char(string='Kode Proses')
    kd_keluar  = fields.Char(string='Kode Keluar')
    warna      = fields.Char(string='Warna') #sementara
    keterangan = fields.Char(string='Ket')
    
    
    
    def action_back_to_draft(self):
        if self.filtered(lambda m: m.state != "cancel"):
            raise UserError(_("You can set to draft cancelled moves only"))
        self.write({"state": "draft"})
    
    
    
class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    grade_id     = fields.Many2one('makloon.grade', string='Grade')
    default_code = fields.Char(string='Code',related='product_id.default_code')
    machine_id   = fields.Many2one('mrp.machine', string='Mesin',copy=True)
    machine_no   = fields.Char(related='machine_id.number', string='No Mesin', store=True)
    rack_id      = fields.Many2one('master.rack', string='Rack')
    warna        = fields.Char(string='Warna') #sementara
    qty_onhand   = fields.Float(string='On Hand', compute="_compute_qty_onhand")
    keterangan   = fields.Char(string='Ket')
    nozle        = fields.Selection([("nozle_1","Nozle 1"),("nozle_2","Nozle 2"),("nozle_3","Nozle 3"),("nozle_4","Nozle 4")], string='Nozle')
    qty_roll     = fields.Integer(string='Roll')
    pcs          = fields.Float(string='Pcs')
    keterangan_wo = fields.Char(string='Ket Wo')
    waste       = fields.Float(string='Waste')
    
    
            
    def open_split_barcode_wizard_form(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Split Barcode',
            'res_model': 'split.barcode.wizard',
            'view_mode': 'form',
            'context': {'default_picking_id':self.picking_id.id,'default_lot_id':self.lot_id.id,"default_quantity":self.qty_done,"default_move_line_id":self.id,"model":self._name},
            'target': 'new',
        }
        
    
    @api.model_create_multi
    def create(self, values):
        res = super(StockMoveLine, self).create(values)
        [move_line.move_id.write({"machine_id": val.get('machine_id') for val in values}) for move_line in res]
        return res
    
    
    @api.depends('product_id')
    def _compute_qty_onhand(self):
        for rec in self:
            domain = [('product_id', '=', rec.product_id.id),('location_id', '=', rec.location_id.id)]
            if rec.lot_id:
                domain.append(('lot_id','=',rec.lot_id.id))
            quant = self.env['stock.quant'].search(domain)
            rec.qty_onhand = sum(quant.mapped('quantity'))
    
    # @api.onchange('lot_id')
    # def onchange_lot_id(self):
    #     for rec in self:
    #         if rec.lot_id:
    #             rec.nozle = rec.picking_id.nozle