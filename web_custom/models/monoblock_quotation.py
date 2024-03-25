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
    user_id                         = fields.Many2one('res.users', string='User')
    subtotal                        = fields.Float(compute='_compute_subtotal', string='Total')
    price_basic                     = fields.Float(related='basic_specification_id.price', string='Price')
    price_material                  = fields.Float(related='material_id.price', string='Price')
    price_single_multi              = fields.Float(related='single_multi_tip_id.price', string='Price')
    price_tip_type                  = fields.Float(related='tip_type_id.price', string='Price')
    price_dust_cup                  = fields.Float(related='dust_cup_configuration_id.price', string='Price')
    price_kposition                 = fields.Float(related='keyway_position_id.price', string='Price')
    price_head_flat                 = fields.Float(related='head_flat_extension_id.price', string='Price')
    price_heat_treatment            = fields.Float(related='heat_treatment_id.price', string='Price')
    price_surface                   = fields.Float(related='surface_treatment_id.price', string='Price')
    price_custom_adj                = fields.Float(related='custom_adjustment_id.price', string='Price')
    price_fat_option                = fields.Float(related='fat_option_id.price', string='Price')
    price_hobb                      = fields.Float(related='hobb_id.price', string='Price')
    price_drawing                   = fields.Float(related='drawing_id.price', string='Price')
    price_kconfig                   = fields.Float(related='keyway_configuration_id.price', string='Price')
    punch                           = fields.Float('Punch')
    tip                             = fields.Float('Tip')

    @api.depends('subtotal')
    def _compute_subtotal(self):
        for a in self:
            a.subtotal = (a.price_basic + a.price_material + a.price_single_multi + a.price_tip_type + a.price_dust_cup + a.price_kposition + a.price_head_flat
            + a.price_heat_treatment + a.price_surface + a.price_custom_adj + a.price_fat_option + a.price_hobb + a.price_drawing + a.price_kconfig)

    @api.model
    def create(self, vals):
        seq_id = self.env.ref('web_custom.monoblock_seq')
        vals['name'] = seq_id.next_by_id() if seq_id else '/'
        return super(Monoblock, self).create(vals)