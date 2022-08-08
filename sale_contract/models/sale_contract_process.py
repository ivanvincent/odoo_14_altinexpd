from odoo import models, fields, api

class SaleContractProcess(models.Model):
    _name = 'sale.contract.process'

    name = fields.Char(string='Name')