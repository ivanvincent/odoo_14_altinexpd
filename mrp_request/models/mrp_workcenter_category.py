from odoo import models, fields, api

class MrpWorkcenterCategory(models.Model):
    _name = 'mrp.workcenter.category'

    name = fields.Char(string='Name')
    parent_category = fields.Selection([
    ('mentah', 'MENTAH'),
    ('matang', 'MATANG')],
    string='Parent Category')