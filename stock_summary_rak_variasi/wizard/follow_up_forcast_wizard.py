from odoo import models, fields, api

class NamaModel(models.TransientModel):
    _name = 'follow.up.forcast.wizard'

    start_date = fields.Datetime(string='Start Date')
    end_date   = fields.Datetime(string='End Date')

    def action_generate(self):
        print("=======action_generate")
        query = """ 
            CREATE OR REPLACE VIEW follow_up_forcast AS (
            SELECT row_number() OVER () as id,
            product_id,
            price_unit,
            qty as qty_forcast,
            qty_so,
            qty_do, 
            qty_inv,
            0 as qty_sale_order,  
            0 as qty_delivery,
            0 as qty_onhand,
            0 as qty_minim,
            0 as qty_mo,
            0 as qty_sisa,
            0 as qty_need, 
            default_code,
            part_no
            FROM sale_contract_line)
           """
        self._cr.execute(query)
        self._cr.commit()
        result = self.env.ref('stock_summary_rak_variasi.action_follow_up_action').read()[0]
        return result