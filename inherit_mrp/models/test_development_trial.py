from odoo import models, fields, api, _
from odoo.exceptions import UserError


import logging
_logger = logging.getLogger(__name__)


class TestDevelopment(models.Model):
    _inherit = 'test.development'

    production_type = fields.Many2one('mrp.type', string='Production Type' ,default=2, readonly=True)
    component_category = fields.Many2many(related='production_type.component_product_category_ids')
    finished_category = fields.Many2many(
        comodel_name='product.category',related='production_type.finished_product_category_ids',
        string='Finished Product Category'
        )
    
    
    lebar_sisir = fields.Float(related='sisir_id.lebar_sisir', string='Lebar Sisir')
    sisir_uom_id = fields.Many2one(related='sisir_id.uom_id', string='Uom')



class TestDevelopmentFinal(models.Model):
    _inherit = 'test.development.final'

    mrp_production_id   = fields.Many2one('mrp.production', string='MO Production')
    program_id          = fields.Many2one('mrp.program', string='Program')
    hours               = fields.Float(string='Hours',related="program_id.hours")
    duration            = fields.Float(string='Duration',related="program_id.duration")
    is_done             = fields.Boolean(string='Done')


class TdTestTemplate(models.Model):
    _inherit = 'td.test.template'
    
    program_id             = fields.Many2one('mrp.program', string='Program')
    hours                  = fields.Float(string='Hours',related="program_id.hours")
    duration               = fields.Float(string='Duration',related="program_id.duration")
    
    

class TestDevelopmentProsesTrial(models.Model):
    _inherit = 'test.development.proses.trial'
    
    program_id             = fields.Many2one('mrp.program', string='Program')
    hours                  = fields.Float(string='Hours',related="program_id.hours")
    duration               = fields.Float(string='Duration',related="program_id.duration")
    
class TestDevelopmentTrial(models.Model):
    _inherit = 'test.development.trial'
    
    master_flow_process_id = fields.Many2one('master.flowprocess', string='TD Master')