from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
    _inherit = 'account.move'

    @api.model
    def create(self, values):
        ctx = self.env.context
        stock_move_id = values.get('stock_move_id', False)
        stock_move_obj = self.env['stock.move'].browse(stock_move_id)
        stock_move_location_id = stock_move_obj.location_id
        stock_move_location_dest_id = stock_move_obj.location_dest_id

        if 'button_mark_done_production_ids' in ctx:
            mrp_obj = self.env['mrp.production'].browse(ctx.get('active_id'))
            bahan_baku_account_id = mrp_obj.type_id.bahan_baku_account_id.id
            persediaan_account_id = mrp_obj.type_id.persediaan_account_id.id
            wip_account_id = mrp_obj.type_id.wip_account_id.id
            journal_obj = self.env['account.journal'].browse(values.get('journal_id'))

            location_id = False

            if stock_move_location_id.usage == 'internal' and not location_id:
                location_id = stock_move_location_id.id

            if stock_move_location_dest_id.usage == 'internal' and not location_id:
                location_id = stock_move_location_dest_id.id
            
            amount = 0
            product_id_tmp = False
            if journal_obj.is_stock and 'button_mark_done_production_ids' in ctx:
                total_var_cost = mrp_obj.bom_id.total_price_var_cost * mrp_obj.qty_producing

                for a in values.get('line_ids', []):
                    analytic_acc_id = self.env['account.account'].browse(a[2].get('account_id')).analytic_account_id.id
                    debit = a[2].get('debit')
                    credit = a[2].get('credit')

                    if debit > 0:
                        a[2].update({
                            # 'debit': debit + total_var_cost,
                            'debit': debit,
                            'location_id': location_id,
                            'analytic_account_id': analytic_acc_id,
                        })
                    if credit > 0:
                        a[2].update({
                            # 'credit': credit + total_var_cost,
                            'credit': credit,
                            'location_id': location_id,
                            'analytic_account_id': analytic_acc_id,
                        })

            elif 'button_mark_done_production_ids' and not journal_obj.is_stock and not ctx.get('create_journal_wip') and 'journal_bb_custom' not in ctx:
                for a in values.get('line_ids', []):
                    debit = a[2].get('debit')
                    credit = a[2].get('credit')
                    analytic_acc_id = self.env['account.account'].browse(a[2].get('account_id')).analytic_account_id.id

                    if amount < 1:
                        amount = debit

                    product_id_tmp = a[2].get('product_id')

                    if debit > 0:
                        a[2].update({
                            'account_id': bahan_baku_account_id,
                            'location_id': location_id,
                            'analytic_account_id': analytic_acc_id,
                        })
                    if credit > 0:
                        a[2].update({
                            # 'account_id': persediaan_account_id,
                            'location_id': location_id,
                            'analytic_account_id': analytic_acc_id,
                        })

                line = values.get('line_ids', [])

                product_obj = self.env['product.product']
                label = '%s - %s' % (mrp_obj.name, product_obj.browse(product_id_tmp).name)
                # analytic_acc_id = self.env['account.account'].browse(a[2].get('account_id')).analytic_account_id.id

                # if not journal_obj.is_foh:
                #     print('valuess', values)
                #     move_obj = self.env['account.move'].create({
                #         'journal_id': values.get('journal_id'),
                #         'ref': values.get('ref'),
                #         'move_type': 'entry',
                #     })
                    # # debit
                    # line.append((0, 0, {
                    #     'name': label,
                    #     'account_id': wip_account_id,
                    #     'debit': amount,
                    #     'credit': 0,
                    #     'product_id': product_id_tmp,
                    #     'location_id': location_id,
                    #     'analytic_account_id': analytic_acc_id,
                    # }))

                    # # credit
                    # line.append((0, 0, {
                    #     'name': label,
                    #     'account_id': bahan_baku_account_id,
                    #     'debit': 0,
                    #     'credit': amount,
                    #     'product_id': product_id_tmp,
                    #     'location_id': location_id,
                    #     'analytic_account_id': analytic_acc_id,
                    # }))
        if 'button_validate_picking_ids' in ctx and 'journal_id' in values and 'journal_bb_custom' not in ctx:
            location_id = False

            if stock_move_location_id.usage == 'internal' and not location_id:
                location_id = stock_move_location_id.id

            if stock_move_location_dest_id.usage == 'internal' and not location_id:
                location_id = stock_move_location_dest_id.id
            
            for a in values.get('line_ids', []):
                analytic_acc_id = self.env['account.account'].browse(a[2].get('account_id')).analytic_account_id.id
                a[2].update({
                    'location_id': location_id,
                    'analytic_account_id': analytic_acc_id,
                })
                a[2].update({
                    'location_id': location_id,
                    'analytic_account_id': analytic_acc_id,
                })
        result = super(AccountMove, self).create(values)
        return result