from odoo import models, fields, api

class MasterRequire(models.Model):
    _name = 'master.require'

    name = fields.Char(string='Name')
    jenis_ids = fields.Many2many(
        comodel_name='master.jenis', 
        string='Jenis',
        # compute="_get_jenis_ids"
        )
    active = fields.Boolean(string='Active ?', default=True)


    # def _get_jenis_ids(self):
    #         for line in self:
    #             spec = self.env['specifications'].search([('spec_id', '=', line.id)])
    #             line.jenis_ids = [(6, 0, spec.mapped('jenis_id.id'))]
    