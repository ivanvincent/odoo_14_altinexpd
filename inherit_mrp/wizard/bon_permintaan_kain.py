from odoo import models, fields, api

class BonPermintaanKain(models.TransientModel):
    _name = 'bon.permintaan.kain'

    date_start = fields.Date(string='Date Start', default=fields.Date.today(), required=True, )
    date_end = fields.Date(string='Date End', default=fields.Date.today(), required=True, )

    def action_print(self):
        query = """
                    select
                        row_number() OVER () as no,
                        pp.default_code,
                        greige_id,
                        sale_id,
                        qty_yard_kp,
                        count(1) as partai,
                        (
                            qty_yard_kp * count(1)
                        )
                        as jumlah,
                        '' as ket 
                    from    
                        mrp_production mp 
                        join
                            product_product as pp 
                            on pp.id = mp.greige_id 
                    where
                        state = 'draft' 
                        and sale_id is not null 
                        and mp.date_planned_start between '%s' and '%s' 
                    group by
                        sale_id,
                        greige_id,
                        qty_yard_kp,
                        pp.default_code
                """ % (self.date_start, self.date_end)
        self._cr.execute(query)
        doc = self._cr.dictfetchall()
        print(doc)
        data = {
            'ids': self.ids,
            'model': self._name,
            'id': self.id,
            'form': {
                'data' : doc,
                'date_start': self.date_start,  
                'date_end': self.date_end
            },
        }
        return self.env.ref('inherit_mrp.action_report_bom_permintaan_kain').report_action(None, data=data)

class ReportBonPermintaanKain(models.Model):
    _name = 'report.inherit_mrp.report_bon_permintaan_kain'

    @api.model
    def _get_report_values(self, docids, data=None):
            product_obj = self.env['product.product']
            so_obj = self.env['sale.order']
            finish_data = []
            for a in data['form']['data']:
                finish_data.append({
                    'no': a.get('no', ),
                    'default_code': a.get('default_code', ''),
                    'greige_id': product_obj.browse(a.get('greige_id', '')).display_name,
                    'sale_id': so_obj.browse(a.get('sale_id', '')).name, 
                    'qty_yard_kp': a.get('qty_yard_kp', ''), 
                    'partai': a.get('partai', ''),
                    'jumlah': a.get('jumlah', ''), 
                    'ket': a.get('ket', ''),
                })
            return {
            'doc_ids': data['ids'],
            'date_start': data['form']['date_start'],
            'date_end': data['form']['date_end'],
            'today': fields.Date.today(),
            'docs': finish_data,
        }