from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockLocationRoute(models.Model):
    _inherit = 'stock.location.route'
    
    
    is_route_vehicle              = fields.Boolean(string='Route Vehicle Location ?')
    vehicle_fg_location_ids       = fields.Many2many(comodel_name='stock.location', relation='vehicle_fg_location_route_rel',string='Vehicle FG Locations',compute="_compute_vehicle_location")
    vehicle_siba_location_ids     = fields.Many2many(comodel_name='stock.location', relation='vehicle_siba_location_route_rel',string='Vehicle SIBA Locations',compute="_compute_vehicle_location")
    vehicle_return_location_ids   = fields.Many2many(comodel_name='stock.location', relation='vehicle_return_location_route_rel',string='Vehicle Return Locations',compute="_compute_vehicle_location")
    sp_fg_location_ids            = fields.Many2many(comodel_name='stock.location', relation='sp_fg_location_route_rel',string='SP FG Locations',compute="_compute_sp_location")
    sp_siba_location_ids          = fields.Many2many(comodel_name='stock.location', relation='sp_siba_location_route_rel',string='SP SIBA Locations',compute="_compute_sp_location")
    sp_return_location_ids        = fields.Many2many(comodel_name='stock.location', relation='sp_return_location_route_rel',string='SP RETURN Locations',compute="_compute_sp_location")
    # route_template_ids            = fields.Many2many(comodel_name='stock.location.route.template', string=' Route Template')
    
    
    def _compute_sp_location(self):
        for route in self:
            sp_fg_location_ids = self.env['stock.location'].search([('is_stock_point','=',True),('siba_location','!=',True),('return_location','!=',True)])
            sp_siba_location_ids = self.env['stock.location'].search([('is_stock_point','=',True),('siba_location','=',True),('return_location','!=',True)])
            sp_return_location_ids = self.env['stock.location'].search([('is_stock_point','=',True),('siba_location','!=',True),('return_location','=',True)])
            route.sp_fg_location_ids = [(6,0,sp_fg_location_ids.ids)] if sp_fg_location_ids else []
            route.sp_siba_location_ids = [(6,0,sp_siba_location_ids.ids)] if sp_siba_location_ids else []
            route.sp_return_location_ids = [(6,0,sp_return_location_ids.ids)] if sp_return_location_ids else []
    

    def reset_rules(self):
        self.ensure_one()
        self.rule_ids = False
    
    
    def create_vehicle_routes(self):
        for template in self.route_template_ids.filtered(lambda template: template.action_type == 'pull'):
            for vehicle in self.vehicle_fg_location_ids:
                dest_location = vehicle.id if not template.src_location_id.siba_location else vehicle.vehicle_id.siba_stock_location_id.id
                display_name  = vehicle.display_name if not template.src_location_id.siba_location else vehicle.vehicle_id.siba_stock_location_id.display_name
                rules = self.env['stock.rule'].create({
                    "name"               :template.src_location_id.display_name +' → '+ display_name,
                    "route_id"           :self.id,
                    "action"             :template.action_type,
                    "location_src_id"    :template.src_location_id.id,
                    "picking_type_id"    :template.picking_type_id.id,
                    "location_id"        :dest_location,
                    "auto"               :'transparent',
                    "procure_method"     :template.procure_method,
                    "warehouse_id"       :self.warehouse_ids[0].id,
                })
        for template in self.route_template_ids.filtered(lambda template: template.action_type == 'push'):
            for vehicle in self.vehicle_fg_location_ids:
                for  fg in self.sp_fg_location_ids.filtered(lambda fg : not fg.siba_location):
                    rules = self.env['stock.rule'].create({
                        "name"               :vehicle.display_name +' → '+ fg.display_name,
                        "route_id"           :self.id,
                        "action"             :template.action_type,
                        "location_src_id"    :vehicle.id,
                        "picking_type_id"    :template.picking_type_id.id,
                        "location_id"        :fg.id,
                        "auto"               :'manual',
                        "procure_method"     :template.procure_method,
                        "warehouse_id"       :self.warehouse_ids[0].id,
                    })
            for vehicle in self.vehicle_siba_location_ids:
                for  siba in self.sp_siba_location_ids.filtered(lambda siba : siba.siba_location):
                    rules = self.env['stock.rule'].create({
                        "name"               :vehicle.display_name +' → '+ siba.display_name,
                        "route_id"           :self.id,
                        "action"             :template.action_type,
                        "location_src_id"    :vehicle.id,
                        "picking_type_id"    :template.picking_type_id.id,
                        "location_id"        :siba.id,
                        "auto"               :'manual',
                        "procure_method"     :template.procure_method,
                        "warehouse_id"       :self.warehouse_ids[0].id,
                    })
            for vehicle in self.vehicle_return_location_ids:
                for  ret in self.sp_return_location_ids.filtered(lambda ret : ret.return_location):
                    rules = self.env['stock.rule'].create({
                        "name"               :vehicle.display_name +' → '+ ret.display_name,
                        "route_id"           :self.id,
                        "action"             :template.action_type,
                        "location_src_id"    :vehicle.id,
                        "picking_type_id"    :template.picking_type_id.id,
                        "location_id"        :ret.id,
                        "auto"               :'manual',
                        "procure_method"     :template.procure_method,
                        "warehouse_id"       :self.warehouse_ids[0].id,
                    })
                
                
    
    
    def _compute_vehicle_location(self):
        for route in self:
            if route.is_route_vehicle:
                vehicle_fg_location_ids = self.env['stock.location'].search([('usage','=','transit'),('vehicle_id','!=',False),('siba_location','!=',True),('return_location','!=',True)])
                vehicle_siba_location_ids = self.env['stock.location'].search([('usage','=','transit'),('vehicle_id','!=',False),('siba_location','=',True),('return_location','!=',True)])
                vehicle_return_location_ids = self.env['stock.location'].search([('usage','=','transit'),('vehicle_id','!=',False),('siba_location','!=',True),('return_location','=',True)])
                route.vehicle_fg_location_ids = [(6,0,vehicle_fg_location_ids.ids)] if vehicle_fg_location_ids else []
                route.vehicle_siba_location_ids = [(6,0,vehicle_siba_location_ids.ids)] if vehicle_siba_location_ids else []
                route.vehicle_return_location_ids = [(6,0,vehicle_return_location_ids.ids)] if vehicle_return_location_ids else []
            else:
                route.vehicle_fg_location_ids = []
                route.vehicle_siba_location_ids = []
                route.vehicle_return_location_ids = []
                
    