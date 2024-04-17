from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ReportPoPerSupplier(models.Model):
    _name = 'report.po.supplier'

    name = fields.Char(string='Report')
    date_start = fields.Date(string='Date Start', default=fields.Date.today())
    date_end = fields.Date(string='Date End', default=fields.Date.today())
    user_id = fields.Many2one(
        'res.users', string='Responsible', default=lambda self: self.env.user.id)
    line_ids = fields.One2many(
        'report.po.supplier.line', 'report_id', string='Details')
    amount_total = fields.Float(
        string='Amount', compute="_get_amount_total", currency_field='currency_id')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', store=True,)

    def init(self):
        self.env.cr.execute("""
            create or replace function wibicon_pivot(
                out_table varchar, in_query varchar,
                key_cols varchar[], class_cols varchar[],
                value_e varchar, col_order varchar
            ) returns void as $$
                declare
                    in_table varchar;
                    col varchar;
                    ali varchar;
                    on_e varchar;
                    i integer;
                    rec record;
                    query varchar;
                    -- This is actually an array of arrays but postgres does not support an array of arrays type so we flatten it.
                    -- We could theoretically use the matrix feature but it's extremly cancerogenous and we would have to involve
                    -- custom aggrigates. For most intents and purposes postgres does not have a multi-dimensional array type.
                    clsc_cols text[] := array[]::text[];
                    n_clsc_cols integer;
                    n_class_cols integer;
                begin
                    in_table := quote_ident('__' || out_table || '_in');
                    execute ('create temp table ' || in_table || ' on commit drop as ' || in_query);
                    -- get ordered unique columns (column combinations)
                    query := 'select array[';
                    i := 0;
                    foreach col in array class_cols loop
                        if i > 0 then
                            query := query || ', ';
                        end if;
                        query := query || 'quote_literal(' || quote_ident(col) || ')';
                        i := i + 1;
                    end loop;
                    query := query || '] x from ' || in_table;
                    for j in 1..2 loop
                        if j = 1 then
                            query := query || ' group by ';
                        else
                            query := query || ' order by ';
                            if col_order is not null then
                                query := query || col_order || ' ';
                                exit;
                            end if;
                        end if;
                        i := 0;
                        foreach col in array class_cols loop
                            if i > 0 then
                                query := query || ', ';
                            end if;
                            query := query || quote_ident(col);
                            i := i + 1;
                        end loop;
                    end loop;
                    -- raise notice '%', query;
                    for rec in
                        execute query
                    loop
                        clsc_cols := array_cat(clsc_cols, rec.x);
                    end loop;
                    n_class_cols := array_length(class_cols, 1);
                    n_clsc_cols := array_length(clsc_cols, 1) / n_class_cols;
                    -- build target query
                    query := 'select ';
                    i := 0;
                    foreach col in array key_cols loop
                        if i > 0 then
                            query := query || ', ';
                        end if;
                        query := query || '_key.' || quote_ident(col) || ' ';
                        i := i + 1;
                    end loop;
                    for j in 1..n_clsc_cols loop
                        query := query || ', ';
                        col := '';
                        for k in 1..n_class_cols loop
                            if k > 1 then
                                col := col || ', ';
                            end if;
                            col := col || clsc_cols[(j - 1) * n_class_cols + k];
                        end loop;
                        ali := '_clsc_' || j::text;
                        query := query || '(' || replace(value_e, '#', ali) || ')' || ' as ' || quote_ident(col) || ' ';
                    end loop;
                    query := query || ' from (select distinct ';
                    i := 0;
                    foreach col in array key_cols loop
                        if i > 0 then
                            query := query || ', ';
                        end if;
                        query := query || quote_ident(col) || ' ';
                        i := i + 1;
                    end loop;
                    query := query || ' from ' || in_table || ') _key ';
                    for j in 1..n_clsc_cols loop
                        ali := '_clsc_' || j::text;
                        on_e := '';
                        i := 0;
                        foreach col in array key_cols loop
                            if i > 0 then
                                on_e := on_e || ' and ';
                            end if;
                            on_e := on_e || ali || '.' || quote_ident(col) || ' = _key.' || quote_ident(col) || ' ';
                            i := i + 1;
                        end loop;
                        for k in 1..n_class_cols loop
                            on_e := on_e || ' and ';
                            on_e := on_e || ali || '.' || quote_ident(class_cols[k]) || ' = ' || clsc_cols[(j - 1) * n_class_cols + k];
                        end loop;
                        query := query || 'left join ' || in_table || ' as ' || ali || ' on ' || on_e || ' ';
                    end loop;
                    -- raise notice '%', query;
                    execute ('create temp table ' || quote_ident(out_table) || ' on commit drop as ' || query);
                    -- cleanup temporary in_table before we return
                    execute ('drop table ' || in_table)
                    return;
                end;
                $$ language plpgsql volatile; """)

    def action_open_purchase_wizard(self):
      return {
          'type': 'ir.actions.act_window',
          'name': 'Preview Report',
          'res_model': 'purchase.report.wizard',
          'view_mode': 'form',
          'target': 'new',
      }
  

    def test_pivot(self):
        query = """
            --begin;
                select wibicon_pivot('test',
                    'select  
                    rp.name as partner_id,
                    pt.name as product_id,
                    sum(rpsh.price_total) as price_total
                    from report_po_supplier_history rpsh
                    left join product_product pp on rpsh.product_id = pp.id 
                    left join product_template pt on pp.product_tmpl_id = pt.id
                    left join report_po_supplier_line rpsl on rpsh.report_line_id = rpsl.id
                    left join res_partner rp on rpsl.partner_id = rp.id
                    where rpsh.report_id = %s group by pt.name,rp.name',array['product_id'],array['partner_id'],'#.price_total',null);
                select * from test;
            --end transaction
        """ % (self.id)

        self._cr.execute(query)
        results = self._cr.dictfetchall()
        return results

    @api.depends('line_ids')
    def _get_amount_total(self):
        for line in self:
            amount_total = sum(line.line_ids.mapped('amount'))
            line.amount_total = amount_total

    def action_clear(self):
        query = """ 
                DELETE FROM report_po_supplier_line WHERE report_id = %s ;
                DELETE FROM report_po_supplier_history WHERE report_id = %s ;
                """ % (self.id, self.id)
        self._cr.execute(query)

    def _group_by_history_product(self):
        query = """ 
                select 
                    pt.name as product_id,sum(price_total) as total
                from 
                    report_po_supplier_history rp
                left join product_product pp on rp.product_id = pp.id
                left join product_template pt on pp.product_tmpl_id = pt.id
                where rp.report_id = %s
                group by pt.name
            """ % (self.id)
        self._cr.execute(query)
        results = self._cr.dictfetchall()
        return results

    def _group_by_history_product_qty(self):
        query = """ 
                select 
                    pt.name as product_id,uu.name as product_uom_id ,sum(price_total) as total
                from 
                    report_po_supplier_history rp
                left join product_product pp on rp.product_id = pp.id
                left join product_template pt on pp.product_tmpl_id = pt.id
                left join uom_uom uu on pt.uom_id = uu.id
                where rp.report_id = %s
                group by pt.name ,uu.name
            """ % (self.id)
        self._cr.execute(query)
        results = self._cr.dictfetchall()
        return results

    def action_calculate(self):
        self.action_clear()

        query = """ 
            insert into report_po_supplier_line (
                report_id,partner_id,amount,company_id,currency_id)(
                select 
                    %s as report_id,po.partner_id as partner_id ,sum(po.amount) as amount, %s as company_id ,%s as currency_id
                from 
                    (
                        select 
                            po.partner_id ,pol.price_total as amount 
                        from 
                            purchase_order po 
                        left join purchase_order_line pol on pol.order_id = po.id
                        left join account_move_line aml on aml.purchase_line_id  = pol.id
                        left join account_move am on aml.move_id = am.id and am.move_type = 'in_invoice'
                        where 
                        po.state in ('purchase','done') 
                        and date(po.date_approve) between '%s' and '%s'
                        
                    ) as po
                group by po.partner_id);
                
                insert into report_po_supplier_history (report_id,product_id,partner_id,bill_id,purchase_id,label,product_uom_id,quantity,bill_qty,purchase_line_id)(
                        select %s as report_id,
                                product_id,
                                partner_id,
                                move_id,
                                po_id,
                                label,
                                uom_id,
                                sum(po_qty) as po_qty,
                                sum(bill_qty) as bill_qty,
                                pol_id
                            from (
                        select row_number() over (),
                            po.id as po_id,
                            pol.id as pol_id,
                            pol.product_id as product_id,
                            pol.product_uom as uom_id,
                            po.partner_id as partner_id,
                            am.id as move_id,
                            aml.name as label,
                            pol.product_qty as po_qty,
                            0 as bill_qty,
                            0 as price_total
                        from purchase_order po
                            left join purchase_order_line pol on pol.order_id = po.id
                            left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_order_line_id = pol.id
                            left join purchase_request_line prl on prpolr.purchase_request_line_id = prl.id
                            left join purchase_request pr on prl.request_id = pr.id
                            left join account_move_line aml on aml.purchase_line_id = pol.id
                            left join account_move am on aml.move_id = am.id
                            and am.move_type = 'in_invoice'
                        where po.state in ('purchase','done')
                            and date(po.date_approve) between '%s' and '%s'
                        union
                        select row_number() over (),
                            po.id as po_id,
                            pol.id as pol_id,
                            pol.product_id as product_id,
                            pol.product_uom as uom_id,
                            po.partner_id as partner_id,
                            am.id as move_id,
                            aml.name as label,
                            0 as po_qty,
                            aml.quantity as bill_qty,
                            0 as price_total
                        from purchase_order po
                            left join purchase_order_line pol on pol.order_id = po.id
                            left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_order_line_id = pol.id
                            left join purchase_request_line prl on prpolr.purchase_request_line_id = prl.id
                            left join purchase_request pr on prl.request_id = pr.id
                            left join account_move_line aml on aml.purchase_line_id = pol.id
                            left join account_move am on aml.move_id = am.id
                            and am.move_type = 'in_invoice'
                        where po.state in ('purchase','done')
                            and date(po.date_approve) between '%s' and '%s'
                        union
                        select row_number() over (),
                            po.id as po_id,
                            pol.id as pol_id,
                            pol.product_id as product_id,
                            pol.product_uom as uom_id,
                            po.partner_id as partner_id,
                            am.id as move_id,
                            aml.name as label,
                            0 as po_qty,
                            0 as bill_qty,
                            pol.price_total as price_total
                        from purchase_order po
                            left join purchase_order_line pol on pol.order_id = po.id
                            left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_order_line_id = pol.id
                            left join purchase_request_line prl on prpolr.purchase_request_line_id = prl.id
                            left join purchase_request pr on prl.request_id = pr.id
                            left join account_move_line aml on aml.purchase_line_id = pol.id
                            left join account_move am on aml.move_id = am.id
                            and am.move_type = 'in_invoice'
                        where po.state in ('purchase','done')
                            and date(po.date_approve) between '%s' and '%s'
                                ) as history
                            group by product_id,
                                partner_id,
                                move_id,
                                po_id,
                                pol_id,
                                label,
                                uom_id
                  
                )
            
            """ % (self.id, self.env.company.id, self.env.company.currency_id.id,
                    self.date_start, self.date_end, 
                    self.id, self.date_start, self.date_end,
                    self.date_start, self.date_end,
                    self.date_start, self.date_end,
                    )
        self._cr.execute(query)
        for line in self.line_ids:
            line.update_reporting_line()

    @api.model
    def get_data_pb_blm_proses(self):
        query = """
            select 
                pt.name as product,
                pr.name as pr_name,
                pr.date_start as tgl_minta,
                prl.product_qty as kuantitas,
                pol.product_uom_qty as k_dipesan,
                uu.name as satuan,
                'Menunggu' as keterangan
            from purchase_request_purchase_order_line_rel rel
                left join purchase_order_line pol on pol.id = rel.purchase_order_line_id
                left join purchase_request_line prl on prl.id = rel.purchase_request_line_id
                left join purchase_request pr on pr.id = prl.request_id
                left join product_product pp on pp.id = pol.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join uom_uom uu on uu.id = pol.product_uom
            where
                pr.date_start between '%s' and '%s'
                and pol.state = 'sent'
        """ % (self.date_start, self.date_end)
        self._cr.execute(query)
        results = self._cr.dictfetchall()
        list_product = []
        for rec in results:
            list_product.append(rec.get('product'))
        data = []
        for product in list_product:
            data.append({
                'product': product,
                'detail' : sorted(list(filter(lambda x: x["product"] == product, results)), key=lambda x: x["product"], reverse=False)
            })
        print('====data====', data)
        return data
    


class ReportPoPerSupplierLine(models.Model):
    _name = 'report.po.supplier.line'

    report_id = fields.Many2one('report.po.supplier', string='Report')
    partner_id = fields.Many2one('res.partner', string='Partner')
    amount = fields.Monetary(string='Amount', currency_field='currency_id')
    company_id = fields.Many2one(
        'res.company', default=lambda self: self.env.company)
    currency_id = fields.Many2one(
        'res.currency', related='company_id.currency_id', store=True,)
    company_currency_id = fields.Many2one(related='company_id.currency_id', string='Company Currency',
                                          readonly=True, store=True, help='Utility field to express amount currency')
    history_ids = fields.One2many(
        'report.po.supplier.history', 'report_line_id', string='History', store=True,)

    def update_reporting_line(self):
        for rec in self:
            sql = " update report_po_supplier_history set report_line_id = %s , currency_id = '%s' where report_id = %s and partner_id = %s  " % (
                rec.id, rec.env.company.currency_id.id, rec.report_id.id, rec.partner_id.id)
            self._cr.execute(sql)


class ReportPoPerSupplierHistory(models.Model):
    _name = 'report.po.supplier.history'

    report_id = fields.Many2one('report.po.supplier', string='Report')
    report_line_id = fields.Many2one('report.po.supplier.line', string='Report Line')
    purchase_line_id = fields.Many2one( 'purchase.order.line', string='Purchase Order line')
    purchase_id = fields.Many2one('purchase.order', string='Purchase Order',)
    partner_id = fields.Many2one( string='Partner',)
    bill_id = fields.Many2one('account.move', string='Bill')
    bill_qty = fields.Float(string='Bill Qty')
    label = fields.Char(string='Label')
    product_id = fields.Many2one('product.product', string='Product')
    product_uom_id = fields.Many2one('uom.uom', string='Uom')
    quantity = fields.Float(string='Quantity')
    price_unit = fields.Float(related='purchase_line_id.price_unit', string='Price')
    price_subtotal = fields.Monetary(related='purchase_line_id.price_subtotal', string='SubTotal')
    price_tax = fields.Float(related='purchase_line_id.price_tax', string='Tax')
    price_total = fields.Monetary( related='purchase_line_id.price_total', string='Total',)
    currency_id = fields.Many2one(related='purchase_id.currency_id',  string='Currency', readonly=True)

    def _group_by_purchase_order(self, product_id):
        query = """ 
                select 
                    am.name as bill,date(po.date_approve) as date_approve,sum(rp.quantity) as quantity,sum(pol.price_total) as total,uu.name as product_uom_id
                from 
                    report_po_supplier_history rp
                left join product_product pp on rp.product_id = pp.id
                left join product_template pt on pp.product_tmpl_id = pt.id
                left join purchase_order po on rp.purchase_id = po.id
                left join purchase_order_line pol on pol.order_id = po.id
                left join uom_uom uu on pt.uom_id = uu.id
                left join stock_move sm on sm.purchase_line_id = pol.id
                left join account_move_line aml on aml.purchase_line_id  = pol.id
                left join account_move am on aml.move_id = am.id
                where rp.report_id = %s and rp.product_id = %s
                group by po.name ,uu.name ,po.date_approve,am.name
            """ % (self.report_id.id, product_id)
        self._cr.execute(query)
        results = self._cr.dictfetchall()
        import logging
        _logger = logging.getLogger(__name__)
        _logger.warning('='*40)
        _logger.warning(query)
        _logger.warning('='*40)
        return results
