from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from io import BytesIO
import xlsxwriter
from . import add_workbook_format as awf
from datetime import datetime
import pytz
from pytz import timezone
import logging

_logger = logging.getLogger(__name__)

class ReportingStockLot(models.Model):
    _name = 'reporting.stock.lot'
    _rec_name = 'location_id'

    
    
    def get_default_date_multi(self):
        date_time = pytz.UTC.localize(datetime.now()).astimezone(timezone('Asia/Jakarta'))
        return date_time.strftime('%d/%m/%Y %H:%M:%S')

    def get_product_category(self):
        return [category.id  for warehouse in self.env.user.default_warehouse_ids for category in warehouse.product_category_ids ]

    name                        = fields.Char(string='Name')
    start_date                  = fields.Date('Start Date', default=datetime.now())
    end_date                    = fields.Date('End Date', default=datetime.now() )
    inventory_date              = fields.Datetime('Inventory Date', related='inventory_id.date')
    warehouse_id                = fields.Many2one('stock.warehouse', string='Warehouse')
    user_id                     = fields.Many2one('res.users', 'Created by', default=lambda self: self.env.user)
    inventory_id                = fields.Many2one('stock.inventory', string='Inventory Adjustment')
    location_id                 = fields.Many2one('stock.location', 'Location', domain=[('usage','=','internal')])
    product_category_id         = fields.Many2one('product.category', string='Product Category', domain=lambda self: [('id','in',self.get_product_category())],)
    line_ids                    = fields.One2many('reporting.stock.lot.line', 'reporting_id', 'Details', ondelete="cascade")
    history_ids                 = fields.One2many('reporting.stock.lot.line.history', 'reporting_id', string="History")
    history_in_id               = fields.One2many('reporting.stock.lot.line.history', 'reporting_id', string="History", domain=[('stock_type', '=', 'receipt')])
    history_out_id              = fields.One2many('reporting.stock.lot.line.history', 'reporting_id', string="History", domain=[('stock_type', '=', 'release')])
    history_return_in_id        = fields.One2many('reporting.stock.lot.line.history', 'reporting_id', string="History", domain=[('stock_type', '=', 'return_in')])
    history_return_out_id       = fields.One2many('reporting.stock.lot.line.history', 'reporting_id', string="History", domain=[('stock_type', '=', 'return_out')])
    history_adjustment_in_id    = fields.One2many('reporting.stock.lot.line.history', 'reporting_id', string="History", domain=[('stock_type', '=', 'adjustment_in')])
    history_adjustment_out_id   = fields.One2many('reporting.stock.lot.line.history', 'reporting_id', string="History", domain=[('stock_type', '=', 'adjustment_out')])
    lot_ids                     = fields.One2many('list.lot', 'reporting_id', 'List Lot')
    rack_ids                    = fields.Many2many(comodel_name='master.rack', string='Rack')
    
    data                        = fields.Binary(string='Image')


    def action_calculate(self):
        if self.warehouse_id.group_reporting == 'greige':
            self.action_delete_reporting()
            self.action_calculate_greige()
            self.action_insert_list_lot()
        elif self.warehouse_id.group_reporting == 'benang':
            self.action_delete_reporting()
            self.action_calculate_benang()

    def action_delete_reporting(self):
        query = """
            DELETE FROM reporting_stock_lot_line where reporting_id = %s;

            DELETE FROM reporting_stock_lot_line_history where reporting_id = %s;

            DELETE FROM list_lot where reporting_id = %s;
        """%(self.id, self.id, self.id)
        self._cr.execute(query)
        return True

    def action_insert_list_lot(self):
        query = """
            insert into list_lot (reporting_id, product_code, product_id, lot_id, rack_id, grade_id, qty) (
                select 
                    %s as reporting_id, 
                    b.default_code as product_code,
                    b.id as product_id,
                    spl.id as lot_id, 
                    spl.rack_id as rack_id,
                    spl.grade_id as grade_id,
                    spl.qty as qty
                from stock_production_lot spl 
                left join product_product as b on spl.product_id = b.id
                where spl.location_id = %s
                and spl.rack_id in %s
                )
        """
        params = [
            self.id,
            self.location_id.id,
            tuple(self.rack_ids.ids) if self.rack_ids else (None,),
            ]
        # self._cr.execute(query, tuple(params))
        self.env.cr.execute(query, tuple(params))



    # @api.multi
    def action_calculate_greige(self):
        date_opname = self.inventory_date
        date_start = " '%s 00:00:00' "%self.start_date
        date_end = " '%s 23:59:59' "%self.end_date
        where_product_category_id = " 1=1 "
        if self.product_category_id:
            where_product_category_id = " ppt.categ_id = %s "%self.product_category_id.id

        query = """
        -- BEGIN DETAIL
            insert into reporting_stock_lot_line (reporting_id, product_id, grade_id, kelompok, qty_start, qty_in, qty_out, return_in, return_out, adjustment_in, adjustment_out, qty_balance) (
                select %s as reporting_id, product_id, grade_id, kelompok, sum(qty_start) as qty_start, sum(qty_in) as qty_in, sum(qty_out) as qty_out, sum(return_in) as return_in, sum(return_out) as return_out, sum(adjustment_in) as adjustment_in, sum(adjustment_out) as adjustment_out, sum(qty_start) + sum(qty_in) + sum(return_in) - sum(qty_out) - sum(return_out) + sum(adjustment_in) - sum(adjustment_out) as qty_balance
                from (
                    -- BEGIN SALDO AWAL
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.qty_done as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id = %s and %s
                    union
                    select row_number() OVER () as id, product_id, grade_id, kelompok, sum(qty_start) + sum(qty_in) + sum(return_in) - sum(qty_out) - sum(return_out) + sum(adjustment_in) - sum(adjustment_out) as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance
                    from (
                        select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, 0 as qty_start, sml.qty_done as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                        from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done > '%s' and sp.date_done < %s and sml.location_dest_id = %s and spt.return_type is null and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, 0 as qty_start, 0 as qty_in, sml.qty_done as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                        from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done > '%s' and sp.date_done < %s and sml.location_id = %s and spt.return_type is null and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, 0 as qty_start, 0 as qty_in, 0 as qty_out, sml.qty_done as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                        from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done > '%s' and sp.date_done < %s and sml.location_dest_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, sml.qty_done as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                        from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done > '%s' and sp.date_done < %s and sml.location_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, sml.qty_done as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                        from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date > '%s' and sml.date < %s and sml.location_dest_id = %s and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, sml.qty_done as adjustment_out, 0 as qty_balance 
                        from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date > '%s' and sml.date < %s and sml.location_id = %s and sm.state = 'done' and %s
                    ) as a group by product_id, grade_id, kelompok
                    -- END SALDO AWAL

                    -- Receipt
                    union
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, 0 as qty_start, sml.qty_done as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_dest_id = %s and spt.return_type is null and sm.state = 'done' and %s

                    -- Release
                    union
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, 0 as qty_start, 0 as qty_in, sml.qty_done as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_id = %s and spt.return_type is null and sm.state = 'done' and %s

                    -- Retur In
                    union
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, 0 as qty_start, 0 as qty_in, 0 as qty_out, sml.qty_done as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_dest_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s

                    -- Retur Out
                    union
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, sml.qty_done as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s

                    -- Adjustment In
                    union
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, sml.qty_done as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date >= %s and sml.date <= %s and sml.location_dest_id = %s and sm.state = 'done' and %s

                    -- Adjustment Out
                    union
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, sml.qty_done as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date >= %s and sml.date <= %s and sml.location_id = %s and sm.state = 'done' and %s
                ) as a group by product_id, grade_id, kelompok order by product_id, grade_id, kelompok
            );
        -- END DETAIL

        -- BEGIN HISTORY IN
            insert into reporting_stock_lot_line_history (reporting_id, move_line_id, move_id, picking_id, product_code, product_id, lot_id, grade_id, rack_id, qty, stock_type) (
                select %s as reporting_id, sml.id, sm.id, sm.picking_id, pp.default_code, pp.id, sml.lot_id, sml.grade_id, sml.rack_id, sml.qty_done, 'receipt' as stock_type 
                from stock_move_line sml
                left join stock_move sm on sml.move_id = sm.id
                left join stock_picking sp on sm.picking_id = sp.id
                left join stock_picking_type spt on sp.picking_type_id = spt.id
                left join product_product pp on sml.product_id = pp.id
                where sp.date_done >= %s and sp.date_done <= %s and sml.location_dest_id = %s and spt.return_type is null and sm.state = 'done' and %s);

        -- BEGIN HISTORY OUT
            insert into reporting_stock_lot_line_history (reporting_id, move_line_id, move_id, picking_id, product_code, product_id, lot_id, grade_id, rack_id, qty, stock_type) (
                select %s as reporting_id, sml.id, sm.id, sm.picking_id, pp.default_code, pp.id, sml.lot_id, sml.grade_id, sml.rack_id, sml.qty_done, 'release' as stock_type 
                from stock_move_line sml
                left join stock_move sm on sml.move_id = sm.id
                left join stock_picking sp on sm.picking_id = sp.id
                left join stock_picking_type spt on sp.picking_type_id = spt.id
                left join product_product pp on sml.product_id = pp.id
                where sp.date_done >= %s and sp.date_done <= %s and sml.location_id = %s and spt.return_type is null and sm.state = 'done' and %s);

        -- BEGIN RETURN IN
            insert into reporting_stock_lot_line_history (reporting_id, move_line_id, move_id, picking_id, product_code, product_id, lot_id, grade_id, rack_id, qty, stock_type) (
                select %s as reporting_id, sml.id, sm.id, sm.picking_id, pp.default_code, pp.id, sml.lot_id, sml.grade_id, sml.rack_id, sml.qty_done, 'return_in' as stock_type 
                from stock_move_line sml
                left join stock_move sm on sml.move_id = sm.id
                left join stock_picking sp on sm.picking_id = sp.id
                left join stock_picking_type spt on sp.picking_type_id = spt.id
                left join product_product pp on sml.product_id = pp.id
                where sp.date_done >= %s and sp.date_done <= %s and sml.location_dest_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s);

        -- BEGIN RETURN OUT
            insert into reporting_stock_lot_line_history (reporting_id, move_line_id, move_id, picking_id, product_code, product_id, lot_id, grade_id, rack_id, qty, stock_type) (
                select %s as reporting_id, sml.id, sm.id, sm.picking_id, pp.default_code, pp.id, sml.lot_id, sml.grade_id, sml.rack_id, sml.qty_done, 'return_out' as stock_type 
                from stock_move_line sml
                left join stock_move sm on sml.move_id = sm.id
                left join stock_picking sp on sm.picking_id = sp.id
                left join stock_picking_type spt on sp.picking_type_id = spt.id
                left join product_product pp on sml.product_id = pp.id
                where sp.date_done >= %s and sp.date_done <= %s and sml.location_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s);

        -- BEGIN ADJUSTMENT IN
            insert into reporting_stock_lot_line_history (reporting_id, picking_id, move_line_id, product_code, product_id, lot_id, grade_id, stock_type) (
                select %s as reporting_id, sm.picking_id as picking_id, sml.id as move_line_id, pp.default_code as product_code, sml.product_id as product_id, sml.lot_id as lot_id, sml.grade_id as grade_id, 'adjustment_in' as stock_type 
                from stock_move_line sml, stock_move sm, product_product pp
                where sml.move_id = sm.id and sml.product_id = pp.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date >= %s and sml.date <= %s and sml.location_dest_id = %s and sm.state = 'done' and %s);

        -- BEGIN ADJUSTMENT OUT
            insert into reporting_stock_lot_line_history (reporting_id, picking_id, move_line_id, product_code, product_id, lot_id, grade_id, stock_type) (
                select %s as reporting_id, sm.picking_id as picking_id, sml.id as move_line_id, pp.default_code as product_code, sml.product_id as product_id, sml.lot_id as lot_id, sml.grade_id as grade_id, 'adjustment_out' as stock_type 
                from stock_move_line sml, stock_move sm, product_product pp
                where sml.move_id = sm.id and sml.product_id = pp.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date >= %s and sml.date <= %s and sml.location_id = %s and sm.state = 'done' and %s);

        DELETE FROM reporting_stock_lot_line where reporting_id = %s and qty_start = 0 and qty_in = 0 and qty_out = 0 and return_in = 0 and return_out = 0 and adjustment_in = 0 and adjustment_out = 0 and qty_balance = 0;
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
            self.inventory_id.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.inventory_id.id, date_start, date_end, self.location_id.id, where_product_category_id,
            
            #HISTORY IN
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, self.inventory_id.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, self.inventory_id.id, date_start, date_end, self.location_id.id, where_product_category_id,

            self.id
            )
        self._cr.execute(query)
        for line in self.line_ids:
            line.update_reporting_line()



    def action_calculate_benang(self):
        date_opname = self.inventory_date
        date_start = " '%s 00:00:00' "%self.start_date
        date_end = " '%s 23:59:59' "%self.end_date
        where_product_category_id = " 1=1 "
        if self.product_category_id:
            where_product_category_id = " ppt.categ_id = %s "%self.product_category_id.id

        query = """
        -- BEGIN DETAIL
            insert into reporting_stock_lot_line (reporting_id, product_id, grade_id, kelompok, lot_id, qty_start, qty_in, qty_out, return_in, return_out, adjustment_in, adjustment_out, qty_balance) (
                select %s as reporting_id, product_id, grade_id, kelompok, lot_id, sum(qty_start) as qty_start, sum(qty_in) as qty_in, sum(qty_out) as qty_out, sum(return_in) as return_in, sum(return_out) as return_out, sum(adjustment_in) as adjustment_in, sum(adjustment_out) as adjustment_out, sum(qty_start) + sum(qty_in) + sum(return_in) - sum(qty_out) - sum(return_out) + sum(adjustment_in) - sum(adjustment_out) as qty_balance
                from (
                    -- BEGIN SALDO AWAL
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, sml.qty_done as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id = %s and %s
                    union
                    select row_number() OVER () as id, product_id, grade_id, kelompok, lot_id, sum(qty_start) + sum(qty_in) + sum(return_in) - sum(qty_out) - sum(return_out) + sum(adjustment_in) - sum(adjustment_out) as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance
                    from (
                        select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, 0 as qty_start, sml.qty_done as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                        from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done > '%s' and sp.date_done < %s and sml.location_dest_id = %s and spt.return_type is null and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, 0 as qty_start, 0 as qty_in, sml.qty_done as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                        from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done > '%s' and sp.date_done < %s and sml.location_id = %s and spt.return_type is null and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, sml.qty_done as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                        from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done > '%s' and sp.date_done < %s and sml.location_dest_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, sml.qty_done as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                        from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done > '%s' and sp.date_done < %s and sml.location_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, sml.qty_done as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                        from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date > '%s' and sml.date < %s and sml.location_dest_id = %s and sm.state = 'done' and %s
                        union
                        select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, sml.qty_done as adjustment_out, 0 as qty_balance 
                        from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date > '%s' and sml.date < %s and sml.location_id = %s and sm.state = 'done' and %s
                    ) as a group by product_id, grade_id, kelompok, lot_id
                    -- END SALDO AWAL

                    -- Receipt
                    union
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, 0 as qty_start, sml.qty_done as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_dest_id = %s and spt.return_type is null and sm.state = 'done' and %s

                    -- Release
                    union
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, 0 as qty_start, 0 as qty_in, sml.qty_done as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_id = %s and spt.return_type is null and sm.state = 'done' and %s

                    -- Retur In
                    union
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, sml.qty_done as return_in, 0 as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_dest_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s

                    -- Retur Out
                    union
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, sml.qty_done as return_out, 0 as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, stock_picking sp, product_product pp, product_template ppt, stock_picking_type spt where sml.move_id = sm.id and sm.picking_id = sp.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.picking_type_id = spt.id and sp.date_done >= %s and sp.date_done <= %s and sml.location_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s

                    -- Adjustment In
                    union
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, sml.qty_done as adjustment_in, 0 as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date >= %s and sml.date <= %s and sml.location_dest_id = %s and sm.state = 'done' and %s

                    -- Adjustment Out
                    union
                    select row_number() OVER (), sml.product_id as product_id, sml.grade_id as grade_id, pp.kelompok as kelompok, sml.lot_id as lot_id, 0 as qty_start, 0 as qty_in, 0 as qty_out, 0 as return_in, 0 as return_out, 0 as adjustment_in, sml.qty_done as adjustment_out, 0 as qty_balance 
                    from stock_move_line sml, stock_move sm, product_product pp, product_template ppt where sml.move_id = sm.id and sml.product_id = pp.id and pp.product_tmpl_id = ppt.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date >= %s and sml.date <= %s and sml.location_id = %s and sm.state = 'done' and %s
                ) as a 
                group by product_id, grade_id, kelompok, lot_id 
                order by product_id, grade_id, kelompok, lot_id
            );
        -- END DETAIL

        -- BEGIN HISTORY IN
            insert into reporting_stock_lot_line_history (reporting_id, move_line_id, move_id, picking_id, product_code, product_id, lot_id, grade_id, rack_id, qty, stock_type) (
                select %s as reporting_id, sml.id, sm.id, sm.picking_id, pp.default_code, pp.id, sml.lot_id, sml.grade_id, sml.rack_id, sml.qty_done, 'receipt' as stock_type 
                from stock_move_line sml
                left join stock_move sm on sml.move_id = sm.id
                left join stock_picking sp on sm.picking_id = sp.id
                left join stock_picking_type spt on sp.picking_type_id = spt.id
                left join product_product pp on sml.product_id = pp.id
                where sp.date_done >= %s and sp.date_done <= %s and sml.location_dest_id = %s and spt.return_type is null and sm.state = 'done' and %s);

        -- BEGIN HISTORY OUT
            insert into reporting_stock_lot_line_history (reporting_id, move_line_id, move_id, picking_id, product_code, product_id, lot_id, grade_id, rack_id, qty, stock_type) (
                select %s as reporting_id, sml.id, sm.id, sm.picking_id, pp.default_code, pp.id, sml.lot_id, sml.grade_id, sml.rack_id, sml.qty_done, 'release' as stock_type 
                from stock_move_line sml
                left join stock_move sm on sml.move_id = sm.id
                left join stock_picking sp on sm.picking_id = sp.id
                left join stock_picking_type spt on sp.picking_type_id = spt.id
                left join product_product pp on sml.product_id = pp.id
                where sp.date_done >= %s and sp.date_done <= %s and sml.location_id = %s and spt.return_type is null and sm.state = 'done' and %s);

        -- BEGIN RETURN IN
            insert into reporting_stock_lot_line_history (reporting_id, move_line_id, move_id, picking_id, product_code, product_id, lot_id, grade_id, rack_id, qty, stock_type) (
                select %s as reporting_id, sml.id, sm.id, sm.picking_id, pp.default_code, pp.id, sml.lot_id, sml.grade_id, sml.rack_id, sml.qty_done, 'return_in' as stock_type 
                from stock_move_line sml
                left join stock_move sm on sml.move_id = sm.id
                left join stock_picking sp on sm.picking_id = sp.id
                left join stock_picking_type spt on sp.picking_type_id = spt.id
                left join product_product pp on sml.product_id = pp.id
                where sp.date_done >= %s and sp.date_done <= %s and sml.location_dest_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s);

        -- BEGIN RETURN OUT
            insert into reporting_stock_lot_line_history (reporting_id, move_line_id, move_id, picking_id, product_code, product_id, lot_id, grade_id, rack_id, qty, stock_type) (
                select %s as reporting_id, sml.id, sm.id, sm.picking_id, pp.default_code, pp.id, sml.lot_id, sml.grade_id, sml.rack_id, sml.qty_done, 'return_out' as stock_type 
                from stock_move_line sml
                left join stock_move sm on sml.move_id = sm.id
                left join stock_picking sp on sm.picking_id = sp.id
                left join stock_picking_type spt on sp.picking_type_id = spt.id
                left join product_product pp on sml.product_id = pp.id
                where sp.date_done >= %s and sp.date_done <= %s and sml.location_id = %s and spt.return_type in ('return_out','return_in') and sm.state = 'done' and %s);

        -- BEGIN ADJUSTMENT IN
            insert into reporting_stock_lot_line_history (reporting_id, picking_id, move_line_id, product_code, product_id, lot_id, grade_id, stock_type) (
                select %s as reporting_id, sm.picking_id as picking_id, sml.id as move_line_id, pp.default_code as product_code, sml.product_id as product_id, sml.lot_id as lot_id, sml.grade_id as grade_id, 'adjustment_in' as stock_type 
                from stock_move_line sml, stock_move sm, product_product pp
                where sml.move_id = sm.id and sml.product_id = pp.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date >= %s and sml.date <= %s and sml.location_dest_id = %s and sm.state = 'done' and %s);

        -- BEGIN ADJUSTMENT OUT
            insert into reporting_stock_lot_line_history (reporting_id, picking_id, move_line_id, product_code, product_id, lot_id, grade_id, stock_type) (
                select %s as reporting_id, sm.picking_id as picking_id, sml.id as move_line_id, pp.default_code as product_code, sml.product_id as product_id, sml.lot_id as lot_id, sml.grade_id as grade_id, 'adjustment_out' as stock_type 
                from stock_move_line sml, stock_move sm, product_product pp
                where sml.move_id = sm.id and sml.product_id = pp.id and sm.inventory_id is not null and sm.inventory_id <> %s and sml.date >= %s and sml.date <= %s and sml.location_id = %s and sm.state = 'done' and %s);

        DELETE FROM reporting_stock_lot_line where reporting_id = %s and qty_start = 0 and qty_in = 0 and qty_out = 0 and return_in = 0 and return_out = 0 and adjustment_in = 0 and adjustment_out = 0 and qty_balance = 0;
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
            self.inventory_id.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.inventory_id.id, date_start, date_end, self.location_id.id, where_product_category_id,
            
            #HISTORY IN
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, self.inventory_id.id, date_start, date_end, self.location_id.id, where_product_category_id,
            self.id, self.inventory_id.id, date_start, date_end, self.location_id.id, where_product_category_id,

            self.id
            )
        self._cr.execute(query)
        for line in self.line_ids:
            line.update_reporting_line()


    def action_print(self):
        return {
            'type'      : 'ir.actions.act_window',
            'name'      : "Print",
            'res_model' : 'print.reporting_stock_lot.wizard',
            'target'    : 'new',
            'view_id'   : self.env.ref('reporting.print_reporting_stock_lot_wizard_form').id,
            'view_mode' : 'form',
            'context'   : {'default_reporting_id': self.id,},
        }

    
    def group_by_print_laporan_penerimaan_kain_grey(self):
        query = """
            select 
                a.code as code, 
                a.product as product, 
                a.roll as roll, 
                a.qty as qty,
                b.roll as x_roll,
                b.qty as x_qty
            from (
                select
                    a.product_code as code,
                    a.product_id as id_product,
                    c.name as product,
                    count(*) as roll,
                    sum(a.qty) as qty
                from reporting_stock_lot_line_history as a
                left join product_product as b on a.product_id = b.id
                left join product_template as c on b.product_tmpl_id = c.id
                left join makloon_grade as d on a.grade_id = d.id
                where a.reporting_id = %s and a.stock_type = 'receipt' and d.name <> 'X'
                group by a.product_code, a.product_id, c.name
            ) as a
            left join (
                select
                    a.product_code as code,
                    a.product_id as id_product,
                    c.name as product,
                    count(*) as roll,
                    sum(a.qty) as qty
                from reporting_stock_lot_line_history as a
                left join product_product as b on a.product_id = b.id
                left join product_template as c on b.product_tmpl_id = c.id
                left join makloon_grade as d on a.grade_id = d.id
                where a.reporting_id = %s and a.stock_type = 'receipt' and d.name = 'X'
                group by a.product_code, a.product_id, c.name
            ) as b on a.id_product = b.id_product
        """ % (self.id,self.id)
        self._cr.execute(query)
        res = self._cr.dictfetchall()
        return res

    def group_by_kelompok(self):
        query = """
            select 
                kelompok as kelompok
            from reporting_stock_lot_line
            where reporting_id = %s 
            group by kelompok
        """% (self.id)
        self._cr.execute(query)
        res = self._cr.dictfetchall()
        return res

    def group_by_rack(self):
        query = """
            select 
                a.rack_id as rack_id, 
                b.name as rack_name 
            from list_lot as a 
            left join master_rack b on a.rack_id = b.id
            where reporting_id = %s 
            group by a.rack_id, b.name
        """% (self.id)
        self._cr.execute(query)
        res = self._cr.dictfetchall()
        return res

    def group_by_rack_product_grade(self):
        query = """
            select 
                a.rack_id as rack_id,
                a.product_id as product_id,
                a.grade_id as grade_id,
                
                a.product_code as product_code,
                c.name as product_name,
                d.name as grade_name,
                sum(a.qty) as qty,
                count(*) as roll
            from list_lot a
            left join product_product b on a.product_id = b.id
            left join product_template c on b.product_tmpl_id = c.id
            left join makloon_grade d on a.grade_id = d.id
            where reporting_id = %s 
            group by a.rack_id, a.product_id, a.grade_id, a.product_code, c.name, d.name
            """% (self.id)
        self._cr.execute(query)
        res = self._cr.dictfetchall()
        return res

    def laporan_kain_lama(self):
        query = """
            select 
                count(*) as roll,
                c.default_code as code,
                c.name as name,
                sum(a.qty) as qty
            from stock_production_lot as a 
            left join product_product as b on a.product_id = b.id
            left join product_template as c on b.product_tmpl_id = c.id
            where a.product_age > 180 and location_id = %s
            group by c.default_code, c.name 
            order by c.name
        """% (self.location_id.id)
        self._cr.execute(query)
        res = self._cr.dictfetchall()
        return res

    def action_export_xlsx(self):
        fp = BytesIO()
        date_string = datetime.now().strftime("%Y-%m-%d")
        workbook = xlsxwriter.Workbook(fp)
        wbf, workbook = awf.add_workbook_format(workbook)

        # WKS 1
        report_name = 'REPORTING STOCK LOT %s' % (self.location_id.name)
        
        worksheet = workbook.add_worksheet(report_name)
        
        worksheet.set_column('A3:A3', 3)
        worksheet.set_column('B3:B3', 14)
        worksheet.set_column('C3:C3', 15)
        worksheet.set_column('D3:D3', 35)
        worksheet.set_column('E3:E3', 15)
        worksheet.set_column('F3:F3', 10)
        worksheet.set_column('G3:G3', 35)
        worksheet.set_column('H3:H3', 15)
        worksheet.set_column('I3:I3', 10)
        worksheet.set_column('J3:J3', 10)
        worksheet.set_column('K3:K3', 10)
        worksheet.set_column('L3:L3', 10)
        worksheet.set_column('M3:M3', 10)
        worksheet.set_column('N3:N3', 10)
        worksheet.set_column('O3:O3', 10)
        worksheet.set_column('P3:P3', 10)
        worksheet.set_column('Q3:Q3', 10)
        # WKS 1

        worksheet.merge_range('A1:Q2', report_name + ' PERIODE ' + '(' + str(self.start_date) + ' - ' + str(self.end_date) + ')' , wbf['format_judul'])

        row = 3
        worksheet.write('A%s' % (row), 'NO', wbf['header'])
        worksheet.write('B%s' % (row), 'KELOMPOK', wbf['header'])
        worksheet.write('C%s' % (row), 'PRODUCT CATEGORY', wbf['header'])
        worksheet.write('D%s' % (row), 'KODE BARANG', wbf['header'])
        worksheet.write('E%s' % (row), 'PRODUCT', wbf['header'])
        worksheet.write('F%s' % (row), 'GRADE', wbf['header'])
        worksheet.write('G%s' % (row), 'VARIASI', wbf['header'])
        worksheet.write('H%s' % (row), 'LOT', wbf['header'])
        worksheet.write('I%s' % (row), 'UOM', wbf['header'])
        worksheet.write('J%s' % (row), 'START', wbf['header'])
        worksheet.write('K%s' % (row), 'QTY IN', wbf['header'])
        worksheet.write('L%s' % (row), 'QTY OUT', wbf['header'])
        worksheet.write('M%s' % (row), 'RETURN IN', wbf['header'])
        worksheet.write('N%s' % (row), 'RETURN OUT', wbf['header'])
        worksheet.write('O%s' % (row), 'ADJUSTMENT IN', wbf['header'])
        worksheet.write('P%s' % (row), 'ADJUSTMENT OUT', wbf['header'])
        worksheet.write('Q%s' % (row), 'BALANCE', wbf['header'])

        row += 1
        
        no = 1

        for rec in self.line_ids:
            worksheet.write('A%s' % (row), no, wbf['content_center'])
            worksheet.write('B%s' % (row), rec.kelompok or '', wbf['content_center'])
            worksheet.write('C%s' % (row), rec.categ_id.name or '', wbf['content_center'])
            worksheet.write('D%s' % (row), rec.product_code or '', wbf['content_center'])
            worksheet.write('E%s' % (row), rec.product_id.name or '', wbf['content_center'])
            worksheet.write('F%s' % (row), rec.grade_id.name or '', wbf['content_center'])
            worksheet.write('G%s' % (row), rec.variasi or '', wbf['content_center'])
            worksheet.write('H%s' % (row), rec.lot_id.name or '', wbf['content_center'])
            worksheet.write('I%s' % (row), rec.uom_id.name or '', wbf['content_float'])
            worksheet.write('J%s' % (row), rec.qty_start or '', wbf['content_float'])
            worksheet.write('K%s' % (row), rec.qty_in or '', wbf['content_float'])
            worksheet.write('L%s' % (row), rec.qty_out or '', wbf['content_float'])
            worksheet.write('M%s' % (row), rec.return_in or '', wbf['content_float'])
            worksheet.write('N%s' % (row), rec.return_out or '', wbf['content_float'])
            worksheet.write('O%s' % (row), rec.adjustment_in or '', wbf['content_float'])
            worksheet.write('P%s' % (row), rec.adjustment_out or '', wbf['content_float'])
            worksheet.write('Q%s' % (row), rec.qty_balance or '', wbf['content_float'])
            no += 1
            row += 1


        filename = '%s %s%s' % (report_name, date_string, '.xlsx')
        workbook.close()
        out = base64.encodestring(fp.getvalue())
        self.write({'data': out})
        fp.close()

        self.write({'data': out})
        url = "web/content/?model=" + self._name + "&id=" + str(self.id) + "&field=data&download=true&filename=" + filename
        result = {
            'name'      : 'Laporan XLSX',
            'type'      : 'ir.actions.act_url',
            'url'       : url,
            'target'    : 'download',
        }
        return result

class ReportingStockLotLine(models.Model):
    _name = 'reporting.stock.lot.line'

    name                        = fields.Char(string='Name')
    product_code                = fields.Char(string='Kode Barang', related='product_id.default_code')
    variasi                     = fields.Char(string='Variasi', compute='_compute_variasi')
    kelompok                    = fields.Char(string='Kelompok',)
    ref                         = fields.Char(string='Ref', related='lot_id.ref')
    categ_id                    = fields.Many2one('product.category', string="Product Category" , related='product_id.categ_id')
    uom_id                      = fields.Many2one('uom.uom', string="Uom", related='product_id.uom_id')
    location_id                 = fields.Many2one('stock.location', 'Location', domain=[('usage','=','internal')])
    reporting_id                = fields.Many2one('reporting.stock.lot', string='Reporting')
    picking_id                  = fields.Many2one('stock.picking', string='Picking',)
    product_id                  = fields.Many2one('product.product', string='Product',)
    grade_id                    = fields.Many2one('makloon.grade', string='Grade')
    lot_id                      = fields.Many2one('stock.production.lot', string='Lot')
    hpp                         = fields.Float("HPP", related='product_id.standard_price')
    qty_start                   = fields.Float("Start", digits=(16,4),)
    qty_in                      = fields.Float("Qty In", digits=(16,4),)
    qty_out                     = fields.Float("Qty Out", digits=(16,4),)
    return_in                   = fields.Float("Return In", digits=(16,4),)
    return_out                  = fields.Float("Return Out", digits=(16,4),)
    adjustment_in               = fields.Float("Adjustment In", digits=(16,4),)
    adjustment_out              = fields.Float("Adjustment Out", digits=(16,4),)
    qty_balance                 = fields.Float("Balance", digits=(16,4),)
    history_in_ids              = fields.One2many('reporting.stock.lot.line.history', 'reporting_line_id', string="History In", domain=[('stock_type', '=', 'receipt')])
    history_out_ids             = fields.One2many('reporting.stock.lot.line.history', 'reporting_line_id', string="History Out", domain=[('stock_type', '=', 'release')])
    history_return_in_ids       = fields.One2many('reporting.stock.lot.line.history', 'reporting_line_id', string="History Return In", domain=[('stock_type', '=', 'return_in')])
    history_return_out_ids      = fields.One2many('reporting.stock.lot.line.history', 'reporting_line_id', string="History Return Out", domain=[('stock_type', '=', 'return_out')])
    history_adjustment_in_ids   = fields.One2many('reporting.stock.lot.line.history', 'reporting_line_id', string="History Adjustment In", domain=[('stock_type', '=', 'adjustment_in')])
    history_adjustment_out_ids  = fields.One2many('reporting.stock.lot.line.history', 'reporting_line_id', string="History Adjustment Out", domain=[('stock_type', '=', 'adjustment_out')])


    def update_reporting_line(self):
        for rec in self:
            sql = " update reporting_stock_lot_line_history set reporting_line_id = %s where reporting_id = %s and product_id = %s " % (rec.id, rec.reporting_id.id, rec.product_id.id)
            self._cr.execute(sql)

    def query_update_onhand(self):
        for rec in self:
            query = """ update stock_quant set quantity = %s where product_id = %s and location_id = %s """%(rec.qty_balance, rec.product_id.id, rec.reporting_id.location_id.id)
            self._cr.execute(query)

    def _compute_variasi(self):
        for rec in self:
            rec.variasi = rec.product_id.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.name == 'Variasi').name

class ReportingStockLotLineHistory(models.Model):
    _name = 'reporting.stock.lot.line.history'

    name                = fields.Char(string='Name')
    product_code        = fields.Char(string='Kode Barang')
    variasi             = fields.Char(string='Variasi', compute='_compute_variasi')
    qty                 = fields.Float(string='Quantity')
    date                = fields.Datetime(string='Date', related='picking_id.date_done')
    categ_id            = fields.Many2one('product.category', string="Product Category" , related='product_id.categ_id')
    reporting_id        = fields.Many2one('reporting.stock.lot', string='Reporting')
    reporting_line_id   = fields.Many2one('reporting.stock.lot.line', string='Reporting Line',)
    move_line_id        = fields.Many2one('stock.move.line', string='Stock Move Live')
    move_id             = fields.Many2one('stock.move', string='Stock Move')
    picking_id          = fields.Many2one('stock.picking', string="Stock Picking")
    product_id          = fields.Many2one('product.product', string='Product')
    lot_id              = fields.Many2one('stock.production.lot', string='Lot')
    grade_id            = fields.Many2one('makloon.grade', string='Grade')
    rack_id             = fields.Many2one('master.rack', string='Rack')
    uom_id              = fields.Many2one('uom.uom', string="Uom", related='move_id.product_uom')
    stock_type          = fields.Selection([("receipt","Receipt"),("release","Release"),("return_in","Return In"),("return_out","Return Out"),("adjustment_in","Adjustment In"),("adjustment_out","Adjustment Out")], string='Stock Type',)
    description         = fields.Text(string='Description', related='move_id.description_picking')

    def _compute_variasi(self):
        for rec in self:
            rec.variasi = rec.product_id.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.name == 'Variasi').name


class ListLot(models.Model):
    _name = 'list.lot'

    name            = fields.Char(string='Name')
    product_code    = fields.Char(string='Product Code')
    qty             = fields.Float(string='Qty')
    product_id      = fields.Many2one('product.product', string='Product')
    lot_id          = fields.Many2one('stock.production.lot', string='Lot')
    rack_id         = fields.Many2one('master.rack', string='Rack')
    grade_id        = fields.Many2one('makloon.grade', string='Grade')
    reporting_id    = fields.Many2one('reporting.stock.lot', string='Reporting')