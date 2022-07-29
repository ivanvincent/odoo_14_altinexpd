from urllib import request
from odoo import fields, models, api, _ 
from odoo.exceptions import UserError
from datetime import datetime
import mysql.connector
import ast
import json
from odoo.tools.float_utils import float_compare, float_is_zero, float_repr, float_round
import logging
_logger = logging.getLogger(__name__)




class PullMysqlWizard(models.TransientModel):

    _name = 'pull.mysql.wizard'
    
    
    start_date  = fields.Date(string='Start Date', default=fields.Date.today(),required=True, )
    end_date    = fields.Date(string='End Date', default=fields.Date.today(),required=True, )
    
    @api.model
    def connect_mysql(self):
        SQL_HOST = self.env["ir.config_parameter"].sudo().get_param("mysql_host")
        SQL_PORT = self.env["ir.config_parameter"].sudo().get_param("mysql_port")
        SQL_PASSWORD = self.env["ir.config_parameter"].sudo().get_param("mysql_password")
        SQL_USER = self.env["ir.config_parameter"].sudo().get_param("mysql_username")
        SQL_DATABASE = self.env["ir.config_parameter"].sudo().get_param("mysql_database")
        connection  = mysql.connector.connect(user=SQL_USER,
                                            password=SQL_PASSWORD,      
                                            host=SQL_HOST,
                                            charset='utf8',
                                            database=SQL_DATABASE,port=SQL_PORT,use_pure=True)
        return connection


    def disconnect_mysql(self):
        self.connect_mysql().close()
        
        
    def unlink_om(self,start_date,end_date):
        query = """ DELETE FROM pull_cron_om WHERE tanggal BETWEEN '%s' AND '%s' """%(start_date,end_date)
        return query
        
        
    def check_pulled_om(self,start_date,end_date):
        query = """ SELECT name FROM pull_cron_om WHERE tanggal BETWEEN  '%s' AND '%s' """%(start_date,end_date)
        self._cr.execute(query)
        results = self._cr.rowcount 
        return results
    
    def query_invoice(self,start_date,end_date):
        query = """
                select a.no_faktur,a.nota,a.tanggal,a.kd_plg,a.nama as nama_plg,
                    a.kelompok,a.ket_group,a.kd_plg_gr,a.noom,a.kd_keluar,a.kd_sales,
                    a.kd_jalur,a.no_lpb,b.kd_brg,b.quantity,b.satuan_harga,b.qty_tukar,
                    b.qty_retur,b.harga_retur from faktur a, faktur_detail b 
                where 
                    a.no_faktur=b.no_faktur and a.no_faktur <> '' and a.tanggal between '%s' and '%s'
                """%(start_date,end_date)
        return query

    
    def action_pull(self):
        connection = self.connect_mysql()
        cr         = connection.cursor(dictionary=True)
        query      =  self.query_invoice(self.start_date,self.end_date)
        cr.execute(query)
        results = cr.fetchall()
        line_ids = []
        for x,result in enumerate(results):
            nxt = results[x + 1].get('no_faktur') if x < len(results) - 1 else None
            nxt_brg = results[x + 1].get('kd_brg') if x < len(results) - 1 else None
            line_ids += [{
                "harga_retur":result.get('harga_retur'),
                "qty_retur":result.get('qty_retur'),
                "qty_tukar":result.get('qty_tukar'),
                "kd_brg":result.get('kd_brg'),
                "quantity":result.get('quantity'),
                }]
            if result.get('no_faktur') != nxt and result.get('nxt_brg') != nxt_brg:
                table = 'invoice_temp'
                quote = '"{}"'.format
                
                columns = ['name','tanggal','nota','kd_plg','nama_plg','kelompok','ket_group','kd_plg_gr','no_om','surat_jalan','kd_sales','kd_jalur','no_lpb']
                values  = [result.get('no_faktur'),result.get('tanggal').strftime('%Y-%m-%d'),result.get('nota'),result.get('kd_plg'),result.get('nama_plg'),result.get('kelompok'),result.get('ket_group'),result.get('kd_plg_gr'),result.get('noom'),result.get('surat_jalan'),result.get('kd_sales'),result.get('kd_jalur'),result.get('no_lpb')]
                query = """ 
                            INSERT INTO %s (%s) VALUES %s RETURNING id
                        """%(table,", ".join(quote(col) for col in columns),tuple(values))
                self._cr.execute(query.replace('None', 'NULL'))
                invoice = self._cr.dictfetchone()
                self._cr.execute("select insert_invoice_temp_line(%s, '%s')" % (invoice.get('id'),json.dumps(line_ids,default=str)))
                line_ids = []
                
              
                
                
            
        
        
    
    
    def update_state_om(self,no_om):
        query = """UPDATE om set status_odoo = 1 WHERE noom =  '%s' """%(no_om)
        return query 
    
    def cancel_state_om(self,no_om):
        query = """UPDATE om set status_odoo = 0 WHERE noom = '%s' """%(no_om)
        return query 
    
    
    def action_rollback(self):
        om_form = self.env.ref('pull_mysql.pull_cron_om_form', raise_if_not_found=False)
        om_tree = self.env.ref('pull_mysql.pull_cron_om_tree', raise_if_not_found=False)
        
        connection = self.connect_mysql()
        cr = connection.cursor(dictionary=True)
        query = """  
                    SELECT  
                        a.noom,a.np,a.tanggal,a.kd_plg,a.kd_brg,a.harga,
                        c.nama as nama_pelanggan ,
                        c.alamat as alamat ,
                        a.pembayaran,a.keterangan,a.nb,a.sales,a.pita,a.sablon,a.size,
                        a.lf,a.handling,a.merek,a.kd_design,a.status,a.kat_flow_proses,a.export,
                        a.satuan_om,a.satuan_om2,a.user_input,a.jenis_transaksi,a.ket_status,
                        a.status_proses,b.idpesanan,b.kd_brg,b.warna,b.quantity,b.harga_warna,
                        b.ket_warna,b.satuan_mkt 
                    FROM  om a ,
                        om_detail b,
                        pelanggan c
                    WHERE 
                        a.noom=b.noom 
                        and a.kd_plg = c.kd_plg
                        and a.tanggal between '%s' and '%s'
                        and a.status_odoo = 1
                """%(self.start_date,self.end_date)

        cr.execute(query)
        results = cr.fetchall()
        
        for result in results:
            query = self.cancel_state_om(result.get('noom'))
            cr.execute(query)   
            self._cr.execute(self.unlink_om(self.start_date,self.end_date))
            
        connection.commit()   
        cr.close()
        self.disconnect_mysql()
        
        
    

    
    
    
    