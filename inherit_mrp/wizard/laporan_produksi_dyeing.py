from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class LaporanProduksiDyeing(models.TransientModel):
    _name = 'laporan.produksi.dyeing'

    date_start = fields.Date(string='Data Start', required=True,default=fields.Date.today())
    date_end = fields.Date(string='Data End', required=True,default=fields.Date.today())
    mrp_type_id = fields.Many2one('mrp.type', string='Type MRP')
    type = fields.Selection([("perhari","Perhari"),("permesin","PerMesin"),("pershift","PerShift"),("peroperator","PerOperator"),("perhari_workcenter","Perhari Workcenter"),("reproses","ReProses"),("reproduksi","ReProduksi"),("overtime","OverTime Schedule")], string='Type')

    def action_generate(self):
        date_start_tmp  = datetime.strptime(self.date_start.strftime('%Y-%m-%d') + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        date_start      = date_start_tmp - timedelta(hours=7)
        
        date_end_tmp    = datetime.strptime(self.date_end.strftime('%Y-%m-%d') + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        date_end        = date_end_tmp - timedelta(hours=7)
        
        if self.type == 'perhari':
            query = """
                SELECT 
                    mp.id as mo_id,
                    mp.name,                    
                    to_char(date_planned_start, 'YYYY-mm-dd') as date,
                    mp.product_id,
                    so.name as no_so,
                    qty_yard_kp,
                    qty_kg_kp,
                    qty_meter_kp
                FROM mrp_production as mp
                    LEFT JOIN sale_order as so
                    ON so.id = mp.sale_id
                where
                    type_id = 2
                    and date_planned_start between '%s' and '%s'
                order by 
                    date_planned_start desc
            """ % (self.date_start, self.date_end)
            self._cr.execute(query)
            result = self._cr.dictfetchall()

            data = {
                'me': self,
                'ids': self.ids,
                'model': self._name,
                'form': {
                    'date_start': self.date_start,
                    'date_end': self.date_end,
                    'data' : result,
                },
            }
            return self.env.ref('inherit_mrp.action_report_produksi_dyeing').report_action(None, data=data)
        elif self.type == 'permesin':
            query = """
                select 
                    mp.id as mo_id,              
                    to_char(mp.date_planned_start, 'YYYY-mm-dd') as date,
                    mp.process_type,
                    mwc.name as workcenter,
                    mp.name as no_mo,
                    CASE
                        WHEN mwc.name = 'DYEING' THEN mmw.name
                        ELSE mm.name
                    END as mesin,
                    mpr.name as no_program,
                    pav.name as warna,
                    mp.no_urut_labdip_final as no_urut,
                    pp.kelompok as kategori,
                    lw.state as status_resep,
                    lw.no_urut as no_urut,
                    mp.product_id,
                    pt.name as greige,
                    mp.greige_id,
                    so.name as no_so,
                    rp.name as pelanggan,
                    qty_yard_kp,
                    qty_kg_kp,
                    qty_meter_kp
                from
                    mrp_workorder as mw
                left join mrp_production as mp on mw.production_id = mp.id
                left join sale_order as so on mp.sale_id = so.id
                left join res_partner as rp on so.partner_id = rp.id
                left join mrp_workcenter as mwc on mw.workcenter_id = mwc.id
                left join mrp_machine as mm on mp.mesin_id = mm.id
                left join mrp_machine as mmw on mw.mesin_id = mmw.id
                left join product_product as pp on mp.product_id = pp.id
                left join product_attribute_value as pav on pp.warna_id = pav.id
                left join product_template as pt on pp.product_tmpl_id=pt.id
                left join labdip_warna lw on mp.labdip_warna_id = lw.id
                left join mrp_program mpr on mw.program_id = mpr.id
                where mp.date_planned_start between %s and %s and mwc.is_planning = True
                order by mm.id, mp.name
            """
            params = [date_start, date_end]
            self._cr.execute(query, params)
            result = self._cr.dictfetchall()

            data = {
                'me': self,
                'ids': self.ids,
                'model': self._name,
                'form': {
                    'date_start': self.date_start,
                    'date_end': self.date_end,
                    'data' : result,
                },
            }
            return self.env.ref('inherit_mrp.action_report_produksi_dyeing_permesin').report_action(None, data=data)
        elif self.type == 'perhari_workcenter':
            query = """
                select 
                    to_char(mp.date_planned_start, 'YYYY-mm-dd') as date,
                    mwc.name as workcenter,
                    mp.name as no_mo,
                    mm.name as mesin,
                    mp.product_id,
                    so.name as no_so,
                    qty_yard_kp,
                    qty_kg_kp,
                    qty_meter_kp
                from
                    mrp_workorder as mw
                left join mrp_production as mp
                    on mw.production_id = mp.id
                left join sale_order as so
                    on mp.sale_id = so.id
                left join mrp_workcenter as mwc
                    on mw.workcenter_id = mwc.id
                left join mrp_machine as mm
                    on mw.mesin_id = mm.id
                and mp.date_planned_start between '%s' and '%s'
                order by 
                    mp.date_planned_start desc
            """ % (self.date_start, self.date_end)
            self._cr.execute(query)
            result = self._cr.dictfetchall()

            data = {
                'me': self,
                'ids': self.ids,
                'model': self._name,
                'form': {
                    'date_start': self.date_start,
                    'date_end': self.date_end,
                    'data' : result,
                },
            }
            return self.env.ref('inherit_mrp.action_report_produksi_dyeing_workcenter').report_action(None, data=data)

class ReportProduksiDyeingPermesin(models.AbstractModel):
    _name = 'report.inherit_mrp.report_produksi_dyeing_permesin'

    @api.model
    def _get_report_values(self, docids, data=None):
        # print('_get_report_values')
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        docs = data['form']['data']
        return {
            'doc_ids': data['ids'],
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
            'doc_ids' : docids,
            'me': self,
            'list_mesin': self.list_mesin(docs)
        }
    
    @api.model
    def product_name(self, product_id):
        product_obj = self.env['product.product'].browse(product_id)
        return product_obj.display_name
    
    @api.model
    def get_prg(self, mo_id):
        mo_obj = self.env['mrp.production'].browse(mo_id)
        return mo_obj.program_ids

    @api.model
    def get_qty_kg(self, mo_id):
        mo_obj = self.env['mrp.production'].browse(mo_id)
        return mo_obj.qty_kg_kp

    def list_mesin(self, data):
        mesin = []
        for a in data:
            mesin.append(a.get('mesin'))
        return list(set(mesin))

    def list_date(self, data):
        date = []
        for a in data:
            date.append(a.get('date'))
        return list(set(date))
class ReportProduksiDyeing(models.AbstractModel):
    _name = 'report.inherit_mrp.report_laporan_produksi_dyeing'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('_get_report_values')
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        docs = data['form']['data']
        return {
            'doc_ids': data['ids'],
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
            'doc_ids' : docids,
            'me': self,
            'list_date': self.list_date(docs)
        }
    
    @api.model
    def product_name(self, product_id):
        product_obj = self.env['product.product'].browse(product_id)
        return product_obj.display_name
    
    @api.model
    def get_qty_mtr(self, mo_id):
        mo_obj = self.env['mrp.production'].browse(mo_id)
        return mo_obj.qty_meter_kp

    @api.model
    def get_qty_kg(self, mo_id):
        mo_obj = self.env['mrp.production'].browse(mo_id)
        return mo_obj.qty_kg_kp

    def list_date(self, data):
        date = []
        for a in data:
            date.append(a.get('date'))
        return list(set(date))
class ReportProduksiDyeingWorkcenter(models.AbstractModel):
    _name = 'report.inherit_mrp.report_laporan_produksi_dyeing_workcenter'

    @api.model
    def _get_report_values(self, docids, data=None):
        print('_get_report_values')
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        docs = data['form']['data']
        return {
            'doc_ids': data['ids'],
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
            'doc_ids' : docids,
            'me': self,
            'list_date': self.list_date(docs),
            'list_workcenter': self.list_workcenter(docs)
        }
    
    @api.model
    def product_name(self, product_id):
        product_obj = self.env['product.product'].browse(product_id)
        return product_obj.display_name

    @api.model
    def get_qty_mtr(self, mo_id):
        mo_obj = self.env['mrp.production'].browse(mo_id)
        return mo_obj.qty_meter_kp

    @api.model
    def get_qty_kg(self, mo_id):
        mo_obj = self.env['mrp.production'].browse(mo_id)
        return mo_obj.qty_kg_kp

    def list_date(self, data):
        date = []
        for a in data:
            date.append(a.get('date'))
        return list(set(date))
    
    def list_workcenter(self, data):
        workcenter = []
        for a in data:
            workcenter.append(a.get('workcenter'))
        return list(set(workcenter))