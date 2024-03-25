from odoo import models, fields, api

class BasicSpecification(models.Model):
    _name = 'basic.specification'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK","MONOBLOCK")], string='Type')

class Material(models.Model):
    _name = 'material'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK","MONOBLOCK")], string='Type')

class BoreType(models.Model):
    _name = 'bore.type'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class SingleOrMultiTip(models.Model):
    _name = 'single.or.multi.tip'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK","MONOBLOCK")], string='Type')

class DieScrew(models.Model):
    _name = 'die.screw'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class OptionalTaperedBore(models.Model):
    _name = 'optional.tapered.bore'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class HeatTreatment(models.Model):
    _name = 'heat.treatment'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK","MONOBLOCK")], string='Type')

class SurfaceTreatment(models.Model):
    _name = 'surface.treatment'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK","MONOBLOCK")], string='Type')

class CustomAdjustment(models.Model):
    _name = 'custom.adjustment'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK","MONOBLOCK")], string='Type')

class FatOption(models.Model):
    _name = 'fat.option'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK","MONOBLOCK")], string='Type')

class DieSettingAligner(models.Model):
    _name = 'die.setting.aligner'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')