from odoo import models, fields, api, _
from odoo.exceptions import UserError


class TypeShip(models.Model):
    _name = 'type.ship'

    name = fields.Char(string='Name')

class TypePacking(models.Model):
    _name = 'type.packing'

    name = fields.Char(string='Name')

class TypeAccessories(models.Model):
    _name = 'type.accessories'

    name = fields.Char(string='Name')

class TypeHangTag(models.Model):
    _name = 'type.hangtag'

    name = fields.Char(string='Name')


class MrpMachineCategory(models.Model):
    _name = 'mrp.machine.category'
    _description = 'Category of Machine'
    
    name        = fields.Char(string='Category')
    description = fields.Char(string='Description')

class MrpProductionFinalSet(models.Model):
    _name = 'mrp.production.final.set'
    _description = 'Final Set'
    
    name        = fields.Char(string='Final Set')
    description = fields.Char(string='Description')
    

   
class MrpMachine(models.Model):
    _name = 'mrp.machine'

    name          = fields.Char(string='Name')
    number        = fields.Char(string='Number')
    location_id   = fields.Many2one('stock.location', string='Location')
    is_under_mtc  = fields.Boolean(string='Check ?')
    purchase_date = fields.Date(string='Purchase Date')
    panjang       = fields.Integer(string='Panjang')
    berat         = fields.Integer(string='Berat')
    expire_date   = fields.Date(string='Expire Date')
    eff           = fields.Float(string='EFF')
    rpm           = fields.Integer(string='RPM')
    lebar         = fields.Float(string='Lebar')
    kelompok      = fields.Char(string='Kelompok')
    category_id   = fields.Many2one('mrp.machine.category', string='Category')
    partner_id    = fields.Many2one('res.partner', string='Supplier')
    max_batch     = fields.Integer(string='Max Batch',default=7)
    volume_air    = fields.Float(string='Volume Air / Liter')
    speed         = fields.Float(string='Speed')
    nozzle        = fields.Integer(string='Nozzle')
    jarum         = fields.Integer(string='Jarum')
    description   = fields.Text(string='Description')
    is_active     = fields.Boolean(string='Is Active')


    def name_get(self):
        result = []
        for machine in self:
            result.append((machine.id, str(machine.name) + ' - ' + str(machine.number)))
        return result
    
    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        res_search = False
        res = self.search([ '|',('name',operator,name),('number',operator,name)] + args, limit=limit)
        res_search = res.name_get()
        return res_search

class MakloonGrade(models.Model):
    _name = 'makloon.grade'

    name = fields.Char(string='Name')
    account_input_id = fields.Many2one('account.account', string='Account Input')
    kelompok = fields.Char(string='Kelompok')


class MakloonWarna(models.Model):
    _name = 'makloon.warna'

    name = fields.Char(string='Name')



class MakloonDesign(models.Model):
    _name = 'makloon.design'

    name = fields.Char(string='Name')
    motive = fields.Char(string='Motive')

class FabricBase(models.Model):
    _name = 'fabric.base'

    name = fields.Char(string='Name')
    
    
class ProcessCategory(models.Model):
    _name = 'process.category'
    
    
    name = fields.Char(string='Process Category')
    
    
class MarketingCategory(models.Model):
    _name = 'marketing.category'
    
    
    name = fields.Char(string='Marketing Category')
class ProcessType(models.Model):
    _name = 'process.type'

    name        = fields.Char(string='Name')
    category_id = fields.Many2one('process.category', string='Process Category')

class MasterProses(models.Model):
    _name = 'master.proses'

    name = fields.Char(string='Name')
    price = fields.Float(string='Price')
    description = fields.Text(string='Description')
    master_wip_id = fields.Many2one('master.wip', string='Master Wip')

class MasterParameter(models.Model):
    _name = 'master.parameter'

    name = fields.Char(string='Name')


class GroupProduct(models.Model):
    _name = 'group.product'

    name        = fields.Char(string='Name')
    description = fields.Text(string='Description')
    
    
class LineProduct(models.Model):
    _name = 'line.product'

    name        = fields.Char(string='Name')
    description = fields.Text(string='Description')
    
    
class MerkProduct(models.Model):
    _name = 'merk.product'

    name        = fields.Char(string='Name')
    description = fields.Text(string='Description')