from jinja2 import environmentfunction
from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class LapProduksiDyeing(models.TransientModel):
    _name = 'lap_produksi.dyeing'

    date_start = fields.Date(string='Data Start', required=True, default=fields.Date.today())
    date_end = fields.Date(string='Data End', required=True, default=fields.Date.today())
    
    
    def action_generate(self):
        date_start_tmp  = datetime.strptime(self.date_start.strftime('%Y-%m-%d') + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        date_start      = date_start_tmp - timedelta(hours=7)
        
        date_end_tmp    = datetime.strptime(self.date_end.strftime('%Y-%m-%d') + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        date_end        = date_end_tmp - timedelta(hours=7)
        
        query = """
            select
                mp.id as mo_id,
                mw.id as wo_id,
                mw.workcenter_id as workcenter_id,
                to_char(mp.date_planned_start, 'YYYY-mm-dd') as date,
                to_char(to_timestamp(mpr.duration), 'MI:SS') as duration,
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
                pct.name as process,
                pt.name as greige,
                so.name as no_so,
                mp.qty_yard_kp as qty_yard_kp,
                he.name as operator,
                mw.shift as shift,
                mw.date_planned_start as date_planned_start,
                mw.date_planned_finished as date_planned_finished,
                rp.name as pelanggan
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
            left join process_chemical_type pct on mp.chemical_process_type_id = pct.id
            left join hr_employee he on mw.employee_id = he.id
            where mp.date_planned_start between '%s' and '%s' 
			and mwc.is_planning = True
            order by mm.id, mp.name
        """ % (date_start, date_end)
        params = [date_start, date_end]
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
        return self.env.ref('reporting.action_lap_produksi_dyeing').report_action(None, data=data)


class LapProduksiDyeing(models.AbstractModel):
    _name = 'report.reporting.lap_produksi_dyeing'

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
    def get_qty_kg(self, mo_id):
        mo_obj = self.env['mrp.production'].browse(mo_id)
        return round(mo_obj.qty_kg_kp, 2)

    @api.model
    def convert_yard_to_kg(self, mo_id, qty_greige=0.0):
        production = self.env['mrp.production'].browse(mo_id)
        if production.gramasi_kain_finish and production.lebar_kain_finish:
            kg = (production.gramasi_kain_finish / 1000 * production.lebar_kain_finish / 100) * 0.9144 * qty_greige
            return kg
        else:
            return 0.0

    @api.model
    def get_qty_greige_sended(self, mo_id):
        print('get_qty_greige_sended')
        picking_obj = self.env['stock.picking'].search([('production_id', '=', mo_id), ('state', '=', 'done'), ('picking_type_id', '=', 604)])
        return round(sum([sp.move_ids_without_package.quantity_done for sp in picking_obj]), 2)

    @api.model
    def get_nozle(self, workcenter_id):
        mwp_obj = self.env['mrp.workorder.parameter'].search([('workorder_id','=',workcenter_id),('parameter_id','=',129)])
        return mwp_obj.no_urut

    def list_mesin(self, data):
        mesin = []
        for a in data:
            mesin.append(a.get('mesin'))
        return list(set(mesin))