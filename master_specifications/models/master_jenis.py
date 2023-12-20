from odoo import models, fields, api

class MasterJenis(models.Model):
    _name = 'master.jenis'

    name = fields.Char(string='Name')
    active = fields.Boolean(string='Active ?', default=True)
    sequence_id = fields.Many2one('ir.sequence', string='Sequence')
    qty_ids = fields.Many2many(comodel_name='master.qty', string="Quantity")
    type = fields.Selection([('produk','PRODUK'),('jasa','JASA')], string='Type')