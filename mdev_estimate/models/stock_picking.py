from odoo import api, fields, models

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    custom_city = fields.Char(string="City")
    custom_cluster_id = fields.Many2one("res.partner.cluster", "Cluster")
    custom_jalur_id = fields.Many2one("res.partner.jalur","Route")
    custom_jalur_jwk = fields.Char(string="JWK")
    custom_group_id = fields.Many2one("res.partner.group","Grouping")
    custom_div_id = fields.Many2one("res.partner.divisi","Division")
