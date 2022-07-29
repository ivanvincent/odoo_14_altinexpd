from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class ManufacturingOrders(models.Model):
    _inherit = 'mrp.production'

    mrp_request_id           = fields.Many2one('mrp.request', string='Mrp Request')
    picking_request_ids      = fields.Many2many('stock,picking', string='Picking Request',compute="_compute_picking_request")
    picking_request_count    = fields.Integer( string='Picking Request Amount',compute="_compute_picking_request")
    pakan                    = fields.Char(related='mrp_request_id.pakan', string='Pakan')
    std_susut                = fields.Float(related='mrp_request_id.std_susut',string='Std Susut')
    pic                      = fields.Integer(related='mrp_request_id.pic',string='Pic')
    lebar                    = fields.Integer(related='mrp_request_id.lebar',string='Lebar')
    beam_id                  = fields.Many2one('mrp.production.beam', string='Beam')
    tgl_naik_beam            = fields.Date(string='Tanggal Naik Beam')
    tgl_hbs_beam             = fields.Date(string='Tanggal Habis Beam')
    mrp_request_detail_id    = fields.Many2one('mrp.request.detail', string='Mrp Request Detail')
    machine_id               = fields.Many2one('mrp.machine', string='Machine')
    quantity_request         = fields.Float(string='Quantity Request')
    
    @api.depends('mrp_request_id')
    def _compute_picking_request(self):
        for production in self:
            pickings = self.env['stock.picking'].search([('production_id','=',production.id),('mrp_request_id','=',production.mrp_request_id.id)])
            _logger.warning('='*40)
            _logger.warning(pickings)
            _logger.warning('='*40)
            production.picking_request_count = len(pickings)
            production.picking_request_ids = pickings.ids
    
    
    
    def action_view_request_picking(self):
        result = self.env["ir.actions.actions"]._for_xml_id('stock.action_picking_tree_all')
        pick_ids = self.mapped('picking_request_ids')
        if not pick_ids or len(pick_ids) > 1:
            result['domain'] = "[('id','in',%s)]" % (pick_ids.ids)
        elif len(pick_ids) == 1:
            res = self.env.ref('stock.view_picking_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state,view) for state,view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = pick_ids.id
        return result
    

    
    def action_view_inspect(self):
        # _logger.warning('='*40)
        return {
            'res_model': 'produksi.inspect',
            'type': 'ir.actions.act_window',
            'name': _("Inspect Finish Goods"),
            'domain': [('production_id', '=', self.id)],
            'view_mode': 'tree,form',
        }

    def button_check(self):
        self.product_qty = self.quantity_request
        self.qty_producing = self.quantity_request
        self._onchange_move_raw()
        for rec in self.move_raw_ids:
            rec.quantity_done = rec.product_uom_qty
    
    def button_validate_mo(self):
        self._button_mark_done_sanity_checks()
        self._post_inventory()
        

class MprTYpe(models.Model):
    _inherit = 'mrp.type'
    
    
    inspect_picking_type_id  = fields.Many2one('stock.picking.type', string='Inspect Operation Type')
    inspect_location_id      = fields.Many2one('stock.location', string='Inspect Location')
    inspect_location_dest_id = fields.Many2one('stock.location', string='Inspect Destination Location')

    