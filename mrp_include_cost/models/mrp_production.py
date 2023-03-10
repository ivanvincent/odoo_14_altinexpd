import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError
import time

_logger = logging.getLogger(__name__)

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    def create_journal_foh(self):
        amount = 0
        # credit_account_id = self.type_id.foh_account_id.id
        debit_account_id = self.type_id.location_mrp_id.valuation_in_account_id.id #ganti wip
        foh_cost_journal = self.type_id.foh_journal_id.id
        # foh_cost = self.bom_id.tot_biaya
        timenow = time.strftime('%Y-%m-%d')

        inv_line = []
        total_amount_foh = 0
        for rec in self:
            for var_cost in rec.bom_id.cost_ids:
                credit_account_id = var_cost.name.account_id.id #tambah coa di variable cost
                amount = rec.product_qty * var_cost.amount_cost
                print('amount', rec.product_qty * var_cost.amount_cost)
                total_amount_foh += amount

                # Credit
                inv_line.append((0, 0, {
                    'name'                  : rec.name + ' - Cost ' + str(var_cost.name.name) or '/',
                    'date'                  : timenow,
                    'debit'                 : amount < 0.0 and -amount or 0.0,
                    'credit'                : amount > 0.0 and amount or 0.0,
                    # 'credit'                : amount,
                    'account_id'            : credit_account_id,
                    'product_id'            : rec.product_id.id,
                    'location_id'           : rec.location_dest_id.id,
                    }))
            
            # Debit
            inv_line.append((0, 0, {
                'name'                  : rec.name or '/',
                'date'                  : timenow,
                'debit'                 : total_amount_foh,
                'credit'                : 0,
                'account_id'            : debit_account_id,
                'product_id'            : rec.product_id.id,
                'location_id'           : rec.location_dest_id.id,
                }))
            
            # print(inv_line)
            

            vals = {
                'name'      : '/',
                'journal_id': foh_cost_journal,
                'narration' : 'FOH' + ' ' + rec.name,
                'date'      : timenow,
                'ref'       : rec.name,
                'line_ids'  : inv_line
                }
            #start foh biaya
            
            
            move_obj = self.env['account.move']
            move_obj.with_context(create_journal_wip=True).create(vals).post()
            #enc foh biaya

            inv_line.clear() # clear list
            # Debit
            inv_line.append((0, 0, {
                    'name'                  : rec.name or '/',
                    'date'                  : timenow,
                    'debit'                 : round(total_amount_foh),
                    'credit'                : 0,
                    'account_id'            : rec.product_id.categ_id.property_stock_valuation_account_id.id,
                    # 'account_id'            : rec.type_id.wip_account_id.id,
                    'product_id'            : rec.product_id.id,
                    'location_id'           : rec.location_dest_id.id,
                    }))

            #Credit
            inv_line.append((0, 0, {
                    'name'                  : rec.name or '/',
                    'date'                  : timenow,
                    'debit'                 : 0,
                    'credit'                : round(total_amount_foh),
                    'account_id'            : rec.type_id.wip_account_id.id,
                    'product_id'            : rec.product_id.id,
                    'location_id'           : rec.location_dest_id.id,
                    }))

            vals = {
                'name'      : '/',
                'journal_id': foh_cost_journal,
                'narration' : 'FOH' + ' ' + rec.name,
                'date'      : timenow,
                'ref'       : rec.name,
                'line_ids'  : inv_line
                }
            move_obj.with_context(create_journal_wip=True).create(vals).post()


            self.update_standard_price(total_amount_foh)
        return True
    
    def update_standard_price(self, amount_foh):
        cost_material = 0
        for rec in self.move_raw_ids.filtered(lambda x: x.product_id.standard_price > 0):
            cost_material += rec.quantity_done * rec.product_id.standard_price
        standard_price = cost_material + amount_foh
        cal_price = standard_price / self.product_qty if standard_price > 0 else standard_price
        self.product_id.write({'standard_price': cal_price})
        # self.product_id.write({'standard_price': standard_price / self.product_qty})

    
    def button_mark_done(self):
        res = super(MrpProduction, self).button_mark_done()
        context = self.env.context
        if 'skip_immediate' in context or 'skip_backorder' in context:
            self.create_journal_foh()
            self.create_journal_bahan_baku()
        # if res == True or context.get('skip_backo rder', False):
        #     self.create_journal_foh()
        return res

    #addtional
    def create_journal_bahan_baku(self):
        for rec in self.move_raw_ids.filtered(lambda x: x.product_id.standard_price > 0):
            #     print('valuess', values)
            line = []
            label = '%s - %s' % (self.name, rec.product_id.name)
            cost = rec.product_id.standard_price * rec.quantity_done
            persediaan_account_id = self.type_id.persediaan_account_id.id
            bahan_baku_account_id = self.type_id.bahan_baku_account_id
            wip_account_id = self.type_id.wip_account_id

            print('============location_id=========', rec.location_id.id)
            # debit
            line.append((0, 0, {
                'name': label,
                'account_id': wip_account_id.id,
                'debit': cost,
                'credit': 0,
                'product_id': rec.product_id.id,
                'location_id': rec.location_id.id,
                'analytic_account_id': wip_account_id.analytic_account_id.id,
            }))

            # credit
            line.append((0, 0, {
                'name': label,
                'account_id': bahan_baku_account_id.id,
                'debit': 0,
                'credit': cost,
                'product_id': rec.product_id.id,
                'location_id': rec.location_id.id,
                'analytic_account_id': bahan_baku_account_id.analytic_account_id.id,
            }))
            move_obj = self.env['account.move'].with_context(journal_bb_custom=True).create({
                'journal_id': rec.product_id.categ_id.property_stock_journal.id,
                'ref': '%s - %s' % (self.name, rec.product_id.name),
                'move_type': 'entry',
                'line_ids'  : line
            }).post()