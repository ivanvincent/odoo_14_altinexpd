from odoo import models, fields, api

class FusionProject(models.Model):
    _name = 'fusion.project'

    name = fields.Char(string='Name')
    id_fp = fields.Char(string='Id Fp')
    detail_line_ids = fields.One2many('fusion.project.line', 'fusion_project_id', 'Line')



class FusionProjectLine(models.Model):
    _name = 'fusion.project.line'

    name = fields.Char(string='Name')
    product_id = fields.Many2one('product.product', string='Product')
    fusion_project_id = fields.Many2one('fusion.project', 'Invoice')