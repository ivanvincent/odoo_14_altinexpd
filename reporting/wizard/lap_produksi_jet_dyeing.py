from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class LapProduksiJetDyeing(models.TransientModel):
    _name = 'lap_produksi.jet_dyeing'

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
                to_char(mp.date_planned_start, 'YYYY-mm-dd') as date,
                mp.process_type,
                mwc.name as workcenter,
                mp.name as no_mo,
                CASE
                    WHEN mwc.name <> 'DYEING' THEN mmw.name
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
                qty_meter_kp,
                mr.quantity_greige as qty_greige
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
            left join mrp_request mr on mp.mrp_request_id = mr.id
            
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
        return self.env.ref('reporting.action_lap_produksi_jet_dyeing').report_action(None, data=data)


class LapProduksiJetDyeing(models.AbstractModel):
    _name = 'report.reporting.lap_produksi_jet_dyeing'

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
        qty = (mo_obj.gramasi_kain_finish / 1000 * mo_obj.lebar_kain_finish / 100) * 0.9144 * mo_obj.mrp_request_id.quantity_greige
        return qty

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