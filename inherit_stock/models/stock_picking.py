from email.policy import default
from itertools import product
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT as DATETIME_FORMAT
import json
import logging
_logger = logging.getLogger(__name__)

class StockPicking(models.Model):
    _inherit = "stock.picking"
    

    operation_code  = fields.Selection(related='picking_type_id.code')
    requested_by = fields.Many2one(
        comodel_name="res.users",
        string="Requested By",
        required=False,
        readonly=True,
    )

    created_journal_mutation   = fields.Boolean(string='Created Journal Mutation ?', default=False)
    rack_id                    = fields.Many2one('master.rack', string='Rack')
    vehicle_id                 = fields.Many2one('fleet.vehicle', string='Vehicle')
    procure_stock              = fields.Selection([("fg","Finish Good"),("siba","Siba"),("return","Return")], string='Procure Stock')

    # @api.model
    # def action_print_sppm(self):
    #     return self.env['report'].get_action(self._context.get('active_ids'), 'inherit_stock.sppm_template')
    
    
        
    @api.onchange('scheduled_date')
    def on_change_schedule_date(self):
        for picking in self:
            if picking.state not in ('done','cancel'):
                picking.write({"date":picking.scheduled_date})
                for move in picking.move_lines:
                    move.write({"date":picking.scheduled_date})
    
    
    
    
    #todo need to fix harus back to draft sampe ke product_move nya juga
    def action_back_to_draft(self):
        moves = self.mapped("move_lines")
        moves.action_back_to_draft()
        
    
    @api.model
    def barcode_scan(self,barcode,active_id):
        self = self.browse([active_id])
        if self:
            lot_id = self.env['stock.production.lot']\
            .search([('name','=',barcode),('location_id','=',self.location_id.id)],limit=1)
            package_id = self.env['stock.quant.package'].search([('name','=',barcode),('location_id','=',self.location_id.id)],limit=1)
            if not lot_id and not self.picking_type_id.show_entire_packs:
                return {
                    "error":True,
                    "message":"Barcode %s \nnot found !!!"%(barcode),
                    "count":len(lot_id)}
            elif package_id and self.picking_type_id.show_entire_packs:
                self.package_level_ids_details = [(0,0,{"package_id":package_id.id ,"company_id":self.env.company.id,"location_id":self.location_id.id ,
                "location_dest_id":self.location_dest_id.id,"is_done":True,
                # "move_ids":[(0,0,{"name":lot.product_id.name,
                #                     "product_id":lot.product_id.id ,
                #                   "product_uom":lot.product_id.uom_id.id,
                #                   "location_id":self.location_id.id ,
                #                   "location_dest_id":self.location_dest_id.id,
                #                 #   "qty_done": lot.quantity,
                #                   "product_uom_qty": lot.quantity}) for lot in package_id.quant_ids]
                })]
                # "move_ids":[(0,0,{"product_id":package_id.product_id.id ,
                #                   "product_uom":package_id.product_id.uom_id.id,
                #                   "location_id":self.location_id.id ,
                #                   "location_dest_id":self.location_dest_id.id,
                #                   "qty_done":sum(package_id.quant_ids.mapped('quantity')),
                #                   "product_uom_qty":sum(package_id.quant_ids.mapped('quantity'))})]})]
                    
                return True
            elif not package_id and self.picking_type_id.show_entire_packs:
                return {
                    "error":True,
                    "message":"Package not %s \nfound !!!"%(barcode),
                    "count":len(lot_id)}
                
            elif self.move_line_nosuggest_ids and lot_id.id in [ lot.id for lot in self.move_line_nosuggest_ids.mapped('lot_id')]:
                return {
                    "error":True,
                    "message":"Barcode %s \nwas Added !!!"%(barcode),
                    "count":len(lot_id)}
        
            self.move_line_nosuggest_ids = [(0,0,{
                    'product_id': lot_id.product_id.id,
                    'lot_id': lot_id.id,
                    'lot_name': lot_id.name,
                    'product_uom_id': lot_id.product_id.uom_id.id,
                    'qty_done': lot_id.product_qty,
                    'company_id':self.env.company.id,
                    "nozle":self.nozle,
                    'location_id': self.location_id.id,
                    'location_dest_id': self.location_dest_id.id,
            })]
            
            
            
            
            return {
                    "error":False,
                    "message":"Barcode %s \n Added !!!"%(barcode),
                    "count":len(lot_id)} 
    
    
    
    # def button_validate(self):
    #     for line in self.move_ids_without_package:
    #         if not line.image_ids and line.picking_id:
    #             raise ValidationError('Mohon maaf image untuk produk %s kosong. Harap untuk diisi terlebih dahulu !' % line.name)

        res = super(StockPicking, self).button_validate()
        #todo fixme
        
                
        self.write({'user_id': self.env.user.id})
        if res == True and not self.package_level_ids_details:
            self.action_journal_mutation(self)
            if self.picking_type_id.id == 357:
                if self.vehicle_id and not self.backorder_id:
                    service = self.env['fleet.vehicle.log.services'].sudo().create({
                        "vehicle_id":self.vehicle_id.id,
                        "service_type_id":2,
                        "date":fields.Date.today(),
                        "history_ids": [(0,0,{'product_id':move.product_id.id,"rr_id":self.request_requisition_id.id,"product_uom_qty":move.product_uom_qty}) for move in self.move_ids_without_package]
                    })
            if self.picking_type_id.is_multi_step and self.do_id:
                self.do_id._create_vehicle_picking(self.procure_stock)
                self.do_id.sudo().write({'state':'delivery'})
            if self.picking_type_id.is_transit_transfer and self.do_id:
                self.do_id.sudo().write({'state':'delivered'})
                
            
            
        return res


    def action_journal_mutation(self, record):
        print('action_journal_mutation')
        domain = [('id', 'in', record.ids), ('location_id.usage', '=', 'internal'),
                ('location_dest_id.usage', '=', 'internal'), ('created_journal_mutation', '!=', True)]
        picking_obj = self.env['stock.picking'].search(domain)

        for pck in picking_obj:            
            journal_id = pck.picking_type_id.journal_mutation_id.id
            line = []

            for smv in pck.move_ids_without_package:
                cost = smv.product_id.standard_price
                qty_done = smv.quantity_done
                amount = qty_done * cost
                account_id = smv.product_id.categ_id.property_stock_valuation_account_id.id
                analytic_account_id = smv.product_id.categ_id.property_stock_valuation_account_id.analytic_account_id.id
                label = 'Mutation From %s To %s (%s)' % (pck.location_id.location_id.name, pck.location_dest_id.location_id.name, pck.name)

                # Debit
                line.append((0, 0, {
                    'name'                  : label,
                    'date'                  : fields.Date.today(),
                    'debit'                 : amount,
                    'credit'                : 0,
                    'account_id'            : account_id,
                    'product_id'            : smv.product_id.id,
                    'location_id'           : pck.location_dest_id.id,
                    'analytic_account_id'   : analytic_account_id,
                    'quantity'              : qty_done,
                    'price_unit'            : smv.price_unit,
                }))

                # Credit
                line.append((0, 0, {
                    'name'                  : label,
                    'date'                  : fields.Date.today(),
                    'debit'                 : 0,
                    'credit'                : amount,
                    'account_id'            : account_id,
                    'product_id'            : smv.product_id.id,
                    'location_id'           : pck.location_id.id,
                    'analytic_account_id'   : analytic_account_id,
                    'quantity'              : qty_done * -1,
                    'price_unit'            : smv.price_unit,
                }))

            vals = {
                    'name'      : '/',
                    'journal_id': journal_id,
                    'narration' : 'Mutation From %s To %s' % (pck.location_id.location_id.name, pck.location_dest_id.location_id.name),
                    'date'      : fields.Date.today(),
                    'ref'       : pck.name,
                    'picking_id': pck.id,
                    'line_ids'  : line
                }
            move_obj = self.env['account.move'].sudo().create(vals).post()
            pck.sudo().write({'created_journal_mutation': True})

    
    def action_print_sppm(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'picking_id': self.ids,
            },
        }
        return self.env.ref('inherit_stock.action_sppm_print').report_action(None, data=data)

    def button_validate(self):
        res = super(StockPicking, self).button_validate()
        print('resssss', res)
        if res == True:
            if sum(self.move_line_ids_without_package.mapped('waste')) > 0:
                self._create_picking_scrap()
        return res

    def _create_picking_scrap(self):
        picking_obj = self.env['stock.picking'].create({
            'picking_type_id' : self.picking_type_id.id,
            'location_id'     : self.location_id.id,
            'location_dest_id': 16, #Virtual Locations / Scraps
            "origin"          : "Scrap - %s" % (self.name),
            "move_line_ids_without_package":[(0,0, {
                "lot_id"            : move.lot_id.id,
                "product_id"        : move.product_id.id,
                # "product_uom_qty"   : move.waste,
                "qty_done"          : move.waste,
                "product_uom_id"    : move.product_id.uom_id.id,
                "location_id"       : self.location_id.id,
                "location_dest_id"  : 16, #Virtual Locations / Scraps
            }) for move in self.move_line_ids_without_package.filtered(lambda x: x.waste > 0)]
        })
        picking_obj.action_confirm()
        picking_obj.action_assign()
        picking_obj.button_validate()

class ReportSPPM(models.AbstractModel):
    _name = 'report.inherit_stock.sppm_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        docs = []
        StockMoveObj = self.env['stock.move'].search([('picking_id','in',(data['form']['picking_id']))], order='name asc')
        for StockMove in StockMoveObj:
            docs.append({
                'name': StockMove.product_id.name,
                'sat': StockMove.product_uom.name,
                'qty': StockMove.quantity_done,
            })

        return {
            'doc_ids': data['ids'],
            'doc_model': data['model'],
            'docs': docs,
        }