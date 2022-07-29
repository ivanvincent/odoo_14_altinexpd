from odoo import models, fields, api, _,tools
from odoo.exceptions import UserError

import logging 
_logger = logging.getLogger(__name__)

class MrpPlanning(models.Model):
    _name = 'mrp.production.planning'
    _auto = False

    date_planned  = fields.Date(string='Tanggal')
    variant_id    = fields.Many2one('product.product', string='Variant')
    product_id    = fields.Many2one('product.template', string='Product',related='variant_id.product_tmpl_id')
    greige_id     = fields.Many2one('product.product', string='Greige')
    code          = fields.Char(related='variant_id.default_code', string='Design Code')
    machine_id    = fields.Many2one('mrp.machine', string='Machine')
    quantity      = fields.Float(string='Quantity')
    uom_id        = fields.Many2one('uom.uom', string='Uom',related="variant_id.uom_id")
    batch_count   = fields.Integer(string='Batch')
    state         = fields.Char(string='State')
    
    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute('''
            CREATE OR REPLACE VIEW %s AS (
            SELECT 
                row_number() OVER() AS id,
                mo.product_id as variant_id,
                sm.product_id as greige_id,
                mo.date_planned_start as date_planned,
                mo.mesin_id as machine_id,
                SUM(mo.product_qty) as quantity,
                mo.state as state,
                COUNT(DISTINCT mo.id) as batch_count
            FROM 
                mrp_production mo 
            LEFT JOIN
                stock_move sm on mo.id = sm.raw_material_production_id 
            LEFT JOIN 
                product_product pr ON mo.product_id = pr.id
            LEFT JOIN
                mrp_machine mm ON mo.mesin_id = mm.id
            WHERE 
                mo.STATE = 'draft' AND mo.type_id = 2
            GROUP 
                BY mo.product_id,mo.date_planned_start,mo.mesin_id,mo.state,sm.product_id 
            )''' % (self._table,)
        )
        
        
    @api.model
    def action_print_components_request(self):
        return self.env['report'].get_action(self._context.get('active_ids'), 'inherit_mrp.action_report_components_request')