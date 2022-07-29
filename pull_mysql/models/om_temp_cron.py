from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil import relativedelta
from datetime import datetime
import mysql.connector

import logging
_logger = logging.getLogger(__name__)


# SQL_HOST     = "pmti.ddns.net"
# SQL_HOST     = "43.248.212.142"
SQL_HOST     = "10.0.10.199"
SQL_USER     = 'pmti'
SQL_PASSWORD = 'rahasiakudewe'
SQL_DATABASE = 'tekstil_pmti'
# SQL_PORT     = 3367
SQL_PORT     = 3306

class PullOmWizard(models.TransientModel):

    _name = 'pull.om.wizard'
    
    
    start_date = fields.Date(string='Start Date', default=fields.Date.today(),required=True, )
    end_date = fields.Date(string='End Date', default=fields.Date.today(),required=True, )
    
    @api.model
    def connect_mysql(self):
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
        
        
    
    
    def action_pull(self):
        self.action_rollback()
        om_form = self.env.ref('pull_mysql.pull_cron_om_form', raise_if_not_found=False)
        om_tree = self.env.ref('pull_mysql.pull_cron_om_tree', raise_if_not_found=False)
        
        # pulled_om = self.check_pulled_om(self.start_date,self.end_date)
        
        # if  pulled_om == 0:
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
                    and a.status_odoo = 0
                """%(self.start_date,self.end_date)

        cr.execute(query)
        results = cr.fetchall()
        line_ids = []
        for x,result in enumerate(results):
            prev = results[x - 1].get('noom') if x >= 1 else None
            nxt = results[x + 1].get('noom') if x < len(results) - 1 else None
            nxt_brg = results[x + 1].get('kd_brg') if x < len(results) - 1 else None
            
            line = {
                "no_om":result.get('noom'),
                "id_pesanan":result.get('id_pesanan'),
                "harga_warna":result.get('harga_warna'),
                "warna":result.get('warna'),
                "kd_brg":result.get('kd_brg'),
                "quantity":result.get('quantity'),
                "satuan_mkt":result.get('satuan_mkt'),
                "ket_warna":result.get('ket_warna'),
            }
            
            line_ids.append((0,0,line))
            if result.get('noom') != nxt and result.get('nxt_brg') != nxt_brg:
                self.env['pull.cron.om'].create({
                "name":result.get('noom'),   
                "kd_brg":result.get('kd_brg'),   
                "kd_plg":result.get('kd_plg'),   
                "nama_pelanggan":result.get('nama_pelanggan'),   
                "alamat":result.get('alamat'),   
                "harga":result.get('harga'),   
                "np":result.get('np'),   
                "nb":result.get('nb'),   
                "lf":result.get('lf'),   
                "merek":result.get('merek'),   
                "ket_warna":result.get('ket_warna'),   
                "warna":result.get('warna'),   
                "handling":result.get('handling'),   
                "user_input":result.get('user_input'),   
                "kd_design":result.get('kd_design'),   
                "export":result.get('export'),   
                "ket_status":result.get('ket_status'),   
                "tanggal":result.get('tanggal'),   
                "pembayaran":result.get('pembayaran'),   
                "sales":result.get('sales'),   
                "pita":result.get('pita'),   
                "status":result.get('status'),   
                "sablon":result.get('sablon'),   
                "satuan_om":result.get('satuan_om'),   
                "keterangan":result.get('keterangan'),   
                "status_proses":result.get('status_proses'),   
                "jenis_transaksi":result.get('jenis_transaksi'),   
                "size":result.get('size'),   
                "kat_flow_proses":result.get('kat_flow_proses'),   
                "line_ids":line_ids,   
                })
                    
                line_ids = []
        
        
        for result in results:
            query = self.update_state_om(result.get('noom'))
            cr.execute(query)
                
        connection.commit()   
        cr.close()
            
        
        self.disconnect_mysql()    
            
        return {
            'type': 'ir.actions.act_window',
            'name': 'Order Marketing',
            'res_model': 'pull.cron.om',
            'views': [(om_tree.id, 'tree'),(om_form.id, 'form')],
            'target': 'current',
        }
   
    # else:
    #     raise UserError('Om pada tanggal %s sampai %s sudah ada di system odoo'%(self.start_date,self.end_date))
    
        
        


class PullCron(models.Model):
    _name = 'pull.cron.om'

    name            = fields.Char(string='OM')
    date            = fields.Datetime('Validation Date', readonly=True,default=fields.Date.today())
    np              = fields.Char(string='No Pesanan')
    kd_brg          = fields.Char(string='Kode Barang')
    kd_plg          = fields.Char(string='Kode Pelanggan')
    nb              = fields.Char(string='NB')
    harga           = fields.Float(string='Harga')
    lf              = fields.Char(string='Lf')
    merek           = fields.Char(string='Merk')
    warna           = fields.Char(string='Warna')
    ket_warna       = fields.Char(string='Ket Warna')
    handling        = fields.Char(string='Handling')
    user_input      = fields.Char(string='User')
    kd_design       = fields.Char(string='Kode Design')
    export          = fields.Char(string='Export')
    ket_status      = fields.Char(string='Status')
    tanggal         = fields.Date(string='Tanggal ')
    nama_pelanggan  = fields.Char(string='Nama Pelanggan')
    alamat          = fields.Char(string='Alamat')
    pembayaran      = fields.Char(string='Pembayaran')
    sales           = fields.Char(string='Sales')
    pita            = fields.Char(string='Pita')
    status          = fields.Integer(string='Status')
    sablon          = fields.Char(string='Sablon')
    satuan_om       = fields.Char(string='Satuan')
    keterangan      = fields.Char(string='Keterangan')
    status_proses   = fields.Char(string='Status Proses')
    jenis_transaksi = fields.Char(string='Jenis Transaksi')
    size            = fields.Integer(string='Size')
    kat_flow_proses = fields.Char(string='Kat Flow Proses')
    tot_quantity    = fields.Float(string='Total Quantity',compute="_total_quantity")
    is_processed    = fields.Boolean(string='Is Proccessed ?',default=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('authorized', 'Authorized'),
        ('done', 'Done'),
        ('cancel', 'Canceled'),
        ('error', 'Error'),],
        string='Status', copy=False, default='draft', required=True, readonly=True)
    
    line_ids = fields.One2many('pull.cron.om.line', 'pull_id', string='Details')
    
    def check_pulled_om(self):
        query = """ SELECT name FROM pull_cron_om WHERE tanggal = '%s'"""%(fields.Date.today())
        self._cr.execute(query)
        results = self._cr.rowcount 
        return results
    
    
    def update_state_om(self,no_om):
        query = """ UPDATE om set status_odoo = 1 WHERE noom =  '%s' """%(no_om)
        self._cr.execute(query)
        results = self._cr.rowcount 
        return results
    
    def cancel_state_om(self,no_om):
        query = """ UPDATE om set status_odoo = 0 WHERE noom = '%s' """%(no_om)
        self._cr.execute(query)
        results = self._cr.rowcount 
        return results
    
    
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
                        and a.tanggal = '%s'
                        and a.status_odoo = 1
                """%(fields.Date.today())

        cr.execute(query)
        results = cr.fetchall()
        
        for result in results:
            query = self.cancel_state_om(result.get('noom'))
            cr.execute(query)   
            self._cr.execute(self.unlink_om(fields.Date.today(),fields.Date.today()))
            
        connection.commit()   
        cr.close()
        self.disconnect_mysql()
    
    
    @api.depends('line_ids')
    def _total_quantity(self):
        for line in self:
            total_quantity = sum(line.line_ids.mapped('quantity'))
            line.tot_quantity = total_quantity
        
    
    @api.model
    def connect_mysql(self):
        connection  = mysql.connector.connect(user=SQL_USER,
                                            password=SQL_PASSWORD,      
                                            host=SQL_HOST,
                                            charset='utf8',
                                            database=SQL_DATABASE,port=SQL_PORT,use_pure=True)
        return connection

    def disconnect_mysql(self):
        self.connect_mysql().close()
        
        
    def pull_process(self):
        self.action_rollback()
        _logger.warning('='*40)
        _logger.warning('Cron Pulling om started')
        _logger.warning('='*40)
        
        connection = self.connect_mysql()
        cr = connection.cursor(dictionary=True)
        pulled_om = self.check_pulled_om()
        pulled = []
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
                    om_detail b ,
                    pelanggan c 
                WHERE 
                    a.noom=b.noom 
                    and a.kd_plg=c.kd_plg
                    and a.tanggal = '%s'
                    and a.status_odoo = 0
                """%(fields.Date.today())

        cr.execute(query)
        results = cr.fetchall()
        line_ids = []
        for x,result in enumerate(results):
            prev = results[x - 1].get('noom') if x >= 1 else None
            nxt = results[x + 1].get('noom') if x < len(results) - 1 else None
            nxt_brg = results[x + 1].get('kd_brg') if x < len(results) - 1 else None
            
            line = {
                "no_om":result.get('noom'),
                "id_pesanan":result.get('id_pesanan'),
                "harga_warna":result.get('harga_warna'),
                "warna":result.get('warna'),
                "kd_brg":result.get('kd_brg'),
                "quantity":result.get('quantity'),
                "satuan_mkt":result.get('satuan_mkt'),
                "ket_warna":result.get('ket_warna'),
            }
            
            line_ids.append((0,0,line))
            if result.get('noom') != nxt and result.get('nxt_brg') != nxt_brg:
                om = self.env['pull.cron.om'].create({
                "name":result.get('noom'),   
                "kd_brg":result.get('kd_brg'),   
                "nama_pelanggan":result.get('nama_pelanggan'),   
                "alamat":result.get('alamat'),   
                "kd_plg":result.get('kd_plg'),   
                "harga":result.get('harga'),   
                "np":result.get('np'),   
                "nb":result.get('nb'),   
                "lf":result.get('lf'),   
                "merek":result.get('merek'),   
                "ket_warna":result.get('ket_warna'),   
                "warna":result.get('warna'),   
                "handling":result.get('handling'),   
                "user_input":result.get('user_input'),   
                "kd_design":result.get('kd_design'),   
                "export":result.get('export'),   
                "ket_status":result.get('ket_status'),   
                "tanggal":result.get('tanggal'),   
                "pembayaran":result.get('pembayaran'),   
                "sales":result.get('sales'),   
                "pita":result.get('pita'),   
                "status":result.get('status'),   
                "sablon":result.get('sablon'),   
                "satuan_om":result.get('satuan_om'),   
                "keterangan":result.get('keterangan'),   
                "status_proses":result.get('status_proses'),   
                "jenis_transaksi":result.get('jenis_transaksi'),   
                "size":result.get('size'),   
                "kat_flow_proses":result.get('kat_flow_proses'),   
                "line_ids":line_ids,   
                })
                
                pulled.append(om)
                
        
        for result in results:
            query = self.update_state_om(result.get('noom'))
            cr.execute(query)
                
        connection.commit()   
        cr.close()
            
        
        self.disconnect_mysql()   
                
        return len(pulled)
    
    
    def _cron_pull_process(self):
        try:
            pulled = self.pull_process()
            self.disconnect_mysql()
            _logger.warning('='*40)
            _logger.warning('Cron Pulling OM stopped with data om as much as %s'%(pulled))
            _logger.warning('='*40)
        except Exception as e:
            _logger.warning('='*40)
            _logger.exception("Transaction pull processing failed because %s"%(e))
            _logger.warning('='*40)
            # self.env.cr.rollback()
    
    
    
    
class PullCronLine(models.Model):
    _name = 'pull.cron.om.line'

    
    pull_id         = fields.Many2one('pull.cron.om', string='Pull')
    no_om           = fields.Char(related='pull_id.name', string='No Om')
    id_pesanan      = fields.Integer(string='Id Pesanan')
    kd_brg          = fields.Char(string='Kode Barang')
    quantity        = fields.Float(string='Quantity')
    harga_warna     = fields.Float(string='Harga Warna')
    warna           = fields.Char(string='Warna')
    ket_warna       = fields.Char(string='Ket Warna')
    satuan_mkt       = fields.Char(string='Satuan MKT')
    
    

    
    
    
    