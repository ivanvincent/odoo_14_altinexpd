from odoo import models, fields, api

class MasterRequire(models.Model):
    _name = 'master.require.new'
    _order = "urutan asc"

    name = fields.Char(string='Name')
    jenis_ids = fields.Many2many(
        comodel_name='master.jenis.new', 
        string='Jenis',
        compute="_get_jenis_ids"
        )
    active = fields.Boolean(string='Active ?', default=True)
    urutan = fields.Integer(string='Urutan', default=99)
    kelompok = fields.Selection([('holder','Holder'),('holder_cap','Holder Cap'),('tip','Tip'),('gen_item','General Items')], string='Kelompok')


    def _get_jenis_ids(self):
            for line in self:
                spec = self.env['specifications.new'].search([('spec_id', '=', line.id)])
                line.jenis_ids = [(6, 0, spec.mapped('jenis_id.id'))]
    