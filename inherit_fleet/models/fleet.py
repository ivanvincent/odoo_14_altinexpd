from odoo import models, fields, api, _
from odoo.exceptions import UserError

class FleetVehicle(models.Model):
    _inherit = 'fleet.vehicle'
    
    machine_vin            = fields.Char(string='Machine Number')
    warehouse_id           = fields.Many2one('stock.warehouse', string='Stock Point')
    fg_stock_location_id   = fields.Many2one('stock.location', string='Stock Location FG',compute="get_vehicle_location")
    siba_stock_location_id = fields.Many2one('stock.location', string='Stock Location SIBA',compute="get_vehicle_location")
    return_stock_location_id = fields.Many2one('stock.location', string='Stock Location Return',compute="get_vehicle_location")
    
    
    def get_vehicle_location(self):
        for vehicle in self:
            fg_location_id         = self.env['stock.location'].search([('vehicle_id','=',vehicle.id)],limit=1)
            siba_stock_location_id = self.env['stock.location'].search([('vehicle_id','=',vehicle.id),('siba_location','=',True)],limit=1)
            return_stock_location_id = self.env['stock.location'].search([('vehicle_id','=',vehicle.id),('return_location','=',True)],limit=1)
            if not fg_location_id:
                fg_location_id.sudo().create({
                    "name":vehicle.license_plate,
                    "usage":'transit',
                    "vehicle_id":vehicle.id
                })
                
                vehicle.fg_stock_location_id = fg_location_id.id
            if not siba_stock_location_id:
                siba_stock_location_id.sudo().create({
                    "name":vehicle.license_plate + '/SIBA',
                    "usage":'transit',
                    "vehicle_id":vehicle.id,
                    "siba_location":True
                })
                
                vehicle.siba_stock_location_id = siba_stock_location_id.id
            if not return_stock_location_id:
                return_stock_location_id.sudo().create({
                    "name":vehicle.license_plate + '/Return',
                    "usage":'transit',
                    "vehicle_id":vehicle.id,
                    "return_location":True
                })
                
                vehicle.return_stock_location_id = return_stock_location_id.id
            else:
                vehicle.fg_stock_location_id = fg_location_id.id if fg_location_id else False
                vehicle.siba_stock_location_id = siba_stock_location_id.id if siba_stock_location_id else False
                vehicle.return_stock_location_id = return_stock_location_id.id if return_stock_location_id else False



class FleetVehicleModel(models.Model):
    _inherit = 'fleet.vehicle.model'
    
    
    category_id = fields.Many2one('fleet.vehicle.category', string='Category')
    
    



class FLeetVehicleLogService(models.Model):
    _inherit = 'fleet.vehicle.log.services'
    
    
    history_ids  = fields.One2many('fleet.mtc.history', 'service_id', string='History')
    maintener_id = fields.Many2one('hr.employee', string='Maintener')
    driver_id    = fields.Many2one('hr.employee', string='Driver')
    
    
    

class FleetVehicleCategory(models.Model):
    _name = 'fleet.vehicle.category'

    name        = fields.Char(string='Category')
    description = fields.Char(string='Description')


class FleetMtcHistory(models.Model):
    _name = 'fleet.mtc.history'

    service_id      = fields.Many2one('fleet.vehicle.log.services', string='Service')
    rr_id           = fields.Many2one('request.requisition', string='RR')
    product_id      = fields.Many2one('product.product', string='Product')
    product_uom_qty = fields.Float(string='Quantity')
    product_uom_id  = fields.Many2one(string='Satuan',related="product_id.uom_id")
    mtc_type        = fields.Selection([("repair","Repair"),("replace","Replace")], string='Method',default="replace")
    note            = fields.Text(string='Note')
    