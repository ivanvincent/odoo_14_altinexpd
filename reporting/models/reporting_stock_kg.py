from odoo import models, fields, api
from odoo.exceptions import UserError
import base64
from io import BytesIO
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT 
import xlsxwriter
from . import add_workbook_format as awf
from datetime import datetime
import pytz
from pytz import timezone
import logging
from lxml import etree

_logger = logging.getLogger(__name__)

class ReportingStockKg(models.Model):
    _name = 'reporting.stock.kg'

    # name = fields.Char(string='Label dari Field')

    _rec_name = 'location_id'

    # @api.multi
    def get_default_date_multi(self):
        date_time = pytz.UTC.localize(datetime.now()).astimezone(timezone('Asia/Jakarta'))
        return date_time.strftime('%d/%m/%Y %H:%M:%S')

    def get_product_category(self):
        return [category.id  for warehouse in self.env.user.default_warehouse_ids for category in warehouse.product_category_ids ]

    name                        = fields.Char(string='Name')
    start_date                  = fields.Date('Start Date', default=datetime.now())
    end_date                    = fields.Date('End Date', default=datetime.now() )
    inventory_date              = fields.Datetime('Inventory Date', related='inventory_id.date')
    user_id                     = fields.Many2one('res.users', 'Created by', default=lambda self: self.env.user)
    inventory_id                = fields.Many2one('stock.inventory', string='Inventory Adjustment')
    location_id                 = fields.Many2one('stock.location', 'Location', domain=[('usage','=','internal')])
    product_category_id         = fields.Many2one('product.category', string='Product Category', domain=lambda self: [('id','in',self.get_product_category())],)
    line_ids                    = fields.One2many('reporting.stock.kg.line', 'reporting_id', 'Details', ondelete="cascade")
    history_ids                 = fields.One2many('reporting.stock.kg.line.history', 'reporting_id', string="History")
    history_in_id               = fields.One2many('reporting.stock.kg.line.history', 'reporting_id', string="History", domain=[('stock_type', '=', 'receipt')])
    history_out_id              = fields.One2many('reporting.stock.kg.line.history', 'reporting_id', string="History", domain=[('stock_type', '=', 'release')])
    history_return_in_id        = fields.One2many('reporting.stock.kg.line.history', 'reporting_id', string="History", domain=[('stock_type', '=', 'return_in')])
    history_return_out_id       = fields.One2many('reporting.stock.kg.line.history', 'reporting_id', string="History", domain=[('stock_type', '=', 'return_out')])
    history_adjustment_in_id    = fields.One2many('reporting.stock.kg.line.history', 'reporting_id', string="History", domain=[('stock_type', '=', 'adjustment_in')])
    history_adjustment_out_id   = fields.One2many('reporting.stock.kg.line.history', 'reporting_id', string="History", domain=[('stock_type', '=', 'adjustment_out')])
    data                        = fields.Binary(string='Image')
    type_reporting              = fields.Selection([("internal","Internal"),("all","All")], string='Type', default='internal')
    state                       = fields.Selection([('open', 'Open'),('locked', 'Locked'),], string='Status', default='open')

    
    
    @api.onchange('start_date')
    def onchange_start_date(self):
        if self.start_date and self.inventory_date: 
            if self.start_date < self.inventory_date.date():
                raise UserError('Tanggal Tidak Boleh kurang dari tanggal opname (Inventory Date)')
        
    
    def generate_penyesuaian(self):
        date_end = "%s 12:00:00"%self.end_date
        StockAdjustment     = self.env['stock.inventory']
        lines               = []
        for rec in self.line_ids:
            # if rec.penyesuaian > 0:
            lines.append((0, 0, {
                'product_id'        : rec.product_id.id,
                'product_uom_id'    : rec.product_id.uom_id.id,
                'location_id'       : self.location_id.id,
                'product_qty'       : rec.penyesuaian,
            }))
        data = {
            'name'          : 'Opname' + ' ' + self.location_id.name + ' ' + str(self.end_date),
            'location_ids'  : [(4, self.location_id.id)],
            'line_ids'      : lines,
            'state'         : 'draft',
        }
        AdjObj = StockAdjustment.create(data)
        AdjObj.action_start()
        AdjObj.write({'date': date_end,'accounting_date': self.end_date})
        AdjObj.action_validate()
        self.state = 'locked'
        return {
            'res_id'    : AdjObj.id,
            'view_id'   : self.env.ref('stock.view_inventory_form').ids,
            'view_type' : 'form',
            "view_mode" : 'form',
            'res_model' : 'stock.inventory',
            'type'      : 'ir.actions.act_window',
            'target'    : 'current'
        }

    def unlink(self):
        if self.state == 'locked':
            raise UserError(_('You cannot delete a reporting !!!'))
        return super(ReportingStockKg, self).unlink()


    def action_calculate(self):
        self.action_delete_reporting()
        self.action_calculate_internal()

    def action_delete_reporting(self):
        query = """
            DELETE FROM reporting_stock_kg_line where reporting_id = %s;

            DELETE FROM reporting_stock_kg_line_history where reporting_id = %s;
        """%(self.id, self.id)
        self._cr.execute(query)



    # @api.multi
    def action_calculate_internal(self):
        date_opname = self.inventory_date
        date_start = " '%s 00:00:00' "%self.start_date
        date_end = " '%s 23:59:59' "%self.end_date
        where_product_category_id = " 1=1 "
        if self.product_category_id:
            where_product_category_id = " ppt.categ_id = %s "%self.product_category_id.id
        
        query = """
        -- BEGIN DETAIL
            insert into reporting_stock_kg_line (reporting_id, location_id, product_id, qty_start, qty_in, qty_out, return_in, return_out, adjustment_in, adjustment_out, qty_balance, penyesuaian) (
                select %s as reporting_id, location_id, product_id, sum(qty_start) as qty_start, sum(qty_in) as qty_in, sum(qty_out) as qty_out, sum(return_in) as return_in, sum(return_out) as return_out, 
                    sum(adjustment_in) as adjustment_in, sum(adjustment_out) as adjustment_out, 
                    (pp.diameter * pp.diameter * pp.variable * (sum(qty_start) + sum(qty_in) + sum(return_in) - sum(qty_out) - sum(return_out) + sum(adjustment_in) - sum(adjustment_out))/ 1000000) as qty_balance, 
                    (pp.diameter * pp.diameter * pp.variable * (sum(qty_start) + sum(qty_in) + sum(return_in) - sum(qty_out) - sum(return_out) + sum(adjustment_in) - sum(adjustment_out))/ 1000000) as penyesuaian
                from (
                    -- BEGIN SALDO AWAL
                    select row_number() OVER (), sil.location_id as location_id, sil.product_id as product_id, 
                    (pp.diameter * pp.diameter * pp.variable * sil.product_qty / 1000000) as qty_start, 
                    0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out 
                    from stock_inventory_line sil, product_product pp, product_template ppt where sil.product_id = pp.id and pp.product_tmpl_id = ppt.id and sil.inventory_id = %s and %s
                    union
                    select row_number() OVER () as id, location_id, product_id, sum(qty_start) + sum(qty_in) + sum(return_in) - sum(qty_out) - sum(return_out) + sum(adjustment_in) - sum(adjustment_out) as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out
                    from (
                        select row_number() OVER (), sml.location_dest_id as location_id, sml.product_id as product_id, 0 as qty_start, sml.qty_done as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out 
                        from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done > '%s' and sp.date_done < %s and sml.location_dest_id = %s and spt.return_type is null and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.location_id as location_id, sml.product_id as product_id, 0 as qty_start, 0 as qty_in, sml.qty_done as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out 
                        from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done > '%s' and sp.date_done < %s and sml.location_id = %s and spt.return_type is null and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.location_dest_id as location_id, sml.product_id as product_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, sml.qty_done as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out 
                        from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done > '%s' and sp.date_done < %s and sml.location_dest_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.location_id as location_id, sml.product_id as product_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, sml.qty_done as return_out, 0 as adjustment_in, 0 as adjustment_out 
                        from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done > '%s' and sp.date_done < %s and sml.location_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.location_dest_id as location_id, sml.product_id as product_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, sml.qty_done as adjustment_in, 0 as adjustment_out 
                        from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date > '%s' and sml.date < %s and sml.location_dest_id = %s and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.location_id as location_id, sml.product_id as product_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, sml.qty_done as adjustment_out 
                        from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date > '%s' and sml.date < %s and sml.location_id = %s and sm.state = 'done' and %s
                    ) as a group by location_id, product_id
                    -- END SALDO AWAL

                    -- Receipt
                    union
                    select row_number() OVER (), sml.location_dest_id as location_id, sml.product_id as product_id, 0 as qty_start, 
                    (pp.diameter * pp.diameter * pp.variable * sml.qty_done / 1000000) as qty_in, 
                    0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out 
                    from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_dest_id = %s and spt.return_type is null and sm.state = 'done' and %s

                    -- Release
                    union
                    select row_number() OVER (), sml.location_id as location_id, sml.product_id as product_id, 0 as qty_start, 0 as qty_in, 
                    (pp.diameter * pp.diameter * pp.variable * sml.qty_done / 1000000) as qty_out, 
                    0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out 
                    from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_id = %s and spt.return_type is null and sm.state = 'done' and %s

                    -- Release Manufacturing
                    union
                    select row_number() OVER (), sml.location_id as location_id, sml.product_id as product_id, 0 as qty_start, 0 as qty_in, 
                    (pp.diameter * pp.diameter * pp.variable * sml.qty_done / 1000000) as qty_out, 
                    0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out 
                    from stock_move_line sml, product_product pp, product_template ppt where sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sml.date >= %s and sml.date <= %s and sml.location_id = %s and sml.production_id is not null and %s


                    -- Retur In
                    union
                    select row_number() OVER (), sml.location_dest_id as location_id, sml.product_id as product_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 
                    (pp.diameter * pp.diameter * pp.variable * sml.qty_done / 1000000) as return_in, 
                    0 as return_out, 0 as adjustment_in, 0 as adjustment_out 
                    from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_dest_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s

                    -- Retur Out
                    union
                    select row_number() OVER (), sml.location_id as location_id, sml.product_id as product_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 
                    (pp.diameter * pp.diameter * pp.variable * sml.qty_done / 1000000) as return_out, 
                    0 as adjustment_in, 0 as adjustment_out 
                    from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s

                    -- Adjustment In
                    union
                    select row_number() OVER (), sml.location_dest_id as location_id, sml.product_id as product_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 
                    (pp.diameter * pp.diameter * pp.variable * sml.qty_done / 1000000) as adjustment_in, 
                    0 as adjustment_out 
                    from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date >= %s and sml.date <= %s and sml.location_dest_id = %s and sm.state = 'done' and %s

                    -- Adjustment Out
                    union
                    select row_number() OVER (), sml.location_id as location_id, sml.product_id as product_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 
                    (pp.diameter * pp.diameter * pp.variable * sml.qty_done / 1000000) as adjustment_out 
                    from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date >= %s and sml.date <= %s and sml.location_id = %s and sm.state = 'done' and %s
                ) as a left join product_product pp on product_id = pp.id group by location_id, product_id, pp.diameter, pp.variable order by product_id
            );
        -- END DETAIL

        -- BEGIN HISTORY IN
            insert into reporting_stock_kg_line_history (reporting_id, move_id, product_id, stock_type) (select %s as reporting_id, move_id, product_id, stock_type from (select row_number() OVER () as id, sm.id as move_id, pp.id as product_id, 'receipt' as stock_type 
            from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_dest_id = %s and spt.return_type is null and sm.state = 'done' and %s) as a group by product_id, move_id, stock_type order by product_id);

        -- BEGIN HISTORY OUT
            insert into reporting_stock_kg_line_history (reporting_id, move_id, product_id, stock_type) (select %s as reporting_id, move_id, product_id, stock_type from (select row_number() OVER () as id, sm.id as move_id, pp.id as product_id, 'release' as stock_type 
            from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_id = %s and spt.return_type is null and sm.state = 'done' and %s) as a group by product_id, move_id, stock_type order by product_id);

            insert into reporting_stock_kg_line_history (reporting_id, move_id, product_id, stock_type) (select %s as reporting_id, move_id, product_id, stock_type from (select row_number() OVER () as id, sm.id as move_id, pp.id as product_id, 'release' as stock_type 
            from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sml.date >= %s and sml.date <= %s and sml.location_id = %s and sml.production_id is not null and %s) as a group by product_id, move_id, stock_type order by product_id);

        -- BEGIN RETURN IN
            insert into reporting_stock_kg_line_history (reporting_id, move_id, product_id, stock_type) (select %s as reporting_id, move_id, product_id, stock_type from (select row_number() OVER () as id, sm.id as move_id, pp.id as product_id, 'return_in' as stock_type 
            from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_dest_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s) as a group by product_id, move_id, stock_type order by product_id);

        -- BEGIN RETURN OUT
            insert into reporting_stock_kg_line_history (reporting_id, move_id, product_id, stock_type) (select %s as reporting_id, move_id, product_id, stock_type from (select row_number() OVER () as id, sm.id as move_id, pp.id as product_id, 'return_out' as stock_type 
            from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s) as a group by product_id, move_id, stock_type order by product_id);

        -- BEGIN ADJUSTMENT IN
            insert into reporting_stock_kg_line_history (reporting_id, move_id, product_id, stock_type) (select %s as reporting_id, move_id, product_id, stock_type from (select row_number() OVER () as id, sm.id as move_id, pp.id as product_id, 'adjustment_in' as stock_type 
            from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date >= %s and sml.date <= %s and sml.location_dest_id = %s and sm.state = 'done' and %s) as a group by product_id, move_id, stock_type order by product_id);

        -- BEGIN ADJUSTMENT OUT
            insert into reporting_stock_kg_line_history (reporting_id, move_id, product_id, stock_type) (select %s as reporting_id, move_id, product_id, stock_type from (select row_number() OVER () as id, sm.id as move_id, pp.id as product_id, 'adjustment_out' as stock_type 
            from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date >= %s and sml.date <= %s and sml.location_id = %s and sm.state = 'done' and %s) as a group by product_id, move_id, stock_type order by product_id);

        DELETE FROM reporting_stock_kg_line where reporting_id = %s and qty_start = 0 and qty_in = 0 and qty_out = 0 and return_in = 0 and return_out = 0 and adjustment_in = 0 and adjustment_out = 0 and qty_balance = 0;
        """%(
            #head
            self.id, self.inventory_id.id, where_product_category_id,
            #saldo awal
            date_opname, date_start, self.location_id.id, where_product_category_id,
            date_opname, date_start, self.location_id.id, where_product_category_id,
            date_opname, date_start, self.location_id.id, where_product_category_id,
            date_opname, date_start, self.location_id.id, where_product_category_id,
            self.inventory_id.id, date_opname, date_start, self.location_id.id, where_product_category_id,
            self.inventory_id.id, date_opname, date_start, self.location_id.id, where_product_category_id,
            
            #detail
            date_start, date_end, self.location_id.id, where_product_category_id,
            date_start, date_end, self.location_id.id, where_product_category_id,
            date_start, date_end, self.location_id.id, where_product_category_id,
            date_start, date_end, self.location_id.id, where_product_category_id,
            date_start, date_end, self.location_id.id, where_product_category_id,
            self.inventory_id.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.inventory_id.id, date_start, date_end, self.location_id.id, where_product_category_id,
            
            #HISTORY IN
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, self.inventory_id.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, self.inventory_id.id, date_start, date_end, self.location_id.id, where_product_category_id,

            self.id
            )
        # print(query)
        # sdfnsldkfsnl
        self._cr.execute(query)
        for line in self.line_ids:
            line.update_reporting_line()



    def action_print_stock_opname(self):
        return self.env.ref('reporting.report_stock_opname_action').report_action(self)



    def action_download_data(self):
        return {
            'type'      : 'ir.actions.act_window',
            'name'      : "Reporting Stock",
            'res_model' : 'reporting.stock.xlsx',
            'target'    : 'new',
            'view_id'   : self.env.ref('reporting.reporting_stock_xlsx_view').id,
            'view_mode' : 'form',
        }



class ReportingStockKgLine(models.Model):
    _name = 'reporting.stock.kg.line'

    
    name                        = fields.Char(string='Name')
    product_code                = fields.Char(string='Kode Barang', related='product_id.default_code')
    variasi                     = fields.Char(string='Variasi', compute='_compute_variasi')
    categ_id                    = fields.Many2one('product.category', string="Product Category" , related='product_id.categ_id')
    uom_id                      = fields.Many2one('uom.uom', string="Uom", related='product_id.uom_id')
    location_id                 = fields.Many2one('stock.location', 'Location', domain=[('usage','=','internal')])
    reporting_id                = fields.Many2one('reporting.stock.kg', string='Reporting')
    picking_id                  = fields.Many2one('stock.picking', string='Picking',)
    product_id                  = fields.Many2one('product.product', string='Product',)
    hpp                         = fields.Float("HPP", related='product_id.standard_price')
    qty_start                   = fields.Float("Saldo Awal", digits=(16,4),)
    qty_in                      = fields.Float("Qty Terima", digits=(16,4),)
    qty_out                     = fields.Float("Qty Keluar", digits=(16,4),)
    return_in                   = fields.Float("Return Terima", digits=(16,4),)
    return_out                  = fields.Float("Return Keluar", digits=(16,4),)
    adjustment_in               = fields.Float("Penyesuaian Terima", digits=(16,4),)
    adjustment_out              = fields.Float("Penyesuaian Keluar", digits=(16,4),)
    qty_balance                 = fields.Float("Saldo Akhir", digits=(16,4),)
    penyesuaian                 = fields.Float("Penyesuaian", digits=(16,4))
    history_in_ids              = fields.One2many('reporting.stock.kg.line.history', 'reporting_line_id', string="History In", domain=[('stock_type', '=', 'receipt')])
    history_out_ids             = fields.One2many('reporting.stock.kg.line.history', 'reporting_line_id', string="History Out", domain=[('stock_type', '=', 'release')])
    history_return_in_ids       = fields.One2many('reporting.stock.kg.line.history', 'reporting_line_id', string="History Return In", domain=[('stock_type', '=', 'return_in')])
    history_return_out_ids      = fields.One2many('reporting.stock.kg.line.history', 'reporting_line_id', string="History Return Out", domain=[('stock_type', '=', 'return_out')])
    history_adjustment_in_ids   = fields.One2many('reporting.stock.kg.line.history', 'reporting_line_id', string="History Adjustment In", domain=[('stock_type', '=', 'adjustment_in')])
    history_adjustment_out_ids  = fields.One2many('reporting.stock.kg.line.history', 'reporting_line_id', string="History Adjustment Out", domain=[('stock_type', '=', 'adjustment_out')])
   

    def update_reporting_line(self):
        for rec in self:
            sql = " update reporting_stock_kg_line_history set reporting_line_id = %s WHERE reporting_id = %s and product_id = %s " % (rec.id, rec.reporting_id.id, rec.product_id.id)
            self._cr.execute(sql)

    def query_update_onhand(self):
        for rec in self:
            query = """ update stock_quant set quantity = %s where product_id = %s and location_id = %s """%(rec.qty_balance, rec.product_id.id, rec.reporting_id.location_id.id)
            self._cr.execute(query)

    def _compute_variasi(self):
        for rec in self:
            rec.variasi = rec.product_id.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.name == 'Variasi').name

class ReportingStockKgLineHistory(models.Model):
    _name = 'reporting.stock.kg.line.history'

    name                = fields.Char(string='Name')
    product_code        = fields.Char(string='Kode Barang', related='product_id.default_code')
    variasi             = fields.Char(string='Variasi', compute='_compute_variasi')
    qty                 = fields.Float(string='Quantity', related='move_id.product_uom_qty')
    date                = fields.Datetime(string='Date', related='picking_id.date_done')
    categ_id            = fields.Many2one('product.category', string="Product Category" , related='product_id.categ_id')
    reporting_id        = fields.Many2one('reporting.stock.kg', string='Reporting')
    reporting_line_id   = fields.Many2one('reporting.stock.kg.line', string='Reporting Line',)
    move_id             = fields.Many2one('stock.move', string='Stock Move')
    picking_id          = fields.Many2one('stock.picking', string="Stock Picking" , related='move_id.picking_id')
    product_id          = fields.Many2one('product.product', string='Product')
    uom_id              = fields.Many2one('uom.uom', string="Uom", related='move_id.product_uom')
    stock_type          = fields.Selection([("receipt","Receipt"),("release","Release"),("return_in","Return In"),("return_out","Return Out"),("adjustment_in","Adjustment In"),("adjustment_out","Adjustment Out")], string='Stock Type',)
    description         = fields.Text(string='Description', related='move_id.description_picking')

    def _compute_variasi(self):
        for rec in self:
            rec.variasi = rec.product_id.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.name == 'Variasi').name