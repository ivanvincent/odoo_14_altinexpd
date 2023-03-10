from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpType(models.Model):
    _inherit = 'mrp.production.type'

    foh_cost = fields.Float('Exspense Cost',)
    foh_journal_id = fields.Many2one('account.journal', 'Journal', required=True,)
    foh_account_id = fields.Many2one('account.account', 'FOH Interim Account', help="Pembebanan Biaya FOH", required=False,)
    location_mrp_id = fields.Many2one('stock.location', string='Proses Location', required=True, )

    bahan_baku_account_id = fields.Many2one('account.account', string='Coa Bahan Baku', required=True, )
    persediaan_account_id = fields.Many2one('account.account', string='Coa Persediaan', required=True, )
    wip_account_id = fields.Many2one('account.account', string='Coa Wip', required=True, )
