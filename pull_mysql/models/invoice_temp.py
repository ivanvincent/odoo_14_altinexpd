from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Invoice(models.Model):
    _name = 'invoice.temp'

    name            = fields.Char(string='Invoice')
    nota            = fields.Char(string='Nota')
    tanggal         = fields.Date(string='Tanggal')
    kd_plg          = fields.Char(string='Kode Pelanggan')
    nama_plg        = fields.Char(string='Nama Pelanggan')
    kelompok        = fields.Char(string='Kelompok')
    ket_group       = fields.Char(string='Ket Group')
    kd_plg_gr       = fields.Char(string='Kode Pelanggan Group')
    no_om           = fields.Char(string='No Om')
    surat_jalan     = fields.Char(string='Surat Jalan')
    kd_sales        = fields.Char(string='Kode Sales')
    kd_jalur        = fields.Char(string='Kode Jalur')
    no_lpb          = fields.Char(string='No LPB')
    line_ids        = fields.One2many('invoice.temp.line', 'invoice_id', string='Details',ondelete='cascade')
    
    
    def init(self):
        self.env.cr.execute("""
            CREATE OR REPLACE FUNCTION insert_invoice_temp_line(invoice_id integer, arr json)
            RETURNS void AS
            $BODY$
                DECLARE
                    inv_line json := arr;
                    inv RECORD;
                    i json;
                begin
                    FOR inv in SELECT * FROM invoice_temp WHERE id = invoice_id
                    LOOP
                        FOR i IN SELECT * FROM json_array_elements(inv_line)
                        LOOP
                            INSERT INTO invoice_temp_line (id,create_uid, create_date, write_uid, write_date,invoice_id,kd_brg,quantity,harga_retur,qty_retur,qty_tukar)	
                                VALUES (nextval('invoice_temp_line_id_seq'), inv.create_uid, inv.create_date, inv.write_uid, inv.write_date, inv.id, 
                                CAST(i->> 'kd_brg' as text),CAST(i ->> 'quantity' as double precision),CAST(i ->> 'harga_retur' as double precision),
                                CAST(i ->> 'qty_retur' as double precision),CAST(i ->> 'qty_tukar' as double precision));
                        END LOOP;
                    END loop;
                END;
            $BODY$
            LANGUAGE plpgsql VOLATILE
            COST 100;
        """)
    
    
    class Invoicelinetemp(models.Model):
        _name = 'invoice.temp.line'
        
        invoice_id      = fields.Many2one('invoice.temp', string='Invoice',index=True)
        kd_brg          = fields.Char(string='Kode Barang')
        quantity        = fields.Float(string='Quantity')
        satuan_harga    = fields.Float(string='Satuan Harga')
        qty_tukar       = fields.Float(string='Qty Tukar')
        qty_retur       = fields.Float(string='Qty Retur')
        harga_retur     = fields.Float(string='Harga Retur')
            