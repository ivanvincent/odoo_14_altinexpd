from odoo import models, fields, api

class MasterRequire(models.Model):
    _name = 'master.require'

    name = fields.Char(string='Name')
    jenis_ids = fields.Many2many(
        comodel_name='master.jenis', 
        string='Jenis'
        )
    active = fields.Boolean(string='Active ?', default=True)
    