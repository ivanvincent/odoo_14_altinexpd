from odoo import models, fields, api

class MrpWorkcenterCategory(models.Model):
    _name = 'mrp.workcenter.category'

    name = fields.Char(string='Name')