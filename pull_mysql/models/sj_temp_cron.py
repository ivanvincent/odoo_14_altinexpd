from odoo import models, fields, api, _
from odoo.exceptions import UserError
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

class PullSJWizard(models.TransientModel):

    _name = 'pull.sj.wizard'
    
    start_date = fields.Date(string='Start Date', default=fields.Date.today())
    end_date = fields.Date(string='End Date', default=fields.Date.today())
    departement = fields.Selection([("GDJ","Gudang Jadi"),("GDG","Gudang Greige"),("GDR","Gudang Rongsok")], string='Department')

     
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
    
    def check_pulled_sj(self,start_date,end_date):
        query = """ SELECT name FROM pull_cron_sj WHERE tanggal BETWEEN '%s' AND '%s' """%(start_date,end_date)
        self._cr.execute(query)
        results = self._cr.rowcount 
        return results
    
    def unlink_sj(self,start_date,end_date):
        query = """ DELETE FROM pull_cron_sj WHERE tanggal BETWEEN '%s' AND '%s' """%(start_date,end_date)
        return query
    
    def update_state_kd_keluar(self,kd_keluar):
        query = """ UPDATE pengeluaran set status_odoo = 1  WHERE kd_keluar = '%s' """%(kd_keluar)
        return query 
    
    def cancel_state_kd_keluar(self,kd_keluar):
        query = """ UPDATE pengeluaran set status_odoo = 0  WHERE kd_keluar = '%s' """%(kd_keluar)
        return query 
    
    
    def check_pulled_sj_by_name(self,kd_keluar):
        # connection = self.connect_mysql()
        # cr = connection.cursor(dictionary=True)
        query = """ SELECT name FROM pull_cron_sj  WHERE name = '%s' """%(kd_keluar)
        self._cr.execute(query)
        results = self._cr.rowcount 
        return results
    
    def action_pull(self):
        self.action_rollback()
        sj_form = self.env.ref('pull_mysql.pull_cron_js_form', raise_if_not_found=False)
        sj_tree = self.env.ref('pull_mysql.pull_cron_js_tree', raise_if_not_found=False)
        connection = self.connect_mysql()
        cr = connection.cursor(dictionary=True)
        updated = None
        pulled_sj = self.check_pulled_sj(self.start_date,self.end_date)
        pulled = []
        # if  pulled_sj == 0:
        # where  a.dep in ('GDJ','GBS') and a.kd_dep = 'DEX' and a.status_odoo = 0 and a.tanggal BETWEEN '%s' and '%s' 
        
        query = """  
                SELECT 
                    a.kd_keluar,
                    a.dep,  
                    a.tanggal,
                    a.kd_plg,
                    c.kd_brg,
                    f.nama as nama_barang,
                    e.nama as nama_pelanggan,
                    e.npwp,
                    e.alamat as alamat,
                    c.lot,c.no_warna,c.grade,sum(c.cone) as cone,sum(c.quantity) as quantity,sum(c.quantity2) as quantity_2,
                    c.noom,c.ket_om,d.harga,c.satuan,
                    g.Gramasi_finish as gramasi_finish,
                    g.Gramasi_grey as gramasi_greige,
                    g.lbr_kain as lebar_greige,
                    g.lbr_finish as lebar_finish,
                    g.potong as std_potong,
                    g.kd_design as kd_design
                FROM pengeluaran a 
                LEFT JOIN 
                    trans_keluar_barcode 
                    b on a.kd_keluar=b.kd_keluar 
                LEFT JOIN barcode c on b.barcode=c.barcode 
                LEFT JOIN om d on c.noom=d.noom 
                LEFT JOIN pelanggan e on a.kd_plg = e.kd_plg
                LEFT JOIN barang f on c.kd_brg = f.kd_brg
                LEFT JOIN kontruksi g on f.kd_brg = g.kd_design 
                where  a.kd_plg is not null and a.status_odoo = 0 and a.tanggal BETWEEN '%s' AND '%s'  
                GROUP BY a.kd_keluar,c.kd_brg,c.no_warna,c.grade,c.satuan,b.id_transaksi
                """%(self.start_date,self.end_date)

        cr.execute(query)
        results = cr.fetchall()
        line_ids = []
        for idx,current in enumerate(results):
            prev = results[idx - 1].get('kd_keluar') if idx >= 1 else None
            nxt = results[idx + 1].get('kd_keluar') if idx < len(results) - 1 else None
            line = {
                "kd_keluar":current.get('kd_keluar'),
                "kd_brg":current.get('kd_brg'),
                "tanggal":current.get('tanggal'),
                "om":current.get('noom'),
                "ket_om":current.get('ket_om'),
                "harga":current.get('harga'),
                "no_warna":current.get('no_warna'),
                "kd_plg":current.get('kd_plg'),
                "grade":current.get('grade'),
                "quantity_2":current.get('quantity_2'),
                "satuan":current.get('satuan'),
                "cone":current.get('cone'),
                "quantity":current.get('quantity'),
                "gramasi_greige":current.get('gramasi_greige'),
                "gramasi_finish":current.get('gramasi_finish'),
                "lebar_greige":current.get('lebar_greige'),
                "lebar_finish":current.get('lebar_finish'),
                "std_potong":current.get('std_potong'),
                "kd_design":current.get('kd_design'),
                "lot":current.get('lot'),
                "dep":current.get('dep'),
                "nama_barang":current.get('nama_barang'),   
                "nama_pelanggan":current.get('nama_pelanggan'),   
                "name":current.get('kd_keluar'),
            }
            
            line_ids.append((0,0,line))
            if current.get('kd_keluar') != nxt:
                self.env['pull.cron.sj'].create({
                "name":current.get('kd_keluar'),   
                "om":current.get('noom'),   
                "ket_om":current.get('ket_om'),   
                "tanggal":current.get('tanggal'),   
                "kd_plg":current.get('kd_plg'),   
                "nama_pelanggan":current.get('nama_pelanggan'),   
                "alamat":current.get('alamat'),   
                "npwp":current.get('npwp'),   
                "dep":current.get('dep'),   
                "line_ids":line_ids,   
                })
                line_ids = []
        
        
        
        for result in results:
            query = self.update_state_kd_keluar(result.get('kd_keluar'))
            cr.execute(query)
        
        connection.commit()   
        cr.close()
        self.disconnect_mysql()    
        
            
        return {
            'type': 'ir.actions.act_window',
            'name': 'Surat Jalan',
            'res_model': 'pull.cron.sj',
            'views': [(sj_tree.id, 'tree'),(sj_form.id, 'form')],
            'target': 'current',
        }
        
    def action_rollback(self):
        sj_form = self.env.ref('pull_mysql.pull_cron_js_form', raise_if_not_found=False)
        sj_tree = self.env.ref('pull_mysql.pull_cron_js_tree', raise_if_not_found=False)
        connection = self.connect_mysql()
        cr = connection.cursor(dictionary=True)
        query = """  
                    SELECT 
                        a.kd_keluar,
                        a.dep,  
                        a.tanggal,
                        a.kd_plg,
                        c.kd_brg,
                        f.nama as nama_barang,
                        e.nama as nama_pelanggan,
                        e.npwp,
                        e.alamat as alamat,
                        c.lot,c.no_warna,c.grade,sum(c.cone) as cone,sum(c.quantity) as quantity,sum(c.quantity2) as quantity_2,
                        c.noom,c.ket_om,d.harga,c.satuan,
                        g.Gramasi_finish as gramasi_finish,
                        g.Gramasi_grey as gramasi_greige,
                        g.lbr_kain as lebar_greige,
                        g.lbr_finish as lebar_finish,
                        g.potong as std_potong,
                        g.kd_design as kd_design
                    FROM pengeluaran a 
                    LEFT JOIN 
                        trans_keluar_barcode 
                        b on a.kd_keluar=b.kd_keluar 
                    LEFT JOIN barcode c on b.barcode=c.barcode 
                    LEFT JOIN om d on c.noom=d.noom 
                    left join jo h on d.noom=h.noom
                    LEFT JOIN pelanggan e on a.kd_plg = e.kd_plg
                    LEFT JOIN barang f on h.kd_brg = f.kd_brg
                    LEFT JOIN kontruksi g on f.kd_brg = g.kd_design 
                    where  a.kd_plg is not null and a.status_odoo = 1 and a.tanggal BETWEEN '%s' AND '%s'  
                    GROUP BY a.kd_keluar,c.kd_brg,c.no_warna,c.grade,c.satuan,b.id_transaksi
                """%(self.start_date,self.end_date)

        cr.execute(query)
        results = cr.fetchall()
        
        for result in results:
            query = self.cancel_state_kd_keluar(result.get('kd_keluar'))
            cr.execute(query)   
            self._cr.execute(self.unlink_sj(self.start_date,self.end_date))
            
        connection.commit()   
        cr.close()
        self.disconnect_mysql()  
        return {
            'type': 'ir.actions.act_window',
            'name': 'Surat Jalan',
            'res_model': 'pull.cron.sj',
            'views': [(sj_tree.id, 'tree'),(sj_form.id, 'form')],
            'target': 'current',
        }  
            


class PullCronSJ(models.Model):
    _name = 'pull.cron.sj'

    name            = fields.Char(string='Surat Jalan')
    tanggal         = fields.Date(string='Tanggal')
    om              = fields.Char(string='OM')
    ket_om          = fields.Char(string='Keterangan Om')
    dep             = fields.Char(string='Department')
    kd_plg          = fields.Char(string='Kode Pelanggan')
    nama_pelanggan  = fields.Char(string='Nama Pelanggan')
    npwp            = fields.Char(string='NPWP')
    partner_id      = fields.Many2one('res.partner', string='Customers',compute="_get_customer_id")
    alamat          = fields.Char(string='Alamat')
    is_invoiced     = fields.Boolean(string='Is Invoiced',default=False)
    line_ids        = fields.One2many('pull.cron.sj.line', 'pull_id', string='Line')
    
    _sql_constraints = [
        ('kd_keluar_unique', 'unique(tanggal,name)', 'Surat Jalan Sudah Di Tarik')
    ]
    
    def _get_customer_id(self):
        for line in self:
            partner = self.env['res.partner'].sudo().search([('ref','=',line.kd_plg)],limit=1)
            if not partner and line.kd_plg:
                customers = self.env['res.partner'].sudo().create({
                        "name":line.nama_pelanggan,
                        "ref": line.kd_plg,
                        "property_stock_customer": 5,
                        "property_stock_supplier": 4,
                        "property_account_receivable_id": 10659,
                        "property_account_payable_id": 10821,
                        "property_product_pricelist": 1,
                        "lang":"en_US",
                        "company_type":"company",
                        "street":line.alamat,
                        # "npwp":line.pull_id.npwp,
                        "npwp":line.npwp,
                    })
                    
                line.partner_id = customers.id
            line.partner_id = partner.id
    
    def name_get(self):
        res = []
        for record in self:
            displayName = '%s - %s'%(record.name,record.nama_pelanggan)
            res.append((record.id,displayName))
        return res
    
    
    @api.model
    def connect_mysql(self):
        connection  = mysql.connector.connect(user=SQL_USER,
                                            password=SQL_PASSWORD,      
                                            host=SQL_HOST,
                                            charset='utf8', 
                                            database=SQL_DATABASE,port=SQL_PORT,use_pure=True)
        return connection

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res_search = False
        res = self.search([ '|',('name',operator,name),('nama_pelanggan',operator,name)] + args, limit=limit)
        res_search = res.name_get()
        return res_search


    def disconnect_mysql(self):
        self.connect_mysql().close()
    
    
        
    def check_pulled_sj(self):
        query = """ SELECT name FROM pull_cron_sj WHERE tanggal = '%s' """%(fields.Date.today())
        self._cr.execute(query)
        results = self._cr.rowcount 
        return results
    
    def check_pulled_sj_pro(self):
        query = """ SELECT name FROM pull_cron_sj WHERE tanggal = '%s' """%(fields.Date.today())
        self._cr.execute(query)
        results = self._cr.rowcount 
        return results
        
    def pull_process(self):
        connection = self.connect_mysql()
        cr = connection.cursor(dictionary=True)
        # pulled_sj = self.check_pulled_sj()
        pulled = []
        # if  pulled_sj == 0:
        query = """  
            SELECT 
                a.kd_keluar,
                a.dep,  
                a.tanggal,
                a.kd_plg,
                c.kd_brg,
                f.nama as nama_barang,
                e.nama as nama_pelanggan,
                e.npwp,
                e.alamat as alamat,
                c.lot,c.no_warna,c.grade,sum(c.cone) as cone,sum(c.quantity) as quantity,sum(c.quantity2) as quantity_2,
                c.noom,c.ket_om,d.harga,c.satuan,
                g.Gramasi_finish as gramasi_finish,
                g.Gramasi_grey as gramasi_greige,
                g.lbr_kain as lebar_greige,
                g.lbr_finish as lebar_finish,
                g.potong as std_potong,
                g.kd_design as kd_design
            FROM pengeluaran a 
            LEFT JOIN 
                trans_keluar_barcode 
                b on a.kd_keluar=b.kd_keluar 
            LEFT JOIN barcode c on b.barcode=c.barcode 
            LEFT JOIN om d on c.noom=d.noom 
            left join jo h on d.noom=h.noom
            LEFT JOIN pelanggan e on a.kd_plg = e.kd_plg
            LEFT JOIN barang f on h.kd_brg = f.kd_brg
            LEFT JOIN kontruksi g on f.kd_brg = g.kd_design 
            where  a.kd_plg is not null and a.status_odoo = 0 and a.tanggal = '%s'  
            GROUP BY a.kd_keluar,c.kd_brg,c.no_warna,c.grade,c.satuan,b.id_transaksi
                # """%(fields.Date.today())


        cr.execute(query)
        results = cr.fetchall()
        line_ids = []
        for idx,current in enumerate(results):
            prev = results[idx - 1].get('kd_keluar') if idx >= 1 else None
            nxt = results[idx + 1].get('kd_keluar') if idx < len(results) - 1 else None
            line = {
                "kd_keluar":current.get('kd_keluar'),
                "kd_brg":current.get('kd_brg'),
                "tanggal":current.get('tanggal'),
                "om":current.get('noom'),
                "ket_om":current.get('ket_om'),
                "harga":current.get('harga'),
                "no_warna":current.get('no_warna'),
                "kd_plg":current.get('kd_plg'),
                "grade":current.get('grade'),
                "quantity_2":current.get('quantity_2'),
                "satuan":current.get('satuan'),
                "cone":current.get('cone'),
                "quantity":current.get('quantity'),
                "gramasi_greige":current.get('gramasi_greige'),
                "gramasi_finish":current.get('gramasi_finish'),
                "lebar_greige":current.get('lebar_greige'),
                "lebar_finish":current.get('lebar_finish'),
                "std_potong":current.get('std_potong'),
                "kd_design":current.get('kd_design'),
                "lot":current.get('lot'),
                "dep":current.get('dep'),
                "nama_barang":current.get('nama_barang'),   
                "nama_pelanggan":current.get('nama_pelanggan'),   
                "name":current.get('kd_keluar'),
            }
            
            line_ids.append((0,0,line))
            if current.get('kd_keluar') != nxt:
                sj = self.env['pull.cron.sj'].create({
                "name":current.get('kd_keluar'),   
                "om":current.get('noom'),   
                "ket_om":current.get('ket_om'),   
                "tanggal":current.get('tanggal'),   
                "kd_plg":current.get('kd_plg'),   
                "npwp":current.get('npwp'),   
                "nama_pelanggan":current.get('nama_pelanggan'),   
                "alamat":current.get('alamat'),   
                "dep":current.get('dep'),   
                "line_ids":line_ids,   
                })
                line_ids = []
                pulled.append(sj)
        
        
        
        for result in results:
            query = self.update_state_kd_keluar(result.get('kd_keluar'))
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
            _logger.warning('Cron Pulling SJ stopped with data sj as much as %s'%(pulled))
            _logger.warning('='*40)
        except Exception as e:
            _logger.warning('='*40)
            _logger.exception("Transaction pull processing failed because %s"%(e))
            _logger.warning('='*40)
            # self.env.cr.rollback()
    
    
class PullCronSJLine(models.Model):
    _name = 'pull.cron.sj.line'

    name            = fields.Char(string='Surat Jalan')
    kd_keluar       = fields.Char(string='Kode Keluar')
    pull_id         = fields.Many2one('pull.cron.sj', string='Pull')
    tanggal         = fields.Date(string='Tanggal')
    om              = fields.Char(string='OM')
    ket_om          = fields.Char(string='Keterangan Om')
    gramasi_greige  = fields.Float(string='Gramasi Greige')
    lebar_greige    = fields.Float(string='Lebar Greige')
    gramasi_finish  = fields.Float(string='Gramasi Finish')
    lebar_finish    = fields.Float(string='Lebar Finish')
    dep             = fields.Char(string='Department')
    cone            = fields.Integer(string='Pcs')
    kd_brg          = fields.Char(string='Kode Barang')
    harga           = fields.Float(string='Harga')
    kd_plg          = fields.Char(string='Kode Pelanggan')
    nama_barang     = fields.Char(string='Nama Barang')
    nama_pelanggan  = fields.Char(string='Nama Pelanggan')
    no_warna        = fields.Char(string='No Warna')
    grade           = fields.Char(string='Grade')
    satuan          = fields.Char(string='Satuan')
    quantity        = fields.Float(string='Quantity')
    quantity_2      = fields.Float(string='Quantity 2')
    kd_design       = fields.Char(string='Kd Design')
    std_potong      = fields.Float(string='Std Potong')
    lot             = fields.Char(string='Customer')
    qty_kg          = fields.Float(compute='_compute_conversion_qty', string='On Kg', store=False)
    qty_meter       = fields.Float(compute='_compute_conversion_qty', string='On Mtr', store=False)
    qty_yard        = fields.Float(compute='_compute_conversion_qty', string='On Yard', store=False)
    
    @api.depends('quantity')
    def _compute_conversion_qty(self):
        for line in self:
            if str(line.satuan).lower() == 'yard' or str(line.satuan).lower() == 'yrd':
                if line.gramasi_greige and line.lebar_greige:
                    line.qty_kg = (line.gramasi_greige / 1000) *  line.quantity
                    # line.qty_kg = (line.lebar_greige / 100 * line.gramasi_greige / 1000) * 0.9144 *  line.quantity
                else:
                    line.qty_kg = 0
                
                line.qty_meter = line.quantity * 0.9144
                line.qty_yard = line.quantity
            
            elif str(line.satuan).lower() == 'meter' or str(line.satuan).lower() == 'mtr':
                line.qty_meter = line.quantity
                line.qty_yard = line.quantity / 0.9144
                line.qty_kg = ((line.quantity / 0.9144 )* line.gramasi_greige) / 1000
            
            elif str(line.satuan).lower() == 'kg':
                line.qty_meter = (line.quantity * 1000 / line.gramasi_greige) * 0.9144
                line.qty_yard = line.quantity * 1000 / line.gramasi_greige
                line.qty_kg = line.quantity
                
            else:
                line.qty_kg = 0
                line.qty_meter = 0
                line.qty_yard = 0
    
    