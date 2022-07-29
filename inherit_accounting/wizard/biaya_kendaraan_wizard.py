from odoo import fields, models, api, _
from odoo.exceptions import UserError

class BiayaKendaraanWizard(models.TransientModel):
    _name = 'biaya.kendaraan.wizard'

    date_start = fields.Date(string='Date Start', required=True, )
    date_end = fields.Date(string='Date End', required=True, )
    is_global = fields.Boolean(string='Global ?')

    def query(self):
        return """
            select 
                row_number() OVER() AS id,
                sw.name as stock_point,
                a.vehicle_id,
                fv.name as vehicle, 
                a.date, 
                a.name, 
                a.origin, 
                pt.name as product, 
                b.product_uom_qty, 
                b.price_unit,
                fv.warehouse_id
            from 
                stock_picking a 
                join stock_move b on a.id = b.picking_id 
                left join fleet_vehicle fv on fv.id = a.vehicle_id
                left join product_product pp on pp.id = b.product_id
                left join product_template pt on pt.id = pp.product_tmpl_id
                left join stock_warehouse sw on sw.id = fv.warehouse_id
            where 
                a.vehicle_id is not null
                and a.state = 'done'
                and a.date between '%s' and '%s'
        """ % (self.date_start, self.date_end)
    
    def query_data_global(self):
        return """
            select 
                row_number() OVER() AS id,
                fv.warehouse_id,
                fv.model_id,
                fv.license_plate,
                sum(b.product_uom_qty) as product_uom_qty, 
                sum(b.price_unit) as price_unit
            from 
                stock_picking a 
                join stock_move b on a.id = b.picking_id 
                left join fleet_vehicle fv on fv.id = a.vehicle_id
                left join stock_warehouse sw on sw.id = fv.warehouse_id
            where 
                a.vehicle_id is not null
                and a.state = 'done'
                and a.date between '%s' and '%s'
            group by 
                fv.warehouse_id, fv.model_id, fv.license_plate
        """ % (self.date_start, self.date_end)
    
    
    def generate_view(self):
        if self.is_global:
            query  = """
                CREATE OR REPLACE VIEW biaya_kendaraan_global_view AS (%s)
            """ % (self.query_data_global())
            self._cr.execute(query)
            return self.env.ref('inherit_accounting.biaya_kendaraan_global_view_action').read()[0]
        else:
            query  = """
                CREATE OR REPLACE VIEW biaya_kendaraan_view AS (%s)
            """ % (self.query())
            self._cr.execute(query)
            return self.env.ref('inherit_accounting.biaya_kendaraan_view_action').read()[0]
        

    def generate_pdf(self):
        self._cr.execute(self.query())
        result = self._cr.dictfetchall()
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'date_start': self.date_start,
                'date_end': self.date_end,
                'data' : result,
            },
        }
        return self.env.ref('inherit_accounting.action_report_biaya_kendaraan').report_action(None, data=data)

    def generate_xlsx(self):
        ""

class BiayaKendaraanView(models.Model):
    _name = 'biaya.kendaraan.view'
    _auto = False

    warehouse_id = fields.Many2one('stock.warehouse', string='Stock Point', 
        # related='vehicle_id.warehouse_id', store=True,
    )
    vehicle = fields.Char(string='Vehicle')
    vehicle_id = fields.Many2one('fleet.vehicle', string='Vehicle',)
    model_id = fields.Many2one('fleet.vehicle.model', string='Model', related='vehicle_id.model_id', store=False,)
    license_plate = fields.Char(string='License Plate', related='vehicle_id.license_plate', store=False,)
    date = fields.Date(string='Date')
    name = fields.Char(string='No Picking')
    origin = fields.Char(string='Source Document')
    product = fields.Char(string='Product')
    product_uom_qty = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Price Unit')

class BiayaKendaraanGlobalView(models.Model):
    _name = 'biaya.kendaraan.global.view'
    _auto = False

    warehouse_id = fields.Many2one('stock.warehouse', string='Stock Point', )
    license_plate = fields.Char(string='License Plate',)
    model_id = fields.Many2one('fleet.vehicle.model', string='Model')
    product_uom_qty = fields.Float(string='Quantity')
    price_unit = fields.Float(string='Price Unit')

class BiayaKendaraanAbstract(models.AbstractModel):
    _name = 'report.inherit_accounting.report_biaya_kendaraan'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        docs = data['form']['data']
        return {
            'doc_ids': data['ids'],
            'date_start': date_start,
            'date_end': date_end,
            'docs': docs,
            'doc_ids' : docids,
        }