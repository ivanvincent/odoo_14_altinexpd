from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.addons import decimal_precision as dp
from odoo.exceptions import Warning, ValidationError, UserError
import time
import pytz
from pytz import timezone
import logging
from odoo.osv import expression
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)

class TjSummaryRakVariasi(models.Model):
    _name = 'tj.summary.rak.variasi'
    _description = "Stock Summary Variasi"

    inventory_id = fields.Many2one('stock.inventory', string='Inventory Adjustment')
    date_start   = fields.Datetime("Start Date")
    date_end     = fields.Datetime("End Date", required=True, default=lambda *a: time.strftime("%Y-%m-%d"))
    location_id  = fields.Many2one('stock.location', 'Location', required=True,)
    stock_summary_line_2 = fields.One2many(comodel_name='tj.summary.rak.variasi.line', inverse_name='order_id', string="summary lines")
    date_opname = fields.Datetime(related='inventory_id.date', string="Date Opname")

    history_ids = fields.One2many('tj.summary.rak.variasi.line.history', 'order_in_id', string="History")
    history_in_id = fields.One2many('tj.summary.rak.variasi.line.history', 'order_in_id', string="History", domain=[('picking_id.picking_category.type','=','purchase')])
    history_return_in_id = fields.One2many('tj.summary.rak.variasi.line.history', 'order_in_id', string="History Return In", domain=[('picking_id.picking_category.type','in',['return_makloon','return_production'])])
    history_out_id = fields.One2many('tj.summary.rak.variasi.line.history', 'order_in_id', string="History Out", domain=[('picking_id.picking_category.type','in',['makloon','production'])])
    history_return_out_id = fields.One2many('tj.summary.rak.variasi.line.history', 'order_in_id', string="History Return Out", domain=[('picking_id.picking_category.type','=', 'return_purchase')])
    history_adj_id = fields.One2many('tj.summary.rak.variasi.line.history.adj', 'order_adj_id', string="History Adjust")

    # kelompok_id = fields.Many2one('tj.stock.variasi.kelompok', 'Kelompok')

    # @api.multi
    def name_get(self):
        res = []

        for record in self:

            displayName = '%s - %s[%s]'%(record.location_id.name,record.inventory_id.name,record.date_opname)
            res.append((record.id,displayName))

        return res


    # @api.multi
    def action_export(self):
        action = self.env.ref('vit_stock_card_pro.report_stock_xlsx_action')
        return {
            'name': action.name + ' In',
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'view_id' : action.view_id.id,
            'target': 'new',
            'res_model': action.res_model,
            'domain': [],
            'context': {'new_report':True}
        }


    # ORIGINAL CODE 13 NOPEMBER 2020
    # def action_calculate(self):

    #     id_inventory = self.inventory_id.id
    #     id_location = self.location_id.id
    #     date_opname = self.date_opname
    #     date_start = self.date_start
    #     date_end = self.date_end
    #     id_summary = self.id

    #     # kelompok_id = self.kelompok_id.id


    #     query1 = """
    #             DELETE FROM tj_summary_rak_variasi_line
    #     """
    #     self._cr.execute(query1)
    #     self._cr.commit()


    #     query = """

    #         select %s as order_id,
    #             rak_id,product_id,grade_id, variasi_id , product_uom_id,
    #             sum(saldo_awal_qty) as saldo_awal_qty, sum(saldo_awal_pcs) as saldo_awal_pcs, sum(terima_qty) as terima_qty, sum(terima_pcs) as terima_pcs, sum(retur_terima_qty) as retur_terima_qty, sum(retur_terima_pcs) as retur_terima_pcs, sum(keluar_qty) as keluar_qty, sum(keluar_pcs) as keluar_pcs, sum(retur_keluar_qty) as retur_keluar_qty, sum(retur_keluar_pcs) as retur_keluar_pcs, sum(adj_qty) as adj_qty, sum(adj_pcs) as adj_pcs,
    #             sum(saldo_awal_qty) + sum(terima_qty) + sum(retur_terima_qty) - sum(keluar_qty) - sum(retur_keluar_qty) + sum(adj_qty) as balance_qty,
    #             sum(saldo_awal_pcs) + sum(terima_pcs) + sum(retur_terima_pcs) - sum(keluar_pcs) - sum(retur_keluar_pcs) + sum(adj_pcs) as balance_pcs
    #             from (


    #             select b.id,b.product_id,b.grade_id,b.prod_lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,b.product_qty as saldo_awal_qty,1 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_inventory a , stock_inventory_line b where a.id=%s  and  a.id=b.inventory_id and b.location_id=%s
    #             union


    #             select row_number() OVER () as id,
    #             product_id,grade_id, lot_id,rak_id , variasi_id , product_uom_id,
    #             sum(saldo_awal_qty) + sum(terima_qty) + sum(retur_terima_qty) - sum(keluar_qty) - sum(retur_keluar_qty) + sum(adj_qty) as saldo_awal_qty,
    #             sum(saldo_awal_pcs) + sum(terima_pcs) + sum(retur_terima_pcs) - sum(keluar_pcs) - sum(retur_keluar_pcs) + sum(adj_pcs) as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs
    #             from (

    #             select c.id,b.product_id,b.grade_id,c.lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, c.qty as terima_qty,1 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_picking a , stock_pack_operation b, stock_pack_operation_lot c where a.min_date > '%s' and a.min_date < '%s'  and  a.id=b.picking_id and b.id=c.operation_id and a.location_dest_id=%s and a.state='done'
    #             union
    #             select c.id,b.product_id,b.grade_id,c.lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, c.qty as keluar_qty, 1 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_picking a , stock_pack_operation b, stock_pack_operation_lot c where a.min_date > '%s' and a.min_date < '%s'  and  a.id=b.picking_id and b.id=c.operation_id and a.location_id=%s and a.state='done'
    #             union
    #             select b.id,b.product_id,b.grade_id,b.prod_lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, b.product_qty as adj_qty, 1 as adj_pcs  from stock_inventory a , stock_inventory_line b where a.date > '%s' and a.date < '%s'  and  a.id=b.inventory_id and b.location_id=%s and a.state='done'
    #             ) as a group by product_id,grade_id, lot_id, rak_id, variasi_id , product_uom_id


    #             union
    #             select c.id,b.product_id,b.grade_id,c.lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, c.qty as terima_qty, 1 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_picking a left join stock_pack_operation b on a.id=b.picking_id left join stock_pack_operation_lot c on b.id=c.operation_id left join stock_picking_type d on a.picking_type_id=d.id where a.min_date >= '%s' and a.min_date <= '%s'  and a.location_dest_id=%s and a.state='done'
    #             union
    #             select c.id,b.product_id,b.grade_id,c.lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, c.qty as keluar_qty, 1 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_picking a left join stock_pack_operation b on a.id=b.picking_id left join stock_pack_operation_lot c on b.id=c.operation_id left join stock_picking_type d on a.picking_type_id=d.id where a.min_date >= '%s' and a.min_date <= '%s'  and a.location_id=%s and a.state='done'
    #             union
    #             select b.id,b.product_id,b.grade_id,b.prod_lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, b.product_qty as adj_qty, 1 as adj_pcs  from stock_inventory a , stock_inventory_line b where a.date > '%s' and a.date <= '%s'  and  a.id=b.inventory_id and b.location_id=%s and a.state='done'
    #             ) as a group by rak_id,product_id,grade_id, variasi_id , product_uom_id
                
    #         """%(id_summary,id_inventory,id_location,

    #             date_opname,date_start,id_location,
    #             date_opname,date_start,id_location,
    #             date_opname,date_start,id_location,

    #             date_start,date_end,id_location,
    #             date_start,date_end,id_location,
    #             date_start,date_end,id_location)

        

    #     self._cr.execute(query)
    #     for res in self.env.cr.fetchall():

    #         tmpKategori = None
    #         tmpJenis = None
    #         tmpDepId = None

    #         tmpGreigeCode = None
    #         tmpKontruksi = None
    #         tmpLebar = None

    #         tmpGramasi = None
    #         tmpPartnerId = None
    #         tmpPartnerCustId = None 

    #         if(kelompok_id!=False):                
                
    #             # -------------------- Filtering berdasarkan kelompok id 
    #             idKelompokVariasi = self.env['tj.stock.variasi'].search([('id','=',int(res[4]))]).kelompok_id.id
    #             if(int(kelompok_id)==int(idKelompokVariasi)):

    #                 variasiPool = self.env['tj.stock.variasi'].search([('id','=',int(res[4]))])
    #                 for rec in variasiPool:
                        
    #                     tmpKategori = None if(rec.kategori_id.id==False) else rec.kategori_id.id
    #                     tmpJenis = None if(rec.jenis_id.id==False) else rec.jenis_id.id
    #                     tmpDepId = None if(rec.dep_id.id==False) else rec.jenis_id.id

    #                     tmpGreigeCode = rec.code
    #                     tmpKontruksi = rec.kontruksi
    #                     tmpLebar = rec.lebar

    #                     tmpGramasi = rec.gramasi
    #                     tmpPartnerId = None if(rec.partner_id.id==False) else rec.partner_id.id
    #                     tmpPartnerCustId = None if(rec.partner_cust_id.id==False) else rec.partner_cust_id.id


    #                 queryInsert = '''
    #                     INSERT INTO tj_summary_rak_variasi_line
    #                     (order_id,rak_id,product_id,grade_id,variasi_id,product_uom_id,saldo_awal_qty,saldo_awal_pcs,terima_qty,terima_pcs,retur_terima_qty,retur_terima_pcs,keluar_qty,keluar_pcs,retur_keluar_qty,retur_keluar_pcs,adj_qty,adj_pcs,balance_qty,balance_pcs,kelompok_id,kategori_id,jenis_id,dep_id,greige_code,kontruksi,lebar,gramasi,partner_id,partner_cust_id)
    #                     VALUES
    #                     (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                    
    #                 '''
                    
    #                 params = [res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13],res[14],res[15],res[16],res[17],res[18],res[19],kelompok_id,tmpKategori,tmpJenis,tmpDepId,tmpGreigeCode,tmpKontruksi,tmpLebar,tmpGramasi,tmpPartnerId,tmpPartnerCustId] 
    #                 self.env.cr.execute(queryInsert,params)
    #             else:
    #                 continue
            
    #         else:

    #             # -------------- Data masuk semua


    #             variasiPool = self.env['tj.stock.variasi'].search([('id','=',int(res[4]))])
    #             for rec in variasiPool:
                    
    #                 tmpKategori = None if(rec.kategori_id.id==False) else rec.kategori_id.id
    #                 tmpJenis = None if(rec.jenis_id.id==False) else rec.jenis_id.id
    #                 tmpDepId = None if(rec.dep_id.id==False) else rec.jenis_id.id

    #                 tmpGreigeCode = rec.code
    #                 tmpKontruksi = rec.kontruksi
    #                 tmpLebar = rec.lebar

    #                 tmpGramasi = rec.gramasi
    #                 tmpPartnerId = None if(rec.partner_id.id==False) else rec.partner_id.id
    #                 tmpPartnerCustId = None if(rec.partner_cust_id.id==False) else rec.partner_cust_id.id


    #             queryInsert = '''
    #                 INSERT INTO tj_summary_rak_variasi_line
    #                 (order_id,rak_id,product_id,grade_id,variasi_id,product_uom_id,saldo_awal_qty,saldo_awal_pcs,terima_qty,terima_pcs,retur_terima_qty,retur_terima_pcs,keluar_qty,keluar_pcs,retur_keluar_qty,retur_keluar_pcs,adj_qty,adj_pcs,balance_qty,balance_pcs,kelompok_id,kategori_id,jenis_id,dep_id,greige_code,kontruksi,lebar,gramasi,partner_id,partner_cust_id)
    #                     VALUES
    #                     (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                   
    #             '''
    #             params = [res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13],res[14],res[15],res[16],res[17],res[18],res[19],kelompok_id,tmpKategori,tmpJenis,tmpDepId,tmpGreigeCode,tmpKontruksi,tmpLebar,tmpGramasi,tmpPartnerId,tmpPartnerCustId] 
    #             self.env.cr.execute(queryInsert,params)


    #     self.action_calculate_history()

    

    # ORIGINAL CODE 13 NOPEMBER 2020
#     def action_calculate_history(self):
        
#         # values = []
#         id_inventory = self.inventory_id.id
#         id_location = self.location_id.id
#         date_opname = self.date_opname
#         date_start = self.date_start
#         date_end = self.date_end
#         id_summary = self.id

#         # kelompok_id = self.kelompok_id.id

#         query1 = """
#                 DELETE FROM tj_summary_rak_variasi_line_history;
#                 DELETE FROM tj_summary_rak_variasi_line_history_adj;
#         """
#         self._cr.execute(query1)
#         self._cr.commit()
        

#         queryHistory = """
#             select %s as order_in_id, a.id as picking_id,a.min_date,a.partner_id,a.location_id,a.location_dest_id,d.id as picking_category,b.product_id,b.grade_id,c.lot_id,b.rak_id,b.variasi_id,b.product_uom_id,c.qty,1 as pcs from stock_picking a , stock_pack_operation b, stock_pack_operation_lot c, makloon_picking_category d where a.picking_category=d.id and  a.min_date >= '%s' and a.min_date <= '%s'  and  a.id=b.picking_id and b.id=c.operation_id and (a.location_dest_id=%s or a.location_id=%s) and a.state='done'
#         """%(id_summary,date_start,date_end,id_location,id_location)

# # ---- Filtering berdasarkan kelompok id

#         self._cr.execute(queryHistory)
#         for res in self.env.cr.fetchall():
#             if(kelompok_id!=False) and res[11]!=None:                
#                 idKelompokVariasi = self.env['tj.stock.variasi'].search([('id','=',int(res[11]))]).kelompok_id.id
#                 if(int(kelompok_id)==int(idKelompokVariasi)):
#                     queryInsert = '''
#                         INSERT INTO tj_summary_rak_variasi_line_history
#                         (order_in_id,picking_id,min_date,partner_id,location_id,location_dest_id,picking_category,product_id,grade_id,lot_id,rak_id,variasi_id,product_uom_id,qty,pcs)
#                         VALUES
#                         (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                    
#                     '''
#                     params = [res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13],res[14]] 
#                     self.env.cr.execute(queryInsert,params)
#                 else:
#                     continue
#             else:                
#                 queryInsert = '''
#                     INSERT INTO tj_summary_rak_variasi_line_history
#                     (order_in_id,picking_id,min_date,partner_id,location_id,location_dest_id,picking_category,product_id,grade_id,lot_id,rak_id,variasi_id,product_uom_id,qty,pcs)
#                     VALUES
#                     (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                    
#                 '''
#                 params = [res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13],res[14]] 
#                 self.env.cr.execute(queryInsert,params)

#                 # --- Masuk semua data






#         queryHistoryAdj = """
#             select %s as order_in_id, a.id as inventory_id,a.date,b.partner_id,b.location_id,b.location_dest_id,b.product_id,b.grade_id,b.restrict_lot_id,b.rak_id,b.variasi_id,b.product_uom,b.product_qty,1 as pcs from stock_inventory a , stock_move b where a.date >= '%s' and a.date <= '%s'  and  a.id=b.inventory_id and (b.location_dest_id=%s or b.location_id=%s) and b.state='done'
#         """%(id_summary,date_start,date_end,id_location,id_location)


#         self._cr.execute(queryHistoryAdj)
#         for res in self.env.cr.fetchall():

#             if(kelompok_id!=False):
#                 # ---- Filtering berdasarkan kelompok id
#                 idKelompokVariasi = self.env['tj.stock.variasi'].search([('id','=',int(res[10]))]).kelompok_id.id
#                 if(int(kelompok_id)==int(idKelompokVariasi)):
#                     queryInsert = '''
#                         INSERT INTO tj_summary_rak_variasi_line_history_adj
#                         (order_adj_id,inventory_id,min_date,partner_id,location_id,location_dest_id,product_id,grade_id,lot_id,rak_id,variasi_id,product_uom_id,qty,pcs)
#                         VALUES
#                         (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                    
#                     '''
#                     params = [res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13]] 
#                     self.env.cr.execute(queryInsert,params)
#                 else:
#                     continue
#             else:

#                 # --- Masuk semua data
#                 queryInsert = '''
#                         INSERT INTO tj_summary_rak_variasi_line_history_adj
#                         (order_adj_id,inventory_id,min_date,partner_id,location_id,location_dest_id,product_id,grade_id,lot_id,rak_id,variasi_id,product_uom_id,qty,pcs)
#                         VALUES
#                         (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                    
#                     '''
#                 params = [res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13]] 
#                 self.env.cr.execute(queryInsert,params)












#     def action_calculate(self):

#         id_inventory = self.inventory_id.id
#         id_location = self.location_id.id
#         date_opname = self.date_opname
#         date_start = self.date_start
#         date_end = self.date_end
#         id_summary = self.id

#         kelompok_id = self.kelompok_id.id


#         query1 = """
#                 DELETE FROM tj_summary_rak_variasi_line
#         """
#         self._cr.execute(query1)
#         self._cr.commit()


#         query = """

#             select %s as order_id,
#                 rak_id,product_id,grade_id, variasi_id , product_uom_id,
#                 sum(saldo_awal_qty) as saldo_awal_qty, sum(saldo_awal_pcs) as saldo_awal_pcs, sum(terima_qty) as terima_qty, sum(terima_pcs) as terima_pcs, sum(retur_terima_qty) as retur_terima_qty, sum(retur_terima_pcs) as retur_terima_pcs, sum(keluar_qty) as keluar_qty, sum(keluar_pcs) as keluar_pcs, sum(retur_keluar_qty) as retur_keluar_qty, sum(retur_keluar_pcs) as retur_keluar_pcs, sum(adj_qty) as adj_qty, sum(adj_pcs) as adj_pcs,
#                 sum(saldo_awal_qty) + sum(terima_qty) + sum(retur_terima_qty) - sum(keluar_qty) - sum(retur_keluar_qty) + sum(adj_qty) as balance_qty,
#                 sum(saldo_awal_pcs) + sum(terima_pcs) + sum(retur_terima_pcs) - sum(keluar_pcs) - sum(retur_keluar_pcs) + sum(adj_pcs) as balance_pcs
#                 from (


#                 select b.id,b.product_id,b.grade_id,b.prod_lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,b.product_qty as saldo_awal_qty,1 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_inventory a , stock_inventory_line b where a.id=%s  and  a.id=b.inventory_id and b.location_id=%s
#                 union


#                 select row_number() OVER () as id,
#                 product_id,grade_id, lot_id,rak_id , variasi_id , product_uom_id,
#                 sum(saldo_awal_qty) + sum(terima_qty) + sum(retur_terima_qty) - sum(keluar_qty) - sum(retur_keluar_qty) + sum(adj_qty) as saldo_awal_qty,
#                 sum(saldo_awal_pcs) + sum(terima_pcs) + sum(retur_terima_pcs) - sum(keluar_pcs) - sum(retur_keluar_pcs) + sum(adj_pcs) as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs
#                 from (

#                 select c.id,b.product_id,b.grade_id,c.lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, c.qty as terima_qty,1 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_picking a , stock_pack_operation b, stock_pack_operation_lot c where a.min_date > '%s' and a.min_date < '%s'  and  a.id=b.picking_id and b.id=c.operation_id and a.location_dest_id=%s and a.state='done'
#                 union
#                 select c.id,b.product_id,b.grade_id,c.lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, c.qty as keluar_qty, 1 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_picking a , stock_pack_operation b, stock_pack_operation_lot c where a.min_date > '%s' and a.min_date < '%s'  and  a.id=b.picking_id and b.id=c.operation_id and a.location_id=%s and a.state='done'
#                 union
#                 select b.id,b.product_id,b.grade_id,b.prod_lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, b.product_qty as adj_qty, 1 as adj_pcs  from stock_inventory a , stock_inventory_line b where a.date > '%s' and a.date < '%s'  and  a.id=b.inventory_id and b.location_id=%s and a.state='done'
#                 ) as a group by product_id,grade_id, lot_id, rak_id, variasi_id , product_uom_id


#                 union
#                 select c.id,b.product_id,b.grade_id,c.lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, c.qty as terima_qty, 1 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_picking a left join stock_pack_operation b on a.id=b.picking_id left join stock_pack_operation_lot c on b.id=c.operation_id left join stock_picking_type d on a.picking_type_id=d.id where a.min_date >= '%s' and a.min_date <= '%s'  and a.location_dest_id=%s and a.state='done'
#                 union
#                 select c.id,b.product_id,b.grade_id,c.lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, c.qty as keluar_qty, 1 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_picking a left join stock_pack_operation b on a.id=b.picking_id left join stock_pack_operation_lot c on b.id=c.operation_id left join stock_picking_type d on a.picking_type_id=d.id where a.min_date >= '%s' and a.min_date <= '%s'  and a.location_id=%s and a.state='done'
#                 union
#                 select b.id,b.product_id,b.grade_id,b.prod_lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, b.product_qty as adj_qty, 1 as adj_pcs  from stock_inventory a , stock_inventory_line b where a.date > '%s' and a.date <= '%s'  and  a.id=b.inventory_id and b.location_id=%s and a.state='done'
#                 ) as a group by rak_id,product_id,grade_id, variasi_id , product_uom_id
                
#             """%(id_summary,id_inventory,id_location,

#                 date_opname,date_start,id_location,
#                 date_opname,date_start,id_location,
#                 date_opname,date_start,id_location,

#                 date_start,date_end,id_location,
#                 date_start,date_end,id_location,
#                 date_start,date_end,id_location)

        

#         self._cr.execute(query)
#         for res in self.env.cr.fetchall():

#             tmpKategori = None
#             tmpJenis = None
#             tmpDepId = None

#             tmpGreigeCode = None
#             tmpKontruksi = None
#             tmpLebar = None

#             tmpGramasi = None
#             tmpPartnerId = None
#             tmpPartnerCustId = None 

#             if(kelompok_id!=False):      


#                 # print " --> 0 ", res
#                 # print " ================================================ "
                 
                
#                 # -------------------- Filtering berdasarkan kelompok id 
#                 idKelompokVariasi = self.env['tj.stock.variasi'].search([('id','=',int(res[4]))]).kelompok_id.id
#                 if(int(kelompok_id)==int(idKelompokVariasi)):

#                     variasiPool = self.env['tj.stock.variasi'].search([('id','=',int(res[4]))])
#                     for rec in variasiPool:
                        
#                         tmpKategori = None if(rec.kategori_id.id==False) else rec.kategori_id.id
#                         tmpJenis = None if(rec.jenis_id.id==False) else rec.jenis_id.id
#                         tmpDepId = None if(rec.dep_id.id==False) else rec.jenis_id.id

#                         tmpGreigeCode = rec.code
#                         tmpKontruksi = rec.kontruksi
#                         tmpLebar = rec.lebar

#                         tmpGramasi = rec.gramasi
#                         tmpPartnerId = None if(rec.partner_id.id==False) else rec.partner_id.id
#                         tmpPartnerCustId = None if(rec.partner_cust_id.id==False) else rec.partner_cust_id.id

#                         print "Kat : ",tmpKategori
#                         print "Jenis : ",tmpJenis
#                         print "Dept : ",tmpDepId
#                         print "Greigco : ",tmpGreigeCode
#                         print "konstuksi : ",tmpKontruksi
#                         print "lebar : ",tmpLebar
#                         print "gramsi : ",tmpGramasi
#                         print "parnter : ",tmpPartnerId
#                         print "cust : ",tmpPartnerCustId
                        
                        


#                     queryInsert = '''
#                         INSERT INTO tj_summary_rak_variasi_line
#                         (order_id,rak_id,product_id,grade_id,variasi_id,product_uom_id,saldo_awal_qty,saldo_awal_pcs,terima_qty,terima_pcs,retur_terima_qty,retur_terima_pcs,keluar_qty,keluar_pcs,retur_keluar_qty,retur_keluar_pcs,adj_qty,adj_pcs,balance_qty,balance_pcs,kelompok_id,kategori_id,jenis_id,dep_id,greige_code,kontruksi,lebar,gramasi,partner_id,partner_cust_id)
#                         VALUES
#                         (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                    
#                     '''
                    
#                     params = [res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13],res[14],res[15],res[16],res[17],res[18],res[19],kelompok_id,tmpKategori,tmpJenis,tmpDepId,tmpGreigeCode,tmpKontruksi,tmpLebar,tmpGramasi,tmpPartnerId,tmpPartnerCustId] 
#                     self.env.cr.execute(queryInsert,params)
#                 else:
#                     continue
            
#             else:

#                 # -------------- Data masuk semua


#                 variasiPool = self.env['tj.stock.variasi'].search([('id','=',int(res[4]))])
#                 for rec in variasiPool:
                    
#                     tmpKategori = None if(rec.kategori_id.id==False) else rec.kategori_id.id
#                     tmpJenis = None if(rec.jenis_id.id==False) else rec.jenis_id.id
#                     tmpDepId = None if(rec.dep_id.id==False) else rec.jenis_id.id

#                     tmpGreigeCode = rec.code
#                     tmpKontruksi = rec.kontruksi
#                     tmpLebar = rec.lebar

#                     tmpGramasi = rec.gramasi
#                     tmpPartnerId = None if(rec.partner_id.id==False) else rec.partner_id.id
#                     tmpPartnerCustId = None if(rec.partner_cust_id.id==False) else rec.partner_cust_id.id


#                 queryInsert = '''
#                     INSERT INTO tj_summary_rak_variasi_line
#                     (order_id,rak_id,product_id,grade_id,variasi_id,product_uom_id,saldo_awal_qty,saldo_awal_pcs,terima_qty,terima_pcs,retur_terima_qty,retur_terima_pcs,keluar_qty,keluar_pcs,retur_keluar_qty,retur_keluar_pcs,adj_qty,adj_pcs,balance_qty,balance_pcs,kelompok_id,kategori_id,jenis_id,dep_id,greige_code,kontruksi,lebar,gramasi,partner_id,partner_cust_id)
#                         VALUES
#                         (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                   
#                 '''
#                 params = [res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13],res[14],res[15],res[16],res[17],res[18],res[19],kelompok_id,tmpKategori,tmpJenis,tmpDepId,tmpGreigeCode,tmpKontruksi,tmpLebar,tmpGramasi,tmpPartnerId,tmpPartnerCustId] 
#                 self.env.cr.execute(queryInsert,params)


#         self.action_calculate_history()




#     def action_calculate_history(self):

#         print "----------------- MASUK FUNGSI INI ----------------------"
        
#         # values = []
#         id_inventory = self.inventory_id.id
#         id_location = self.location_id.id
#         date_opname = self.date_opname
#         date_start = self.date_start
#         date_end = self.date_end
#         id_summary = self.id

#         kelompok_id = self.kelompok_id.id

#         query1 = """
#                 DELETE FROM tj_summary_rak_variasi_line_history;
#                 DELETE FROM tj_summary_rak_variasi_line_history_adj;
#         """
#         self._cr.execute(query1)
#         self._cr.commit()
        

#         queryHistory = """
#             select %s as order_in_id, 
#             a.id as picking_id,
#             a.min_date,
#             a.partner_id,
#             a.location_id,
#             a.location_dest_id,
#             d.id as picking_category,
#             b.product_id,
#             b.grade_id,
#             c.lot_id,
#             b.rak_id,
#             b.variasi_id,
#             b.product_uom_id,
#             c.qty,
#             1 as pcs 
#             from 
#                 stock_picking a , stock_pack_operation b, stock_pack_operation_lot c, makloon_picking_category d 
#             where 
#                 a.picking_category=d.id 
#                 and  a.min_date >= '%s' 
#                 and a.min_date <= '%s'  
#                 and  a.id=b.picking_id 
#                 and b.id=c.operation_id 
#                 and (a.location_dest_id=%s or a.location_id=%s) 
#                 and a.state='done'
#         """%(id_summary,date_start,date_end,id_location,id_location)


#         print " AAAA ", id_summary
#         print " BBBB ", date_start
#         print " CCCC ", date_end
#         print " DDDD ", id_location
        

# # ---- Filtering berdasarkan kelompok id

#         self._cr.execute(queryHistory)
#         for res in self.env.cr.fetchall():
#             if(kelompok_id!=False) and res[11]!=None:                
#                 idKelompokVariasi = self.env['tj.stock.variasi'].search([('id','=',int(res[11]))]).kelompok_id.id
#                 if(int(kelompok_id)==int(idKelompokVariasi)):
#                     queryInsert = '''
#                         INSERT INTO tj_summary_rak_variasi_line_history
#                         (order_in_id,picking_id,min_date,partner_id,location_id,location_dest_id,picking_category,product_id,grade_id,lot_id,rak_id,variasi_id,product_uom_id,qty,pcs)
#                         VALUES
#                         (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                    
#                     '''

#                     print " 0 - ", res[0]
#                     print " 1 - ", res[1]
#                     print " 2 - ", res[2]
#                     print " 3 - ", res[3]
#                     print " 4 - ", res[4]
#                     print " 5 - ", res[5]
#                     print " 6 - ", res[6]
#                     print " 7 - ", res[7]
#                     print " 8 - ", res[8]
#                     print " 9 - ", res[9]
#                     print " 10 - ", res[10]
#                     print " 11 - ", res[11]
#                     print " 12 - ", res[12]
#                     print " 13 - ", res[13]
#                     print " 14 - ", res[14]
                    

#                     params = [res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13],res[14]] 
#                     self.env.cr.execute(queryInsert,params)
#                 else:
#                     continue
#             else:                
#                 queryInsert = '''
#                     INSERT INTO tj_summary_rak_variasi_line_history
#                     (order_in_id,picking_id,min_date,partner_id,location_id,location_dest_id,picking_category,product_id,grade_id,lot_id,rak_id,variasi_id,product_uom_id,qty,pcs)
#                     VALUES
#                     (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                    
#                 '''
#                 params = [res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13],res[14]] 
#                 self.env.cr.execute(queryInsert,params)

#                 # --- Masuk semua data




#         queryHistoryAdj = """
#             select %s as order_in_id, 
#             a.id as inventory_id,
#             a.date,b.partner_id,
#             b.location_id,
#             b.location_dest_id,
#             b.product_id,
#             b.grade_id,
#             b.restrict_lot_id,
#             b.rak_id,
#             b.variasi_id,
#             b.product_uom,
#             b.product_qty,
#             1 as pcs 
#             from 
#                 stock_inventory a , stock_move b 
#             where 
#                 a.date >= '%s' 
#                 and a.date <= '%s' 
#                 and  a.id=b.inventory_id 
#                 and (b.location_dest_id=%s or b.location_id=%s) 
#                 and b.state='done'
#         """%(id_summary,date_start,date_end,id_location,id_location)


#         print "@@ ", id_summary
#         print "@@ ", date_start
#         print "@@ ", date_end
#         print "@@ ", location_id
#         print "--------------"
        

#         self._cr.execute(queryHistoryAdj)
#         for res in self.env.cr.fetchall():


#             print " A - ", res[0]
#             print " B - ", res[1]
#             print " C - ", res[2]
#             print " D - ", res[3]
#             print " E - ", res[4]
#             print " F - ", res[5]
#             print " G - ", res[6]
#             print " H - ", res[7]
#             print " I - ", res[8]
#             print " J - ", res[9]
#             print " K - ", res[10]
#             print " L - ", res[11]
#             print " M - ", res[12]
#             print " N - ", res[13]

#             if(kelompok_id!=False):
#                 # ---- Filtering berdasarkan kelompok id
#                 idKelompokVariasi = self.env['tj.stock.variasi'].search([('id','=',int(res[10]))]).kelompok_id.id
#                 if(int(kelompok_id)==int(idKelompokVariasi)):
#                     queryInsert = '''
#                         INSERT INTO tj_summary_rak_variasi_line_history_adj
#                         (order_adj_id,inventory_id,min_date,partner_id,location_id,location_dest_id,product_id,grade_id,lot_id,rak_id,variasi_id,product_uom_id,qty,pcs)
#                         VALUES
#                         (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                    
#                     '''

#                     params = [res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13]] 
#                     self.env.cr.execute(queryInsert,params)
#                 else:
#                     continue
#             else:

#                 # --- Masuk semua data
#                 queryInsert = '''
#                         INSERT INTO tj_summary_rak_variasi_line_history_adj
#                         (order_adj_id,inventory_id,min_date,partner_id,location_id,location_dest_id,product_id,grade_id,lot_id,rak_id,variasi_id,product_uom_id,qty,pcs)
#                         VALUES
#                         (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)                    
#                     '''
#                 params = [res[0],res[1],res[2],res[3],res[4],res[5],res[6],res[7],res[8],res[9],res[10],res[11],res[12],res[13]] 
#                 self.env.cr.execute(queryInsert,params)





        
    # ORIGINAL CODE 27 OKTOBER 2020
    def original_code_action_calculate(self):
        #print("==============================")
        values = []
        id_inventory = self.inventory_id.id
        id_location = self.location_id.id
        date_opname = self.date_opname
        date_start = self.date_start
        date_end = self.date_end
        id_summary = self.id

        query1 = """
                DELETE FROM tj_summary_rak_variasi_line
        """
        self._cr.execute(query1)
        self._cr.commit()
        query = """
                insert into tj_summary_rak_variasi_line (order_id,rak_id,product_id,grade_id, variasi_id , product_uom_id,saldo_awal_qty,saldo_awal_pcs,terima_qty,terima_pcs,retur_terima_qty,retur_terima_pcs,keluar_qty,keluar_pcs,retur_keluar_qty,retur_keluar_pcs,adj_qty,adj_pcs,balance_qty,balance_pcs) (
                select %s as order_id,
                rak_id,product_id,grade_id, variasi_id , product_uom_id,
                sum(saldo_awal_qty) as saldo_awal_qty, sum(saldo_awal_pcs) as saldo_awal_pcs, sum(terima_qty) as terima_qty, sum(terima_pcs) as terima_pcs, sum(retur_terima_qty) as retur_terima_qty, sum(retur_terima_pcs) as retur_terima_pcs, sum(keluar_qty) as keluar_qty, sum(keluar_pcs) as keluar_pcs, sum(retur_keluar_qty) as retur_keluar_qty, sum(retur_keluar_pcs) as retur_keluar_pcs, sum(adj_qty) as adj_qty, sum(adj_pcs) as adj_pcs,
                sum(saldo_awal_qty) + sum(terima_qty) + sum(retur_terima_qty) - sum(keluar_qty) - sum(retur_keluar_qty) + sum(adj_qty) as balance_qty,
                sum(saldo_awal_pcs) + sum(terima_pcs) + sum(retur_terima_pcs) - sum(keluar_pcs) - sum(retur_keluar_pcs) + sum(adj_pcs) as balance_pcs
                from (


                select b.id,b.product_id,b.grade_id,b.prod_lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,b.product_qty as saldo_awal_qty,1 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_inventory a , stock_inventory_line b where a.id=%s  and  a.id=b.inventory_id and b.location_id=%s
                union


                select row_number() OVER () as id,
                product_id,grade_id, lot_id,rak_id , variasi_id , product_uom_id,
                sum(saldo_awal_qty) + sum(terima_qty) + sum(retur_terima_qty) - sum(keluar_qty) - sum(retur_keluar_qty) + sum(adj_qty) as saldo_awal_qty,
                sum(saldo_awal_pcs) + sum(terima_pcs) + sum(retur_terima_pcs) - sum(keluar_pcs) - sum(retur_keluar_pcs) + sum(adj_pcs) as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs
                from (

                select c.id,b.product_id,b.grade_id,c.lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, c.qty as terima_qty,1 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_picking a , stock_pack_operation b, stock_pack_operation_lot c where a.min_date > '%s' and a.min_date < '%s'  and  a.id=b.picking_id and b.id=c.operation_id and a.location_dest_id=%s and a.state='done'
                union
                select c.id,b.product_id,b.grade_id,c.lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, c.qty as keluar_qty, 1 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_picking a , stock_pack_operation b, stock_pack_operation_lot c where a.min_date > '%s' and a.min_date < '%s'  and  a.id=b.picking_id and b.id=c.operation_id and a.location_id=%s and a.state='done'
                union
                select b.id,b.product_id,b.grade_id,b.prod_lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, b.product_qty as adj_qty, 1 as adj_pcs  from stock_inventory a , stock_inventory_line b where a.date > '%s' and a.date < '%s'  and  a.id=b.inventory_id and b.location_id=%s and a.state='done'
                ) as a group by product_id,grade_id, lot_id, rak_id, variasi_id , product_uom_id


                union
                select c.id,b.product_id,b.grade_id,c.lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, c.qty as terima_qty, 1 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_picking a left join stock_pack_operation b on a.id=b.picking_id left join stock_pack_operation_lot c on b.id=c.operation_id left join stock_picking_type d on a.picking_type_id=d.id where a.min_date >= '%s' and a.min_date <= '%s'  and a.location_dest_id=%s and a.state='done'
                union
                select c.id,b.product_id,b.grade_id,c.lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, c.qty as keluar_qty, 1 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, 0 as adj_qty, 0 as adj_pcs  from stock_picking a left join stock_pack_operation b on a.id=b.picking_id left join stock_pack_operation_lot c on b.id=c.operation_id left join stock_picking_type d on a.picking_type_id=d.id where a.min_date >= '%s' and a.min_date <= '%s'  and a.location_id=%s and a.state='done'
                union
                select b.id,b.product_id,b.grade_id,b.prod_lot_id,COALESCE (NULLIF (b.rak_id,1),1) as rak_id,COALESCE (NULLIF (b.variasi_id,5778),5778) as variasi_id,b.product_uom_id,0 as saldo_awal_qty,0 as saldo_awal_pcs, 0 as terima_qty,0 as terima_pcs, 0 as retur_terima_qty, 0 as retur_terima_pcs, 0 as keluar_qty, 0 as keluar_pcs, 0 as retur_keluar_qty, 0 as retur_keluar_pcs, b.product_qty as adj_qty, 1 as adj_pcs  from stock_inventory a , stock_inventory_line b where a.date > '%s' and a.date <= '%s'  and  a.id=b.inventory_id and b.location_id=%s and a.state='done'
                ) as a group by rak_id,product_id,grade_id, variasi_id , product_uom_id
                )
            """%(id_summary,id_inventory,id_location,

                date_opname,date_start,id_location,
                date_opname,date_start,id_location,
                date_opname,date_start,id_location,

                date_start,date_end,id_location,
                date_start,date_end,id_location,
                date_start,date_end,id_location)
        self._cr.execute(query)
        self._cr.commit()
        self.action_calculate_history()

    

    # ORIGINAL CODE 27 OKTOBER 2020
    def original_code_action_calculate_history(self):
        print("==============================")
        # values = []
        id_inventory = self.inventory_id.id
        id_location = self.location_id.id
        date_opname = self.date_opname
        date_start = self.date_start
        date_end = self.date_end
        id_summary = self.id

        query1 = """
                DELETE FROM tj_summary_rak_variasi_line_history;
                DELETE FROM tj_summary_rak_variasi_line_history_adj;
        """
        self._cr.execute(query1)
        self._cr.commit()
        query = """
                insert into tj_summary_rak_variasi_line_history (order_in_id,picking_id,min_date,partner_id,location_id,location_dest_id,picking_category,product_id,grade_id,lot_id,rak_id,variasi_id,product_uom_id,qty,pcs) (
                select %s as order_in_id, a.id as picking_id,a.min_date,a.partner_id,a.location_id,a.location_dest_id,d.id as picking_category,b.product_id,b.grade_id,c.lot_id,b.rak_id,b.variasi_id,b.product_uom_id,c.qty,1 as pcs from stock_picking a , stock_pack_operation b, stock_pack_operation_lot c, makloon_picking_category d where a.picking_category=d.id and  a.min_date >= '%s' and a.min_date <= '%s'  and  a.id=b.picking_id and b.id=c.operation_id and (a.location_dest_id=%s or a.location_id=%s) and a.state='done'
                );

                insert into tj_summary_rak_variasi_line_history_adj (order_adj_id,inventory_id,min_date,partner_id,location_id,location_dest_id,product_id,grade_id,lot_id,rak_id,variasi_id,product_uom_id,qty,pcs) (
                select %s as order_in_id, a.id as inventory_id,a.date,b.partner_id,b.location_id,b.location_dest_id,b.product_id,b.grade_id,b.restrict_lot_id,b.rak_id,b.variasi_id,b.product_uom,b.product_qty,1 as pcs from stock_inventory a , stock_move b where a.date >= '%s' and a.date <= '%s'  and  a.id=b.inventory_id and (b.location_dest_id=%s or b.location_id=%s) and b.state='done'
                );


            """%(id_summary,date_start,date_end,id_location,id_location,
                id_summary,date_start,date_end,id_location,id_location)
        self._cr.execute(query)
        self._cr.commit()

class TjSummaryRakVariasiLine(models.Model):
    _name = 'tj.summary.rak.variasi.line'

    order_id = fields.Many2one('tj.summary.rak.variasi')
    product_id = fields.Many2one('product.product', string='Product')
    grade_id = fields.Many2one('makloon.grade', string='Grade')
    rak_id = fields.Many2one('makloon.rak', string='Lokasi')
    partner_id = fields.Many2one('res.partner', 'Partner', compute='_compute_partner_id')
    variasi_id = fields.Many2one('tj.stock.variasi', string='Variasi')
    product_uom_id = fields.Many2one('product.uom', string='Uom')
    saldo_awal_qty = fields.Float(string='saldo_awal_qty')
    saldo_awal_pcs = fields.Float(string='saldo_awal_pcs')
    terima_qty = fields.Float(string='terima_qty')
    terima_pcs = fields.Float(string='terima_pcs')
    retur_terima_qty = fields.Float(string='retur_terima_qty')
    retur_terima_pcs = fields.Float(string='retur_terima_pcs')
    keluar_qty = fields.Float(string='keluar_qty')
    keluar_pcs = fields.Float(string='keluar_pcs')
    retur_keluar_qty = fields.Float(string='retur_keluar_qty')
    retur_keluar_pcs = fields.Float(string='retur_keluar_pcs')
    adj_qty = fields.Float(string='adj_qty')
    adj_pcs = fields.Float(string='adj_pcs')
    balance_qty = fields.Float(string='balance_qty')
    balance_pcs = fields.Float(string='balance_pcs')


    # kelompok_id = fields.Many2one('tj.stock.variasi.kelompok', 'Kelompok',compute='_compute_partner_id')
    # kategori_id = fields.Many2one('tj.stock.variasi.kategori', 'Kategori',compute='_compute_partner_id')
    # jenis_id = fields.Many2one('tj.stock.variasi.jenis', 'Jenis',compute='_compute_partner_id')
    # dep_id = fields.Many2one('tj.stock.variasi.departemen', 'Dept',compute='_compute_partner_id')

    # greige_code = fields.Char('Greige Code',compute='_compute_partner_id')
    # kontruksi = fields.Char('Kontruksi', compute='_compute_partner_id')
    # lebar = fields.Float('Lebar', compute='_compute_partner_id')

    # gramasi = fields.Float('Gramasi', compute='_compute_partner_id')
    # partner_id = fields.Many2one('res.partner', 'Supplier',compute='_compute_partner_id')
    # partner_cust_id = fields.Many2one('res.partner', 'Customer',compute='_compute_partner_id')


    # kelompok_id = fields.Many2one('tj.stock.variasi.kelompok', 'Kelompok')
    kategori_id = fields.Many2one('tj.stock.variasi.kategori', 'Kategori')
    jenis_id = fields.Many2one('tj.stock.variasi.jenis', 'Jenis')
    dep_id = fields.Many2one('tj.stock.variasi.departemen', 'Dept')

    greige_code = fields.Char('Greige Code')
    kontruksi = fields.Char('Kontruksi')
    lebar = fields.Float('Lebar')

    gramasi = fields.Float('Gramasi')
    partner_id = fields.Many2one('res.partner', 'Supplier')
    partner_cust_id = fields.Many2one('res.partner', 'Customer')



    @api.depends('variasi_id')
    def _compute_partner_id(self):
        for rec in self:
            rec.partner_id = rec.variasi_id.partner_id.id

            # rec.kelompok_id = rec.variasi_id.kelompok_id.id
            # rec.kategori_id = rec.variasi_id.kategori_id.id
            # rec.jenis_id = rec.variasi_id.jenis_id.id
            # rec.dep_id = rec.variasi_id.dep_id.id

            # rec.greige_code = rec.variasi_id.code
            # rec.kontruksi = rec.variasi_id.kontruksi
            # rec.lebar = rec.variasi_id.lebar

            # rec.gramasi = rec.variasi_id.gramasi
            # rec.partner_id = rec.variasi_id.partner_id.id
            # rec.partner_cust_id = rec.variasi_id.partner_cust_id.id


class TjSummaryRakVariasiLineHistory(models.Model):
    _name = 'tj.summary.rak.variasi.line.history'

    order_in_id = fields.Many2one('tj.summary.rak.variasi')
    picking_id = fields.Many2one('stock.picking', 'No Transfer',)
    min_date  = fields.Datetime("Date")
    partner_id = fields.Many2one('res.partner', 'Partner',)
    location_id = fields.Many2one('stock.location', 'Source Location',)
    location_dest_id = fields.Many2one('stock.location', 'Destination',)
    picking_category = fields.Many2one('makloon.picking.category', string='Picking Type',)
    product_id = fields.Many2one('product.product', string='Product',)
    grade_id = fields.Many2one('makloon.grade', string='Grade')
    lot_id = fields.Many2one('stock.production.lot', string='Lot',)
    rak_id = fields.Many2one('makloon.rak', string='Lokasi')
    variasi_id = fields.Many2one('tj.stock.variasi', string='Variasi',)
    product_uom_id = fields.Many2one('product.uom', string='Uom',)
    qty = fields.Float(string='Qty',)
    pcs = fields.Float(string='pcs',)


# class TjBenangLineHistoryReturnIn(models.Model):
#     _name = 'tj.benang.line.history.return.in'

#     order_ret_in_id = fields.Many2one('stock.summary.dua')
#     picking_id = fields.Many2one('stock.picking', 'No Transfer',)
#     min_date  = fields.Datetime("Date")
#     partner_id = fields.Many2one('res.partner', 'Partner',)
#     location_id = fields.Many2one('stock.location', 'Source Location',)
#     location_dest_id = fields.Many2one('stock.location', 'Destination',)
#     picking_category = fields.Many2one('makloon.picking.category', string='Picking Type')
#     product_id = fields.Many2one('product.product', string='Product')
#     lot_id = fields.Many2one('stock.production.lot', string='Lot')
#     variasi_id = fields.Many2one('tj.stock.variasi', string='Variasi')
#     product_uom_id = fields.Many2one('product.uom', string='Uom')
#     qty = fields.Float(string='Qty')
#     pcs = fields.Float(string='pcs')

# class TjBenangLineHistoryOut(models.Model):
#     _name = 'tj.benang.line.history.out'

#     order_out_id = fields.Many2one('stock.summary.dua')
#     picking_id = fields.Many2one('stock.picking', 'No Transfer',)
#     min_date  = fields.Datetime("Date")
#     partner_id = fields.Many2one('res.partner', 'Partner',)
#     location_id = fields.Many2one('stock.location', 'Source Location',)
#     location_dest_id = fields.Many2one('stock.location', 'Destination',)
#     picking_category = fields.Many2one('makloon.picking.category', string='Picking Type')
#     product_id = fields.Many2one('product.product', string='Product')
#     lot_id = fields.Many2one('stock.production.lot', string='Lot')
#     variasi_id = fields.Many2one('tj.stock.variasi', string='Variasi')
#     product_uom_id = fields.Many2one('product.uom', string='Uom')
#     qty = fields.Float(string='Qty')
#     pcs = fields.Float(string='pcs')

# class TjBenangLineHistoryReturnOut(models.Model):
#     _name = 'tj.benang.line.history.return.out'

#     order_ret_out_id = fields.Many2one('stock.summary.dua')
#     picking_id = fields.Many2one('stock.picking', 'No Transfer',)
#     min_date  = fields.Datetime("Date")
#     partner_id = fields.Many2one('res.partner', 'Partner',)
#     location_id = fields.Many2one('stock.location', 'Source Location',)
#     location_dest_id = fields.Many2one('stock.location', 'Destination',)
#     picking_category = fields.Many2one('makloon.picking.category', string='Picking Type')
#     product_id = fields.Many2one('product.product', string='Product')
#     lot_id = fields.Many2one('stock.production.lot', string='Lot')
#     variasi_id = fields.Many2one('tj.stock.variasi', string='Variasi')
#     product_uom_id = fields.Many2one('product.uom', string='Uom')
#     qty = fields.Float(string='Qty')
#     pcs = fields.Float(string='pcs')

class TjSummaryRakVariasiLineHistoryAdj(models.Model):
    _name = 'tj.summary.rak.variasi.line.history.adj'

    order_adj_id = fields.Many2one('tj.summary.rak.variasi')
    inventory_id = fields.Many2one('stock.inventory', 'No Adjustment',)
    min_date  = fields.Datetime("Date")
    partner_id = fields.Many2one('res.partner', 'Partner',)
    location_id = fields.Many2one('stock.location', 'Source Location',)
    location_dest_id = fields.Many2one('stock.location', 'Destination',)
    # picking_category = fields.Many2one('makloon.picking.category', string='Picking Type')
    product_id = fields.Many2one('product.product', string='Product')
    grade_id = fields.Many2one('makloon.grade', string='Grade')
    lot_id = fields.Many2one('stock.production.lot', string='Lot')
    rak_id = fields.Many2one('makloon.rak', string='Lokasi')
    variasi_id = fields.Many2one('tj.stock.variasi', string='Variasi')
    product_uom_id = fields.Many2one('product.uom', string='Uom')
    qty = fields.Float(string='Qty')
    pcs = fields.Float(string='pcs')