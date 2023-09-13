from odoo import models, fields, api

class Multipart(models.Model):
    _name = 'multipart'

    name                            = fields.Char(string='Name')
    holder_specification_id         = fields.Many2one('holder.specification', string='Holder Specification')
    holder_position_id              = fields.Many2one('holder.position', string='Holder Position')
    holder_material_id              = fields.Many2one('holder.material', string='Holder Material')
    dust_cup_configuration_id       = fields.Many2one('dust.cup.configuration', string='Dust Cup Configuration')
    keyway_configuration_id         = fields.Many2one('keyway.configuration', string='Keyway Configuration')
    keyway_position_id              = fields.Many2one('keyway.position', string='Keyway Position')
    head_flat_extension_id          = fields.Many2one('head.flat.extension', string='Head Flat Extension')
    holder_heat_treatment_id        = fields.Many2one('holder.heat.treatment', string='Holder Heat Treatment')
    holder_surface_treatment_id     = fields.Many2one('holder.surface.treatment', string='Holder Surface Treatment')
    tip_shape_id                    = fields.Many2one('tip.shape', string='Tip Shape')
    tip_position_id                 = fields.Many2one('tip.position', string='Tip Position')
    tip_material_id                 = fields.Many2one('tip.material', string='Tip Material')
    tip_heat_treatment_id           = fields.Many2one('tip.heat.treatment', string='Tip Heat Treatment')
    tip_surface_treatment_id        = fields.Many2one('tip.surface.treatment', string='Tip Surface Treatment')
    holder_cap_id                   = fields.Many2one('holder.cap', string='Holder Cap')
    holder_cap_bore_id              = fields.Many2one('holder.cap.bore', string='Holder Cap Bore')
    holder_cap_surface_id           = fields.Many2one('holder.cap.surface.treatment', string='Holder Cap Surface Treatment')
    custom_adjustment_id            = fields.Many2one('custom.adjustment', string='Custom Adjustment')
    fat_option_id                   = fields.Many2one('fat.option', string='Fat Option')
    hobb_id                         = fields.Many2one('hobb', string='Hobb')
    drawing_id                      = fields.Many2one('drawing', string='Drawing')
    user_id                         = fields.Many2one('res.users', string='User')
    subtotal                        = fields.Float(compute='_compute_subtotal', string='Total')
    price_holder_spec               = fields.Float(related='holder_specification_id.price', string='Price')
    price_holder_pos                = fields.Float(related='holder_position_id.price', string='Price')
    price_holder_mat                = fields.Float(related='holder_material_id.price', string='Price')
    price_holder_heat               = fields.Float(related='holder_heat_treatment_id.price', string='Price')
    price_dust_cup                  = fields.Float(related='dust_cup_configuration_id.price', string='Price')
    price_kposition                 = fields.Float(related='keyway_position_id.price', string='Price')
    price_head_flat                 = fields.Float(related='head_flat_extension_id.price', string='Price')
    price_holder_surface            = fields.Float(related='holder_surface_treatment_id.price', string='Price')
    price_tip_shape                 = fields.Float(related='tip_shape_id.price', string='Price')
    price_custom_adj                = fields.Float(related='custom_adjustment_id.price', string='Price')
    price_fat_option                = fields.Float(related='fat_option_id.price', string='Price')
    price_hobb                      = fields.Float(related='hobb_id.price', string='Price')
    price_drawing                   = fields.Float(related='drawing_id.price', string='Price')
    price_kconfig                   = fields.Float(related='keyway_configuration_id.price', string='Price')
    price_tip_pos                   = fields.Float(related='tip_position_id.price', string='Price')
    price_tip_mat                   = fields.Float(related='tip_material_id.price', string='Price')
    price_tip_heat                  = fields.Float(related='tip_heat_treatment_id.price', string='Price')
    price_tip_surface               = fields.Float(related='tip_surface_treatment_id.price', string='Price')
    price_holder_cap                = fields.Float(related='holder_cap_id.price', string='Price')
    price_holder_cap_bore           = fields.Float(related='holder_cap_bore_id.price', string='Price')
    # price_holder_cap_surface        = fields.Float(related='holder_cap_surface_id.price', string='Price')

    @api.depends('subtotal')
    def _compute_subtotal(self):
        for a in self:
            a.subtotal = (a.price_holder_spec + a.price_holder_pos + a.price_holder_mat + a.price_holder_heat + a.price_dust_cup + a.price_kposition + a.price_head_flat
            + a.price_holder_surface + a.price_tip_shape + a.price_custom_adj + a.price_fat_option + a.price_hobb + a.price_drawing + a.price_kconfig + a.price_tip_pos 
            + a.price_tip_mat + a.price_tip_heat + a.price_tip_surface + a.price_holder_cap + a.price_holder_cap_bore)
