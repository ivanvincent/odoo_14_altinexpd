from odoo import models, fields, api

class HolderSpecification(models.Model):
    _name = 'holder.specification'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class HolderPosition(models.Model):
    _name = 'holder.position'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class HolderMaterial(models.Model):
    _name = 'holder.material'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class DustCupConfiguration(models.Model):
    _name = 'dust.cup.configuration'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK", "MONOBLOCK")], string='Type')

class KeywayConfiguration(models.Model):
    _name = 'keyway.configuration'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK", "MONOBLOCK")], string='Type')

class KeywayPosition(models.Model):
    _name = 'keyway.position'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK", "MONOBLOCK")], string='Type')

class HeadFlatExtension(models.Model):
    _name = 'head.flat.extension'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK", "MONOBLOCK")], string='Type')

class HolderHeatTreatment(models.Model):
    _name = 'holder.heat.treatment'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class HolderSurfaceTreatment(models.Model):
    _name = 'holder.surface.treatment'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class TipShape(models.Model):
    _name = 'tip.shape'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class TipPosition(models.Model):
    _name = 'tip.position'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class TipMaterial(models.Model):
    _name = 'tip.material'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class TipHeatTreatment(models.Model):
    _name = 'tip.heat.treatment'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class TipSurfaceTreatment(models.Model):
    _name = 'tip.surface.treatment'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class HolderCap(models.Model):
    _name = 'holder.cap'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class HolderCapBore(models.Model):
    _name = 'holder.cap.bore'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')

class Hobb(models.Model):
    _name = 'hobb'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK", "MONOBLOCK")], string='Type')

class Hobb(models.Model):
    _name = 'drawing'

    name = fields.Char(string='Name')
    desc = fields.Char(string='Desc')
    price = fields.Float(string='Price')
    type = fields.Selection([("DIE","DIE"),("MULTIPART","MULTIPART"),("MONOBLOCK", "MONOBLOCK")], string='Type')