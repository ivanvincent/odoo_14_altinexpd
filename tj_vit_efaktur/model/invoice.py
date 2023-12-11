from odoo import api, fields, models, _
from odoo.exceptions import UserError

class invoice(models.Model):
    # _name = 'account.move'
    _inherit = 'account.move'

    efaktur_id  = fields.Many2one(comodel_name="vit.efaktur", string="eFaktur", required=False, )
    is_efaktur_exported = fields.Boolean(string="Is eFaktur Exported",  )
    date_efaktur_exported = fields.Datetime(string="eFaktur Exported Date", required=False, )

    tanggal_efaktur = fields.Date(string="Tanggal Efaktur")
    masa_pajak = fields.Char(string="Masa Pajak",)
    tahun_pajak = fields.Char(string="Tahun Pajak",)

    efaktur_masukan = fields.Char(string="Nomor Seri Faktur Pajak", required=False, )
    amount_efaktur = fields.Monetary(string='Tax Efaktur', store=True, readonly=True, compute='_compute_efaktur')
    # efaktur_masukan = fields.Char(string="Nomor Seri Faktur Pajak", required=False, )
    surat_jalan_doc       = fields.Binary(string='Surat Jalan')
    bill_doc              = fields.Binary(string='Bill')
    fp_doc                = fields.Binary(string='Faktur Pajak')
    surat_jalan_name      = fields.Char(string='Surat Jalan')
    bill_name             = fields.Char(string='Bill')
    fp_name               = fields.Char(string='Faktur Pajak')

    def action_post(self):
        if not self.surat_jalan_doc:
            raise UserError('Mohon maaf silakan lengkapi seluruh kelengkapan dokumen terlebih dahulu')
        elif not self.bill_doc:
            raise UserError('Mohon maaf silakan lengkapi seluruh kelengkapan dokumen terlebih dahulu')
        elif not self.fp_doc:
            raise UserError('Mohon maaf silakan lengkapi seluruh kelengkapan dokumen terlebih dahulu')
        res = super(invoice, self).action_post()
        return res

    @api.onchange("efaktur_id")
    def _masa_pajak(self):
        for inv in self:
            if inv.invoice_date:
                d = inv.invoice_date.strftime("%m")
                inv.masa_pajak = d

    @api.onchange("efaktur_id")
    def _tahun_pajak(self):
        for inv in self:
            if inv.invoice_date:
                d = inv.invoice_date.strftime("%Y")
                inv.tahun_pajak = d
                inv.tanggal_efaktur = inv.invoice_date
    # @api.multi
    def action_invoice_open(self):
        res = super(invoice, self).action_invoice_open()
        self.is_efaktur_exported=False
        return res

    @api.depends('line_ids.tax_line_id.amount', 'currency_id', 'company_id', 'invoice_date')
    def _compute_efaktur(self):
        round_curr = self.currency_id.round
        self.amount_efaktur = sum(round_curr(line.amount) for line in self.line_ids.tax_line_id if line.is_efaktur)

    # @api.model
    # def create(self, val):
    #     res = super(invoice, self).create(val)
    #     faktur_id = val.get('efaktur_id')
    #     if faktur_id:
    #         fakturObj = self.env['vit.efaktur'].browse(faktur_id).write({
    #             'invoice_ids' : [(4,res.id)]
    #         })
    #     return res

    def write(self, val):
        res = super(invoice, self).write(val)
        faktur_id = val.get('efaktur_id')
        if faktur_id:
            fakturObj = self.env['vit.efaktur'].browse(faktur_id).write({
                'invoice_ids' : [(4,self.id)]
            })
        return res