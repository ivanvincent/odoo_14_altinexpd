from urllib import request
from odoo import fields, models, api, _ 
from odoo.http import fields, models, api, _ 
from odoo.exceptions import UserError
from datetime import datetime
import mysql.connector
import ast
from odoo.tools.float_utils import float_compare, float_is_zero, float_repr, float_round
import logging
_logger = logging.getLogger(__name__)


SQL_HOST     = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
# SQL_HOST     = "43.248.212.142"
# SQL_HOST     = "10.0.10.199"
SQL_USER     = 'pmti'
SQL_PASSWORD = 'rahasiakudewe'
SQL_DATABASE = 'tekstil_pmti'
SQL_DATABASE_2 = 'pmti'
SQL_PORT     = 3367
# SQL_PORT     = 3306





class PullSqlWizard(models.TransientModel):

    _name = 'pull.mysql.wizard'
    
    
    
    
    sql_connection = None
    
    
    @api.model
    def _default_location(self):
        location_id = self.env.user.default_warehouse_ids.lot_stock_id.mapped('id')
        if len(location_id) > 1:
            return location_id[1]
        elif not location_id:
            return False
        return location_id[0]
    
    @api.model
    def _default_warehouse(self):
        warehouse_id = self.env.user.default_warehouse_ids.mapped('id')
        if len(warehouse_id) > 1:
            return warehouse_id[1]
        elif not warehouse_id:
            return False
        return warehouse_id[0]
    
    
    
    start_date   = fields.Date(string='Start Date',default=fields.Date.today())
    end_date     = fields.Date(string='End Date',default=fields.Date.today())
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse',
        domain = lambda self : [('id','in',self.env.user.default_warehouse_ids.ids)],
        default=lambda self: self._default_warehouse())
    warehouse_code = fields.Char(related='warehouse_id.code', string='Code')
    location_id  = fields.Many2one('stock.location', string='Location',default=lambda self: self._default_location())
    surat_jalan = fields.Char(string='Surat Jalan')
    # pull_type = fields.Selection([("day","By Day"),("surat_jalan","Surat Jalan")], string='Pull Type')
    is_connected = fields.Boolean(string='Connected',compute='get_mysql_connection')
    
    @property
    def get_connection(self):
        return self.sql_connection
    
    @api.model
    def get_mysql_connection(self):
        connection  = mysql.connector.connect(user=SQL_USER,
                                            password=SQL_PASSWORD,      
                                            host=SQL_HOST,
                                            charset='utf8',
                                            database=SQL_DATABASE,port=SQL_PORT,use_pure=True)
        if connection:
            self.is_connected = True 
        else:
            self.is_connected = False 
    
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
        
        
    def generate_lot(self,vals={}):
        if vals:
            columns = ['name', 'product_id', 'product_category','location_id','product_uom_id', 
                       'tanggal_produksi', 'rack_id','company_id','no_warna','grade_id','no_om',
                       'lebar','pic','kelompok','cone','harga'] 
            
            query = """ INSERT INTO stock_production_lot (%s)
                        VALUES %s RETURNING id"""%\
                        (", ".join('"{}"'.format(column) for column in columns),tuple(vals.values()))
            self._cr.execute(query.replace('False', 'NULL'))
            return self._cr.fetchall()[0][0]
        
    def generate_move(self,vals={}):
        if vals:
            columns = ['name', 'date','product_id','location_id','product_uom', 'product_uom_qty', 'location_dest_id','company_id','procure_method'] 
            query = """ INSERT INTO stock_move (%s)
                        VALUES %s RETURNING id"""%\
                        (", ".join('"{}"'.format(column) for column in columns),tuple(vals.values()))
            self._cr.execute(query.replace('False', 'NULL'))
            return self._cr.fetchall()[0][0]
        
        
        

    def update_state_barcode(self,barcode,dep):
        query = """UPDATE barcode set status_odoo = 1 WHERE  barcode = '%s' AND kd_dep = '%s' """%(barcode,dep)
        
        return query 
    
    def cancel_state_barcode(self,barcode,dep):
        query = """UPDATE barcode set status_odoo = 0 WHERE  barcode = '%s' AND kd_dep = '%s' """%(barcode,dep)
        
        return query 
    
    
    def action_cancel(self):
        connection = self.connect_mysql()
        cr = connection.cursor(dictionary=True)
        if  self.warehouse_id.code == "GDG":
            query = self.query_gdg()
        
        elif  self.warehouse_id.code == "GDJU":
            query = self.query_gdj()
        
        cr.execute(query)
        results = cr.fetchall()
        
        for result in results:
            self.cancel_state_barcode(result.get('barcode',self.warehouse_id.code))
            
        
        self.disconnect_mysql()
        
    
    def query_gdg(self):
        query = """ 
            SELECT 
                a.barcode,a.rak,a.kd_brg,LTRIM(RTRIM(b.nama)) as nama,a.lot,a.grade,a.quantity,
                a.satuan,a.tgl_prod, a.pic,a.lebar,b.kelompok 
            FROM 
                barcode a,
                barang b 
            WHERE 
                a.kd_brg=b.kd_brg 
                AND a.kd_dep='GDG' 
                AND a.status in (1,2)
                AND a.status_odoo != 1 
                AND a.tgl_prod BETWEEN '%s' AND '%s' 
        """%(self.start_date.strftime('%Y-%m-%d'),self.end_date.strftime('%Y-%m-%d'))
        
        return query 
    
    def query_gdj(self):
        query = """ 
            SELECT 
                a.barcode,a.rak,a.kd_brg, LTRIM(RTRIM(b.nama)) as nama, a.lot, a.no_warna,a.grade,
                a.quantity,a.satuan,a.tgl_prod, a.cone,a.noom,
                b.kelompok,c.harga,d.kategori
            FROM 
                barcode a, 
                barang b ,
                om c ,
                kategori d
            WHERE 
                a.kd_brg=b.kd_brg 
                AND a.kd_dep ='GDJ' 
                AND a.noom = c.noom 
                AND a.status in (1,2)
                AND b.kat = d.kode
                AND a.status_odoo != 1 
                AND a.tgl_prod BETWEEN '%s' AND '%s' 
        """%(self.start_date.strftime('%Y-%m-%d'),self.end_date.strftime('%Y-%m-%d'))
        
        return query 
    
    def query_gdo(self):
        query = """ 
                SELECT 
                    d.status_reproses,
                    d.nama_proses,a.status_pemakaian,
                    a.tanggal_load,c.no_mesin,
                    c.kd_proses,
                    a.id,
                    a.kd_brg,
                    if(a.satuan='gr/yrd',
                    a.quantity_actual/1000,a.quantity_actual) as quantity,
                    a.no,
                    e.kategori as kategori,
                    a.no_jadwal,
                    b.nama,b.satuan
                FROM 
                    proses_jadwal_resep a , 
                    barang b , proses_jadwal c , 
                    proses d , kategori e 
                WHERE 
                    c.kd_proses=d.kd_proses 
                    AND a.no_jadwal=c.no 
                    AND a.kd_brg=b.kd_brg
                    AND b.kat = e.kode 
                    AND a.kd_brg <> ''
                AND a.tanggal_load between '%s' AND '%s'
        """%(self.start_date.strftime('%Y-%m-%d'),self.end_date.strftime('%Y-%m-%d'))
        
        return query
    
    
    def _check_lot_by_date(self,start_date,end_date):
        query = """ SELECT name FROM stock_production_lot WHERE tanggal BETWEEN '%s' AND '%s' """%(start_date,end_date)
        self._cr.execute(query)
        results = self._cr.rowcount 
        return results
        
    
    # def create_product(self):
    
    def action_pull_greige(self):
        return self.env['pull.cron.sj.greige'].action_pull(self.start_date.strftime('%Y-%m-%d'),self.end_date.strftime('%Y-%m-%d'))
        

    def action_pull(self):
        connection = self.connect_mysql()
        cr = connection.cursor(dictionary=True)
        query = None
        def remove_key(d,key):
                r = dict(d)
                del r[key]
                return r
        if  self.warehouse_id.code == "GDG":
            query = self.query_gdg()
            
        
        elif  self.warehouse_id.code == "GDJU":
            query = self.query_gdj()
        
        elif  self.warehouse_id.code == "DF1":
            query = self.query_gdo()
        
        
        cr.execute(query)
        move_ids = []
        moveline_ids = []
        results = cr.fetchall()
        fabric_wh = self.warehouse_id.code in ['GDG','GDJU']
        if results:
            for result in results:
                rack = None
                grade_id = None
                product_id = None
                if fabric_wh: 
                    rack = self.env['master.rack'].sudo().search([('name','=',result.get('rak'))],limit=1)
                    grade_id = self.env['makloon.grade'].sudo().search([('name','=',result.get('grade'))],limit=1)
                    if not rack and result.get('rak'):
                        rack.sudo().create({"name":result.get('rak'),"location_id":self.location_id.id,"warehouse_id":self.warehouse_id.id})
                    if not grade_id and result.get('grade'):
                        grade_id.sudo().create({"name":result.get('grade')})
                else:
                    machine_id = self.env['mrp.machine'].sudo().search([("number",'=',result.get("no_mesin"))],limit =1)
                product_id = self.env['product.product'].sudo().search([('default_code','=',result.get('kd_brg'))],limit=1)
                if not product_id:
                    # raise UserError('Product %s Belum Ada Di System Odoo\n dengan kode barang %s'%(result.get('nama'),result.get('kd_brg')))
                    product_category = self.env['product.category'].sudo().search([('name','=',result.get('kategori'))],limit=1)
                    if not product_category:
                        raise UserError('Kategori  %s Belum Ada Di System Odoo'%(result.get('kategori')))
                    satuan = result.get('satuan').upper()
                    if satuan == 'GR/YARD':
                        satuan = 'GR/YRD'
                    product_uom = self.env['uom.uom'].sudo().search([('name','=',satuan)],limit=1)
                    if not product_uom:
                        raise UserError('Satuan untuk Product %s Tidak Ditemukan\n dengan kode barang %s'%(result.get('nama'),result.get('kd_brg')))
                    product_id = self.env['product.product'].with_context(generatorless=False).sudo().create({
                                "name":result.get('nama'),
                                "default_code":result.get('kd_brg'),
                                "uom_id": product_uom.id,
                                "uom_po_id":product_uom.id,
                                "categ_id": product_category.id,
                                "tracking": 'lot' if fabric_wh else 'none',
                                "type": 'product'
                        })
                elif product_id and product_id.tracking != 'lot' and fabric_wh:
                    raise UserError('Product %s Belum Di Set Tracking By Lots \n dengan kode barang %s'%(result.get('nama'),result.get('kd_brg')))
                rounding = self.env['decimal.precision'].precision_get('Product Unit of Measure')
                uom_quantity = product_id.uom_id._compute_quantity(float(result.get('quantity')), product_id.uom_id, rounding_method='HALF-UP')
                uom_quantity = float_round(uom_quantity, precision_digits=rounding)
                
                
                if fabric_wh:
                    lot_template = {
                        "name":str(result.get('barcode')),
                        "product_id":product_id.id,
                        "product_category":product_id.categ_id.id,
                        "location_id":self.location_id.id,
                        "product_uom_id":product_id.uom_id.id,
                        "tanggal_produksi":result.get('tgl_prod').strftime('%Y-%m-%d'),
                        "rack_id":rack.id if rack else False,
                        "company_id":self.env.company.id,
                        "no_warna": result.get('no_warna') or False,
                        "grade_id": grade_id.id ,
                        "no_om": result.get('noom')  or False,
                        "lebar": result.get('lebar')  or False,
                        "pic": result.get('pic')  or False,
                        "kelompok": result.get('kelompok')  or False,
                        "cone": result.get('cone')  or False,
                        "harga": float(result.get('harga'))  or False,
                    }
                    
                    lot_id = self.generate_lot(lot_template)
                    
                    moveline_template = {
                        'product_id': product_id.id,
                        'lot_id': lot_id,
                        'grade_id': grade_id.id,
                        'lot_name': result.get('barcode'),
                        'warna':result.get('no_warna'),
                        'product_uom_id': product_id.uom_id.id,
                        'location_id': 15,
                        'qty_done': uom_quantity,
                        # 'product_uom_qty':uom_quantity,
                        'location_dest_id': self.location_id.id,
                        'company_id':self.env.company.id,
                        
                    }
                    # moveline_ids.append((0,0,moveline_template))
                    
                    move_template = {
                        'name': product_id.name,
                        'date':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'product_id': product_id.id,
                        'location_id': 15,
                        'product_uom': product_id.uom_id.id,
                        'product_uom_qty': uom_quantity,
                        'picking_type_id':self.warehouse_id.in_type_id.id,
                        'location_dest_id': self.location_id.id,
                        'company_id': self.env.company.id,
                        'procure_method':'make_to_stock',
                        # 'move_line_ids':moveline_ids
                    }
                    move_ids.append((0,0,move_template))
                    moveline_ids.append((0,0,moveline_template))
                else:
                    move_template = {
                        'name': product_id.name,
                        'date':datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'product_id': product_id.id,
                        'location_id': self.location_id.id,
                        'product_uom': product_id.uom_id.id,
                        'quantity_done': uom_quantity,
                        'product_uom_qty': uom_quantity,
                        'picking_type_id':self.warehouse_id.int_type_id.id,
                        'location_dest_id': 1174, 
                        'company_id': self.env.company.id,
                        'machine_id':machine_id.id,
                        'kd_proses':result.get('kd_proses'),
                        'kd_keluar':result.get('kd_keluar'),
                        'hand3':result.get('hand3'),
                    }
                    move_ids.append((0,0,move_template))
            
            picking_template = {
                'picking_type_id': self.warehouse_id.in_type_id.id if fabric_wh else self.warehouse_id.int_type_id.id,
                'date': fields.Date.today(),
                'scheduled_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'location_id': 15 if fabric_wh else self.location_id.id,
                'location_dest_id': self.location_id.id if fabric_wh else 1174,
                'immediate_transfer': False,
                'move_line_nosuggest_ids': moveline_ids if fabric_wh else False,
                'move_lines': move_ids,
                }
            
            if not fabric_wh:
                picking_template = remove_key(picking_template,"move_line_nosuggest_ids")


            picking = self.env['stock.picking'].sudo().create(picking_template)
            picking.action_confirm()
            picking.sudo().message_post_with_view('mail.message_origin_link',
                                                    values={'self': picking, },
                                                    subtype_id=self.env.ref('mail.mt_note').id)
            
            connection.commit()   
            cr.close()
            self.disconnect_mysql()
            if picking:
                return {
                    'name': 'Transfer',
                    'view_mode': "form",
                    'res_model': 'stock.picking',
                    'type': 'ir.actions.act_window',
                    'target': 'current',
                    'res_id': picking.id,}
        else:
            raise UserError('No result ..')


