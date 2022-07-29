from odoo import _, api, fields, models

class Warehouse(models.Model):
    _inherit = 'product.category'

    warehouse_id = fields.Many2one(comodel_name="stock.warehouse", string="Warehouse",)