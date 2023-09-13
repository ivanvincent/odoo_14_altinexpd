from odoo import models, fields, api

class Die(models.Model):
    _name = 'die'

    name                            = fields.Char(string='Name')
    basic_specification_id          = fields.Many2one('basic.specification', string='Basic Specification')
    material_id                     = fields.Many2one('material', string='Material')
    bore_type_id                    = fields.Many2one('bore.type', string='Bore Type')
    single_multi_tip_id             = fields.Many2one('single.or.multi.tip', string='Single or Multi Tip')
    die_screw_id                    = fields.Many2one('die.screw', string='Die Screw Groove')
    optional_tapered_bore_id        = fields.Many2one('optional.tapered.bore', string='Optional Tapered Bore')
    heat_treatment_id               = fields.Many2one('heat.treatment', string='Heat Treatment')
    surface_treatment_id            = fields.Many2one('surface.treatment', string='Surface Treatment')
    custom_adjustment_id            = fields.Many2one('custom.adjustment', string='Custom Adjustment')
    fat_option_id                   = fields.Many2one('fat.option', string='Fat Option')
    die_setting_aligner_id          = fields.Many2one('die.setting.aligner', string='Die Setting Aligner')
    user_id                         = fields.Many2one('res.users', string='User')
    subtotal                        = fields.Float(compute='_compute_subtotal', string='Total')
    price_basic                     = fields.Float(related='basic_specification_id.price', string='Price')
    price_material                  = fields.Float(related='material_id.price', string='Price')
    price_bore_type                 = fields.Float(related='bore_type_id.price', string='Price')
    price_single_multi              = fields.Float(related='single_multi_tip_id.price', string='Price')
    price_die_screw                 = fields.Float(related='die_screw_id.price', string='Price')
    price_optional_tapered          = fields.Float(related='optional_tapered_bore_id.price', string='Price')
    price_heat_treatment            = fields.Float(related='heat_treatment_id.price', string='Price')
    price_surface                   = fields.Float(related='surface_treatment_id.price', string='Price')
    price_custom_adj                = fields.Float(related='custom_adjustment_id.price', string='Price')
    price_fat_option                = fields.Float(related='fat_option_id.price', string='Price')
    price_die_setting               = fields.Float(related='die_setting_aligner_id.price', string='Price')
    die_segment                     = fields.Float('Die/Segment')
    bore                            = fields.Float('Bore')

    @api.depends('subtotal')
    def _compute_subtotal(self):
        for a in self:
            a.subtotal = (a.price_basic + a.price_material + a.price_single_multi + a.price_bore_type + a.price_die_screw + a.price_optional_tapered
            + a.price_heat_treatment + a.price_surface + a.price_custom_adj + a.price_fat_option + a.price_die_setting)