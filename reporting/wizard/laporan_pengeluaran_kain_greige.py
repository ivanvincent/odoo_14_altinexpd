from odoo import fields, models, api, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

class LapPengeluaranKainGreigeWizard(models.TransientModel):
    _name = 'lap_pengeluaran_kain_greige.wizard'

    
    location_id = fields.Many2one('stock.location', string='Location')
    date_start  = fields.Date('Start Date', default=datetime.now())
    date_end    = fields.Date('End Date', default=datetime.now() )
    
    def action_generate(self):
        date_start_tmp  = datetime.strptime(self.date_start.strftime('%Y-%m-%d') + ' 00:00:00', '%Y-%m-%d %H:%M:%S')
        date_start      = date_start_tmp - timedelta(hours=7)
        
        date_end_tmp    = datetime.strptime(self.date_end.strftime('%Y-%m-%d') + ' 23:59:59', '%Y-%m-%d %H:%M:%S')
        date_end        = date_end_tmp - timedelta(hours=7)

        where_location = " 1=1 "
        if self.location_id :
            where_location = " sp.location_id = %s "%self.location_id.id
        
        query = """
            select 
                a.code as code, 
                a.product as product, 
                a.roll as roll, 
                a.quantity as qty,
                b.roll as x_roll,
                b.quantity as x_qty
            from (
                select
                    pt.default_code as code,
                    pt.name as product,
                    pp.id as id_product,
                    count(*) as roll,
                    sum(sml.qty_done) as quantity
                from stock_move_line as sml
                join stock_move as sm on sml.move_id = sm.id
                join stock_picking as sp on sm.picking_id = sp.id
                join product_product as pp on sml.product_id = pp.id
                join product_template as pt on pp.product_tmpl_id = pt.id
                join makloon_grade as mg on sml.grade_id = mg.id
                where
                    sp.state = 'done' and
                    sp.date_done between %s and %s and
                    sp.picking_type_id in (select id from stock_picking_type where code = 'outgoing') and
                    """+ where_location +""" and
                    mg.name <> 'X'
                group by 
                    pt.default_code, pt.name, pp.id
            ) as a
            left join (
                select
                    pt.default_code as code,
                    pt.name as product,
                    pp.id as id_product,
                    count(*) as roll,
                    sum(sml.qty_done) as quantity
                from stock_move_line as sml
                join stock_move as sm on sml.move_id = sm.id
                join stock_picking as sp on sm.picking_id = sp.id
                join product_product as pp on sml.product_id = pp.id
                join product_template as pt on pp.product_tmpl_id = pt.id
                join makloon_grade as mg on sml.grade_id = mg.id
                join stock_location as a on sp.location_id = a.id
                join stock_location as b on sp.location_dest_id = b.id
                where
                    sp.state = 'done' and
                    sp.date_done between %s and %s and
                    b.usage <> 'internal' and
                    a.usage = 'internal' and
                    """+ where_location +""" and
                    mg.name = 'X'
                group by 
                    pt.default_code, pt.name, pp.id
            ) as b on a.id_product = b.id_product
        """
        params = [
            date_start, date_end, date_start, date_end
        ]
        self._cr.execute(query, params)
        res = self._cr.dictfetchall()
        data = {
            'me'    : self,
            'ids'   : self.ids,
            'model' : self._name,
            'form': {
                'date_start'    : self.date_start,
                'date_end'      : self.date_end,
                'location_id'   : self.location_id.name if self.location_id else '',
                'data'          : res,
            },
        }
        return self.env.ref('reporting.action_lap_pengeluaran_kain_greige_wizard').report_action(None, data=data)


class LapPengeluaranKainGreigeAbstract(models.AbstractModel):
    _name = 'report.reporting.lap_pengeluaran_kain_greige_wizard'
    
    @api.model
    def _get_report_values(self, docids, data=None):
        date_start  = data['form']['date_start']
        date_end    = data['form']['date_end']
        location_id = data['form']['location_id']
        docs        = data['form']['data']
        return {
            'date_start'    : date_start,
            'date_end'      : date_end,
            'location_id'   : location_id,
            'docs'          : docs,
        }