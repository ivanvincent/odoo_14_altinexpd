# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    gbb_warehouse_id = fields.Many2one('stock.warehouse', string='GBB Warehouse' )
    gpr_warehouse_id = fields.Many2one('stock.warehouse', string='GPR Warehouse' )
    gpj_warehouse_id = fields.Many2one('stock.warehouse', string='GPJ Warehouse' )
    grr_warehouse_id = fields.Many2one('stock.warehouse', string='GRR Warehouse' )

    @api.model
    def get_values(self):

        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter'].sudo()

        gbb_warehouse_id = int(ir_config.get_param('mdev_sharon.gbb_warehouse_id')) if ir_config.get_param('mdev_sharon.gbb_warehouse_id') else False
        gpr_warehouse_id = int(ir_config.get_param('mdev_sharon.gpr_warehouse_id')) if ir_config.get_param('mdev_sharon.gpr_warehouse_id') else False
        gpj_warehouse_id = int(ir_config.get_param('mdev_sharon.gpj_warehouse_id')) if ir_config.get_param('mdev_sharon.gpj_warehouse_id') else False
        grr_warehouse_id = int(ir_config.get_param('mdev_sharon.grr_warehouse_id')) if ir_config.get_param('mdev_sharon.grr_warehouse_id') else False

        res.update(
            gbb_warehouse_id = gbb_warehouse_id,
            gpr_warehouse_id = gpr_warehouse_id,
            gpj_warehouse_id = gpj_warehouse_id,
            grr_warehouse_id = grr_warehouse_id
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()

        gbb_warehouse_id = self.gbb_warehouse_id and self.gbb_warehouse_id.id or False
        gpr_warehouse_id = self.gpr_warehouse_id and self.gpr_warehouse_id.id or False
        gpj_warehouse_id = self.gpj_warehouse_id and self.gpj_warehouse_id.id or False
        grr_warehouse_id = self.grr_warehouse_id and self.grr_warehouse_id.id or False

        ir_config.set_param('mdev_sharon.gbb_warehouse_id', gbb_warehouse_id)
        ir_config.set_param('mdev_sharon.gpr_warehouse_id', gpr_warehouse_id)
        ir_config.set_param('mdev_sharon.gpj_warehouse_id', gpj_warehouse_id)
        ir_config.set_param('mdev_sharon.grr_warehouse_id', grr_warehouse_id)

