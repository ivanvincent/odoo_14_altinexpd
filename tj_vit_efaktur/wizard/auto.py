from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.exceptions import UserError

class efaktur_wizard(models.TransientModel):
    _name = 'vit.efaktur_auto'
    
    start   = fields.Date("Invoice Date Start",required=True,)
    end     = fields.Date("Invoice Date End",required=True,)
    invoice_ids = fields.Many2many(comodel_name="account.move", string="Invoices",)

    # @api.multi
    def confirm_button(self):

        invoice_ids = self.invoice_ids

        efaktur_ids = self.env['vit.efaktur'].search([('is_used','=',False)],
                                                     order="name asc")
        efaktur_len = len(efaktur_ids)

        i = 0
        for inv in invoice_ids:
            if i < efaktur_len:
                inv.efaktur_id = efaktur_ids[i]
            else:
                break
            i+=1

        self.env.cr.commit()
        raise UserError("Selesai penomoran E-Faktur %s invoices(s)!" % i)

    # @api.multi
    def find_invoices(self):
        start = self.start
        end = self.end
        inv_obj = self.env['account.move']
        invoices = inv_obj.search([('date','>=', start),
                                   ('date','<=', end),
                                   ('state','=','posted'),
                                   ('efaktur_id','=',False),
                                   ('type','=','out_invoice')
                                   ])
        i = 0
        invoice_ids = []
        line_ids = []
        for inv in invoices:
            invoice_ids.append(inv.id)
            line_ids.append(inv.id)
            i+=1
        print("=========invoices==========")
        print(invoices.ids)
        self.invoice_ids = [(6,0,invoices.ids)]
        # self.cr.commit()
        # raise UserError("Found %s invoices(s)!" % i)

    def _domain_compute_invoice(self, line_ids):
        print("============================")
        print(line_ids)
        res = {}
        res['domain'] = {'invoice_ids' : [('id','in',line_ids)]}
        return res

    @api.onchange('start','end')
    def _compute_test(self):
        start = self.start
        end = self.end
        inv_obj = self.env['account.move']
        invoices = inv_obj.search([('date','>=', start),
                                   ('date','<=', end),
                                   ('state','=','posted'),  
                                   ('efaktur_id','=',False),
                                   ('move_type','=','out_invoice')
                                   ])
        i = 0
        invoice_ids = []
        line_ids = []
        for inv in invoices:
            invoice_ids.append(inv.id)
            line_ids.append(inv.id)
            i+=1
        print("=========invoices==========")
        print(invoices.ids)
        self.invoice_ids = [(6,0,invoices.ids)]
