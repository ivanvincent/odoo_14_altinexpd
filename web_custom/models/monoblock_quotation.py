from odoo import models, fields, api

class Monoblock(models.Model):
    _name = 'monoblock'

    name                            = fields.Char(string='Name')
    basic_specification_id          = fields.Many2one('basic.specification', string='Basic Specification')
    material_id                     = fields.Many2one('material', string='Material')
    tip_type_id                     = fields.Many2one('tip.type', string='Tip Type')
    single_multi_tip_id             = fields.Many2one('single.or.multi.tip', string='Single or Multi Tip')
    dust_cup_configuration_id       = fields.Many2one('dust.cup.configuration', string='Dust Cup Configuration')
    keyway_position_id              = fields.Many2one('keyway.position', string='Keyway Position')
    head_flat_extension_id          = fields.Many2one('head.flat.extension', string='Head Flat Extension')
    heat_treatment_id               = fields.Many2one('heat.treatment', string='Heat Treatment')
    surface_treatment_id            = fields.Many2one('surface.treatment', string='Surface Treatment')
    custom_adjustment_id            = fields.Many2one('custom.adjustment', string='Custom Adjustment')
    fat_option_id                   = fields.Many2one('fat.option', string='Fat Option')
    hobb_id                         = fields.Many2one('hobb', string='Hobb')
    drawing_id                      = fields.Many2one('drawing', string='Drawing')
    keyway_configuration_id         = fields.Many2one('keyway.configuration', string='Keyway Configuration')