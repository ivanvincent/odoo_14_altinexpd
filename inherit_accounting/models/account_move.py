from odoo import models, fields, api, _
from odoo.exceptions import UserError
from . import terbilang
import pandas as pd

class AccountMove(models.Model):
    _inherit = 'account.move'

    terbilang = fields.Char(string='Terbilang', compute="_compute_terbilang")
    product_id = fields.Many2one('product.product', string='Product', related="invoice_line_ids.product_id")
    partner_address_id = fields.Many2one('partner.address', string='Alamat', )


    def _compute_terbilang(self):
        for rec in self:
            amount = rec.amount_residual
            if amount > 0:
                # rec.terbilang = terbilang.terbilang(float(amount),'IDR', 'id').replace("Sen", "")
                rec.terbilang = terbilang.terbilang(float(amount),'IDR', 'id')
            else:
                rec.terbilang = ""

    def action_post(self):
        if self.name == '/':
            self.change_sequence_custom()
        res = super(AccountMove, self).action_post()
        return res
    
    def change_sequence_custom(self):
        """ 
            picking_type_id 330 = Delivery Order GD BS
        """
        if self.journal_id.name == 'Customer Invoice':
            if self.picking_id.picking_type_id.id == 330:
                seq = self.env.ref('inherit_accounting.seq_inv_bs_custom').next_by_id()
            elif self.move_type == 'out_refund':
                seq = self.env.ref('inherit_accounting.seq_inv_credit_note_custom').next_by_id()
            else:
                seq = self.env.ref('inherit_accounting.seq_inv_custom').next_by_id()
            self.write({
                'name': seq
            })

    def get_line_groupby(self):
        list_dataframe = []
        list_result = []
        for rec in self.invoice_line_ids:
            # price = rec.price_unit / 1.1
            price = rec.price_unit * 100 / (100 + sum(rec.tax_ids.mapped('amount')))
            dpp = rec.quantity * price
            # ppn = dpp * 10 / 100
            ppn = dpp * sum(rec.tax_ids.mapped('amount')) / 100
            jumlah = dpp + ppn
            list_dataframe.append({
                'product_name': rec.product_id.name,
                'price': price,
                'dpp': dpp,
                'ppn': ppn,
                'jumlah': jumlah,
                'total_roll': rec.total_roll,   
                'qty': rec.quantity,
                'uom_name': rec.product_uom_id.name,
            })
        dataframe = pd.DataFrame(list_dataframe)
        # print(dataframe)
        grouped = dataframe.groupby(["product_name", "uom_name", "price"])
        # print(grouped.sum())
        for a in grouped.sum().to_records():
            list_result.append({
                'product_name': a[0],
                'uom_name': str(a[1]),
                'price': float(a[2]),
                'dpp': float(a[3]),
                'ppn': float(a[4]),
                'jumlah': float(a[5]),
                'total_roll': int(a[6]),
                'qty': float(a[7]),
            })
        return list_result


    #Overide From Base Odoo
    def _constrains_date_sequence(self):
        # Make it possible to bypass the constraint to allow edition of already messed up documents.
        # /!\ Do not use this to completely disable the constraint as it will make this mixin unreliable.
        print('_constrains_date_sequence')

    # def action_update_address(self):