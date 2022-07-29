from odoo import models, fields, api, _
from odoo.exceptions import UserError
import mysql.connector

import logging
_logger = logging.getLogger(__name__)

SQL_HOST     = "pmti.ddns.net"
# SQL_HOST     = "43.248.212.142"
# SQL_HOST     = "10.0.10.199"
SQL_USER     = 'pmti'
SQL_PASSWORD = 'rahasiakudewe'
SQL_DATABASE = 'pmti'
SQL_PORT     = 3367
# SQL_PORT     = 3306


class PullCronSJ(models.Model):
    _name = 'pull.cron.sj.greige'

    name            = fields.Char(string='Surat Jalan')
    tanggal         = fields.Date(string='Tanggal')
    dep             = fields.Char(string='Department')
    amount_total    = fields.Float(compute='_compute_total', string='Total Qty', store=False)
    amount_roll     = fields.Float(compute='_compute_total', string='Total Roll', store=False)
    
    
    @api.depends('line_ids')
    def _compute_total(self):
        for greige in self:
            amount_total = sum(greige.line_ids.mapped('quantity'))
            greige.amount_total = amount_total
            greige.amount_roll = len(greige.line_ids)
    
    line_ids        = fields.One2many('pull.cron.sj.greige.line', 'pull_id', string='Line')
    
    
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
        
    
    
    def action_pull(self,start_date,end_date):
        sj_form = self.env.ref('pull_mysql.pull_cron_js_greige_form', raise_if_not_found=False)
        sj_tree = self.env.ref('pull_mysql.pull_cron_js_greige_tree', raise_if_not_found=False)
        connection = self.connect_mysql()
        cr = connection.cursor(dictionary=True)
        updated = None
        # pulled_sj = self.check_pulled_sj(self.start_date,self.end_date)
        pulled = []
        # if  pulled_sj == 0:
        query = """  
                    SELECT a.jenis_kain,a.kd_brg,a.potong,b.kd_kain,c.potong,
                        b.tgl_srt_jln,b.barcode,b.lusi,b.pakan,b.pic,b.lebar,b.panjang,
                        b.unit_prod,b.grade,b.tgl_prod,b.keterangan,a2.kelompok,
                        b.no_mesin,b.no_beam,b.srt_jln,c.Gramasi_finish as gramasi_finish,c.Gramasi_grey as gramasi_grey
                        FROM barang a
                        LEFT JOIN inspect b ON a.kd_brg = b.kd_kain 
                        LEFT JOIN tekstil_pmti.barang a2 ON b.kd_kain = a2.kd_brg
                        LEFT JOIN kontruksi c ON a.kd_brg = c.kd_design 
                        WHERE b.tgl_srt_jln BETWEEN '%s' and '%s' ORDER BY srt_jln DESC
                """%(start_date,end_date)
                    # select * from inspect  where tgl_srt_jln BETWEEN '%s' and '%s' and status_isp = 1 ORDER BY srt_jln DESC

        cr.execute(query)
        results = cr.fetchall()
        line_ids = []
        for idx,current in enumerate(results):
            prev = results[idx - 1].get('srt_jln') if idx >= 1 else None
            nxt = results[idx + 1].get('srt_jln') if idx < len(results) - 1 else None
            # nxt = results[idx + 1].get('srt_jln') if idx < len(results) - 1 else None
            
            product = self.env['product.product'].search([('default_code','=',current.get('kd_kain'))],limit =1)
            if not product :
                product_template = self.env['product.template'].sudo().search([('name','=',current.get('jenis_kain'))],limit=1)
                if product_template:
                    greige_attr = self.env['product.attribute.value'].sudo().search([('name','=',current.get('kd_kain'))],limit=1)
                    if not greige_attr:
                        greige_attr = greige_attr.sudo().create({
                            "attribute_id":28,
                            "name": current.get('kd_kain'),
                        })
                    
                    greige_code_attr = self.env['product.template.attribute.line'].sudo().search([('product_tmpl_id','=',product_template.id),('attribute_id','=',28)],limit=1)
                    if greige_code_attr:
                        greige_code_attr.sudo().write({
                            "value_ids":[(4,greige_attr.id)],
                        })
                    else:
                        greige_code_attr.sudo().create({
                            'product_tmpl_id': product_template.id,
                            'attribute_id': 28, 
                            'value_ids': [(4,greige_attr.id)]
                        })
                    
                    product_ids = self.env['product.product'].sudo().search([('product_tmpl_id','=',product_template.id)]).filtered(lambda x: x.product_template_attribute_value_ids.filtered(lambda x:x.product_attribute_value_id.id == greige_attr.id))
                    product = product_ids
                    for prod in product_ids:
                        prod.sudo().write({
                                "tracking":'lot',
                                "pic":current.get('pic'),
                                "lebar":current.get('lebar'),
                                "kelompok":current.get('kelompok'),
                                "categ_id":127,
                                "type":'product',
                                "gramasi_finish":current.get('gramasi_finish'),
                                "default_code": current.get('kd_kain'),
                                "gramasi_greige":current.get('gramasi_grey'),
                                
                            })
                    
                    # line.product_id = product_ids.id
                        
                else:
                    product_template = product_template.sudo().create({
                        "name":current.get('jenis_kain'),
                        # "product_tmpl_id":product_template.id,
                        "uom_id":46,
                        "uom_po_id":46,
                        "tracking":'lot',
                        # "pic":line.pic,
                        # "lebar":line.lebar,
                        "categ_id":127,
                        "type":'product',
                        # "gramasi_finish":line.gramasi_finish,
                        "default_code": current.get('kd_kain'),
                        # "gramasi_greige":line.gramasi_greige,
                        
                    })
                    greige_attr = self.env['product.attribute.value'].sudo().search([('name','=',current.get('kd_kain'))],limit=1)
                    if not greige_attr:
                        greige_attr = greige_attr.sudo().create({
                            "attribute_id":28,
                            "name": current.get('kd_kain'),
                        })
                    
                    greige_code_attr = self.env['product.template.attribute.line'].sudo().search([('product_tmpl_id','=',product_template.id),('attribute_id','=',28)],limit=1)
                    if greige_code_attr:
                        greige_code_attr.sudo().write({
                            "value_ids":[(4,greige_attr.id)],
                        })
                    else:
                        greige_code_attr.sudo().create({
                            'product_tmpl_id': product_template.id,
                            'attribute_id': 28,
                            'value_ids': [(4,greige_attr.id)]
                        })
                    
                    
                    product_ids = self.env['product.product'].sudo().search([('product_tmpl_id','=',product_template.id)])
                    for prod in  product_ids:
                        if prod: 
                            prod.sudo().write({
                                "tracking":'lot',
                                "pic":current.get('pic'),
                                "lebar":current.get('lebar'),
                                "categ_id":127,
                                "uom_id":46,
                                "uom_po_id":46,
                                "type":'product',
                                "gramasi_finish":current.get('gramasi_finish'),
                                "default_code": current.get('kd_kain'),
                                "gramasi_greige":current.get('gramasi_grey'),
                                "kelompok":current.get('kelompok'),
                            })
                        product = prod
            line = {
                "no_mesin":current.get('no_mesin'),
                "no_beam":current.get('no_beam'),
                "tanggal":current.get('tgl_srt_jln'),
                "barcode":current.get('barcode'),
                "kd_kain":current.get('kd_kain'),
                "lusi":current.get('lusi'),
                "pakan":current.get('pakan'),
                "product_id":product.id,
                "kelompok":current.get('kelompok'),
                "pic":current.get('pic'),
                "grade":current.get('grade'),
                "lebar":current.get('lebar'),
                "std_potong":current.get('potong'),
                "quantity":current.get('panjang'),
                "nama_barang":current.get('jenis_kain'),
                "gramasi_finish":current.get('gramasi_finish'),
                "gramasi_greige":current.get('gramasi_grey'),
                "dep":current.get('unit_prod'),
                "tanggal_prod":current.get('tgl_prod'),   
                "keterangan":current.get('keterangan'),   
                "name":current.get('srt_jln'),
            }
            
            line_ids.append((0,0,line))
            
            if current.get('srt_jln') != nxt:
                sj = self.env['pull.cron.sj.greige'].create({
                "name":current.get('srt_jln'),   
                "tanggal":current.get('tgl_srt_jln'),   
                "line_ids":line_ids,   
                })
                _logger.warning('='*40)
                _logger.warning('PULL GREIGE')
                _logger.warning(current.get('srt_jln'))
                _logger.warning(nxt)
                # _logger.warning(prev)
                _logger.warning('='*40)
                _logger.warning(sj.name)
                _logger.warning('='*40)
                line_ids = []
        
        
        
        # for result in results:
        #     query = self.update_state_kd_keluar(result.get('kd_keluar'))
        #     cr.execute(query)
        
        connection.commit()   
        cr.close()
        self.disconnect_mysql()    
        
            
        return {
            'type': 'ir.actions.act_window',
            'name': 'Surat Jalan Greige',
            'res_model': 'pull.cron.sj.greige',
            'views': [(sj_tree.id, 'tree'),(sj_form.id, 'form')],
            'target': 'current',
        }
        
    
    
    



class PullCronSJLine(models.Model):
    _name = 'pull.cron.sj.greige.line'
    
    def _get_product(self):
        for line in self:
            product = self.env['product.product'].search([('default_code','=',line.kd_kain)],limit =1)
            if product:
                line.product_id = product.id
            else :
                product_template = self.env['product.template'].sudo().search([('name','=',line.nama_barang)],limit=1)
                if product_template:
                    greige_attr = self.env['product.attribute.value'].sudo().search([('name','=',line.kd_kain)],limit=1)
                    if not greige_attr:
                        greige_attr = greige_attr.sudo().create({
                            "attribute_id":28,
                            "name": line.kd_kain,
                        })
                    
                    greige_code_attr = self.env['product.template.attribute.line'].sudo().search([('product_tmpl_id','=',product_template.id),('attribute_id','=',28)],limit=1)
                    if greige_code_attr:
                        greige_code_attr.sudo().write({
                            "value_ids":[(4,greige_attr.id)],
                        })
                    else:
                        greige_code_attr.sudo().create({
                            'product_tmpl_id': product_template.id,
                            'attribute_id': 28, 
                            'value_ids': [(4,greige_attr.id)]
                        })
                    
                    product_ids = self.env['product.product'].sudo().search([('product_tmpl_id','=',product_template.id)]).filtered(lambda x: x.product_template_attribute_value_ids.filtered(lambda x:x.product_attribute_value_id.id == greige_attr.id))
                    line.product_id = product_ids.id
                        
                else:
                    _logger.warning(line.product_id)
                    product_template = product_template.sudo().create({
                        "name":line.nama_barang,
                        # "product_tmpl_id":product_template.id,
                        "uom_id":46,
                        "uom_po_id":46,
                        "tracking":'lot',
                        # "pic":line.pic,
                        # "lebar":line.lebar,
                        "categ_id":127,
                        "type":'product',
                        # "gramasi_finish":line.gramasi_finish,
                        # "default_code": line.kd_kain,
                        # "gramasi_greige":line.gramasi_greige,
                        
                    })
                    greige_attr = self.env['product.attribute.value'].sudo().search([('name','=',line.kd_kain)],limit=1)
                    if not greige_attr:
                        greige_attr = greige_attr.sudo().create({
                            "attribute_id":28,
                            "name": line.kd_kain,
                        })
                    
                    greige_code_attr = self.env['product.template.attribute.line'].sudo().search([('product_tmpl_id','=',product_template.id),('attribute_id','=',28)],limit=1)
                    if greige_code_attr:
                        greige_code_attr.sudo().write({
                            "value_ids":[(4,greige_attr.id)],
                        })
                    else:
                        greige_code_attr.sudo().create({
                            'product_tmpl_id': product_template.id,
                            'attribute_id': 28,
                            'value_ids': [(4,greige_attr.id)]
                        })
                    
                    
                    product_ids = self.env['product.product'].sudo().search([('product_tmpl_id','=',product_template.id)])
                    if product_ids: 
                        product_ids.sudo().write({
                            "tracking":'lot',
                            "pic":line.pic,
                            "lebar":line.lebar,
                            "categ_id":127,
                            "type":'product',
                            "gramasi_finish":line.gramasi_finish,
                            "default_code": line.kd_kain,
                            "gramasi_greige":line.gramasi_greige,
                        })
                        _logger.warning('='*40)
                        _logger.warning('Product ids')
                        _logger.warning(product_ids)
                        _logger.warning(product_ids.id)
                        _logger.warning(product_ids.name)
                        _logger.warning('='*40)
                        line.product_id = product_ids.id
                    else:
                        line.product_id = False
                        
                        

    pull_id         = fields.Many2one('pull.cron.sj.greige', string='Pull')
    product_id      = fields.Many2one('product.product', string='Product')
    nama_barang     = fields.Char(string='Nama Barang')
    tanggal         = fields.Date(string='Tanggal')
    tanggal_prod    = fields.Date(string='Tanggal Produksi')
    dep             = fields.Char(string='Department')
    name            = fields.Char(string='Surat Jalan')
    kelompok        = fields.Char(string='Kelompok')
    keterangan      = fields.Text(string='Keterangan')
    grade           = fields.Char(string='Grade')
    quantity        = fields.Float(string='Quantity')
    barcode         = fields.Char(string='Barcode')
    lusi            = fields.Char(string='Lusi')
    gramasi_finish  = fields.Float(string='Gramasi Finish')
    gramasi_greige  = fields.Float(string='Gramasi Greige')
    pakan           = fields.Char(string='Pakan')
    no_beam         = fields.Char(string='No Beam')
    pic             = fields.Char(string='Pic')
    lebar           = fields.Char(string='Lebar')
    kd_kain         = fields.Char(string='Kode Kain')
    no_mesin        = fields.Char(string='No Mesin')
    std_potong      = fields.Float(string='STD Potong')