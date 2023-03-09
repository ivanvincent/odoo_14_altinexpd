from odoo import models, fields, api, _
from odoo.exceptions import UserError


class RuteSale(models.Model):
    _inherit = 'rute.sale'


    ajuan_id      = fields.Many2one('uudp', string='Kasbon',domain=[('type', '=', 'pengajuan')],help="Kasbon")
    # penyelesaian_id      = fields.Many2one('uudp', string='Kasbon',domain=[('type', '=', 'penyelesaian')],help="Penyelesain")
    uudp_ids      = fields.One2many(related='ajuan_id.uudp_ids',string='Expense')
    realisasi_ids = fields.One2many('uudp.detail', 'rute_id', 'Realisasi')
   
    # realisasi_ids = fields.Many2many(
    #     'uudp.detail', 
    #     'realisasi_rute_sale_rel',
    #     string='Realisasi'
    #     )
    
   
