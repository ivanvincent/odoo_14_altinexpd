from odoo import models, fields, api

class FusionProject(models.Model):
    _name = 'fusion.project'

    name = fields.Char(string='Name')


class FusionProjectLine(models.Model):
    _name = 'fusion.project.line'

    name = fields.Char(string='Name')