from odoo import models, fields, api

class PermintaanKain(models.Model):
    _name = 'permintaan.kain'

    name = fields.Char(string='Name')
    date_start = fields.Date(string='Date Start', required=True, )
    date_end = fields.Date(string='Date End', required=True, default=fields.Date.today())
    state = fields.Selection([("draft","Draft"),("confirm","Confirm")], default='draft', string='State')
    line_ids = fields.One2many('permintaan.kain.line', 'permintaan_kain_id', string='Line')

    def action_confirm(self):
        query = """
            select
                row_number() OVER () as no,
                pp.default_code,
                greige_id,
                sale_id,
                qty_yard_kp,
                count(1) as partai,
                (
                    qty_yard_kp * count(1)
                )
                as jumlah,
                '' as ket 
            from    
                mrp_production mp 
                join
                    product_product as pp 
                    on pp.id = mp.greige_id 
            where
                -- state = 'draft' 
                sale_id is not null 
                and mp.date_planned_start between '%s' and '%s' 
                and mp.is_permintaan_kain is null
            group by
                sale_id,
                greige_id,
                qty_yard_kp,
                pp.default_code
        """ % (self.date_start, self.date_end)
        self._cr.execute(query)
        data = []
        doc = self._cr.dictfetchall()
        for a in doc:
            sale_id = a.get('sale_id', '')
            qty = a.get('qty_yard_kp', '')
            self.env['mrp.production'].search([('sale_id', '=', sale_id),
                                            ('is_permintaan_kain', '=', False)]).write({'is_permintaan_kain': True})
            
            data.append((0, 0, {
                'default_code': a.get('default_code', ''),
                'greige_id': a.get('greige_id', ''),
                'sale_id': sale_id, 
                'qty_yard_kp': qty, 
                'partai': a.get('partai', ''),
                'jumlah': a.get('jumlah', ''), 
                'ket': a.get('ket', ''),
            }))
        if self.line_ids:
            self.line_ids = False
        self.line_ids = data
        self.state = 'confirm'
    
    def action_print_kartu_proses(self):
        line = self.line_ids
        mo_obj = self.env['mrp.production'].search([('sale_id', 'in', line.mapped('sale_id.id')),
                                                    ('qty_yard_kp', 'in', line.mapped('qty_yard_kp')),
                                                    # ('greige_id', 'in', line.mapped('greige_id.id'))
                                                    ('is_permintaan_kain', '=', True)])
        url = "/report/pdf/inherit_mrp.report_kartu_proses_new/%s" % (','.join(list(map(str, mo_obj.mapped('id')))))
        return {
            'name': 'Kartu Proses',
            'type': 'ir.actions.act_url',
            'url': url,
            'target': 'new',
        }

class PermintaanKainLine(models.Model):
    _name = 'permintaan.kain.line'
    
    default_code = fields.Char(string='Default Code')
    greige_id= fields.Many2one('product.product', string='Greige')
    sale_id = fields.Many2one('sale.order', string='No OM')
    qty_yard_kp = fields.Float(string='Price Total')
    jumlah = fields.Float(string='Yard')
    ket = fields.Char(string='Ket')
    partai = fields.Integer(string='Partai')
    permintaan_kain_id = fields.Many2one('permintaan.kain', string='Permintaan Kain')
