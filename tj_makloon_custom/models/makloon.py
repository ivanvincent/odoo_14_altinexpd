from odoo import api, fields, models, _

class Roll(models.Model):
    _name = 'makloon.roll'

    name = fields.Integer("@ Kg", )
    desc = fields.Char("Description", )
    # color = fields.Integer(string='Color Index', help="Warna Surat Jalan")

class MakloonMerk(models.Model):
    _name = 'makloon.merk'

    name = fields.Char("Name", )

class MakloonSetting(models.Model):
    _name = 'makloon.setting'

    name = fields.Char("Name", )

class MakloonGramasi(models.Model):
    _name = 'makloon.gramasi'

    name = fields.Char("Name", )

class MakloonCorak(models.Model):
    _name = 'makloon.corak'

    name = fields.Char("Name", )

class MakloonColor(models.Model):
    _name = 'makloon.warna'

    name = fields.Char("Name", )

class MakloonResepWarna(models.Model):
    _name = 'makloon.resep.warna'

    name = fields.Char("Name", )
    warna_id = fields.Many2one('makloon.warna', 'Warna')
    category_warna_id = fields.Many2one('makloon.category.warna', 'Category Warna')

    # order_line = fields.One2many('makloon.resep.warna.line', 'order_id', string='Makloon Resep Warna Lines', copy=True,
    #                          track_visibility='onchange', )

class MakloonResepWarna(models.Model):
    _name = 'makloon.resep.warna.line'

    name = fields.Char("Description", )
    order_id = fields.Many2one('makloon.resep.warna', string='Makloon Resep Warna', required=True, ondelete='cascade',
                                index=True, copy=False)
    warna_id = fields.Many2one('makloon.warna', 'Warna')
    category_warna_id = fields.Many2one('makloon.category.warna', 'Category Warna')

class MakloonCategoryColor(models.Model):
    _name = 'makloon.category.warna'

    name = fields.Char("Name", )

class MakloonOperationLine(models.Model):
    _inherit = "makloon.operation"

    order_line = fields.One2many('makloon.operation.line', 'order_id', string='Makloon Operation Lines', copy=True,
                                 track_visibility='onchange',)
    color = fields.Integer(string='Color Index', help="Warna Surat Jalan")

class MakloonOperationLine(models.Model):
    _name = "makloon.operation.line"
    _rec_name = 'product_category_id'

    order_id = fields.Many2one('makloon.operation', string='Makloon Operation', required=True, ondelete='cascade',
                               index=True, copy=False)
    product_category_id = fields.Many2one('product.category', 'Result')
    product_material_id = fields.Many2one('product.category', 'Material')
    name = fields.Char(string="Description")


class MakloonPlanningStage(models.Model):
    _inherit = "makloon.planning.stage"

    operation_name = fields.Char(
        string='Operation Name',
        store=True,)

    @api.onchange('operation_id')
    @api.depends('operation_id')
    def _onchange_uom(self):
        for rec in self:
            if rec.operation_id:
                rec.operation_name = rec.operation_id.name

    @api.depends('order_ids.material_progress','order_ids.result_progress')
    # @api.multi
    def _get_makloon_progress(self):
        for me_id in self :
            progress_in = 0
            progress_out = 0
            progress_in_count = 0
            progress_out_count = 0

            for order in me_id.order_ids :
                progress_in += order.result_progress
                progress_out += order.material_progress
                progress_in_count += 1
                progress_out_count += 1

            if progress_in_count :
                progress_in = progress_in/progress_in_count
                progress_out = progress_out/progress_out_count
            
            me_id.result_progress = progress_in
            me_id.material_progress = progress_out

    material_progress = fields.Float('Material Progress', compute="_get_makloon_progress", copy=False)
    result_progress = fields.Float('Result Progress', compute="_get_makloon_progress", copy=False)

class MakloonPlanning(models.Model):
    _inherit = "makloon.planning"

    @api.depends('stage_ids.material_progress','stage_ids.result_progress')
    # @api.multi
    def _get_makloon_progress(self):
        for me_id in self :
            progress_in = 0
            progress_out = 0
            progress_in_count = 0
            progress_out_count = 0

            for order in me_id.stage_ids :
                progress_in += order.result_progress
                progress_out += order.material_progress
                progress_in_count += 1
                progress_out_count += 1

            if progress_in_count :
                progress_in = progress_in/progress_in_count
                progress_out = progress_out/progress_out_count
            
            me_id.result_progress = progress_in
            me_id.material_progress = progress_out

    material_progress = fields.Float('Material Progress', compute="_get_makloon_progress", copy=False)
    result_progress = fields.Float('Result Progress', compute="_get_makloon_progress", copy=False)
    progress = fields.Float('Planning Progress', )#compute="_get_makloon_progress"
    source_po = fields.Many2one('purchase.order', 'PO')

    # po_count = fields.Integer(compute='_compute_po', string='Result', default=0)
    # state = fields.Selection(
    #     [('draft', 'Draft'), ('confirm', 'Confirmed')],
    #     string="State", track_visibility='onchange', default="draft")  # compute="_compute_state"

    # @api.depends('stage_ids')
    # def _get_makloon_progress(self):
    #     for rec in self:
    #         rec.progress = 0.0
    #         if rec.stage_ids:
    #             total = 0.0
    #             for record in rec.stage_ids:
    #                total += record.progress
    #         if total != 0.0 :
    #             rec.progress = (total / len(rec.stage_ids)) * 100

    # @api.one
    # @api.depends('po_ids')
    # def _compute_po(self):
    #     po_cn = 0
    #     if self.po_ids:
    #         po_cn = len(self.po_ids)
    #     self.po_count = po_cn
    #
    # # @api.multi
    # def button_confirm(self):
    #     self.write({'state': 'confirm'})
    #     self._create_po()
    #     return True
    #
    # # @api.multi
    # def _create_po(self):
    #     po_obj = self.env['purchase.order']
    #     # po_line_obj = self.env['purchase.order.line']
    #     for me in self:
    #         # if me.result_ids:
    #         po_data = {
    #             'origin': me.name,
    #             'partner_id': me.partner_id.id,
    #             'makloon_plan_id': me.id,
    #             'type_id': 'benang'
    #             # 'order_line': []
    #         }
    #         po_obj.create(po_data)
    #         # po_id = po_obj.create(po_data)
    #         # for rs in me.result_ids:
    #         #     line = {
    #         #         'name': rs.service_product_id.name,
    #         #         'order_id': po_id.id,
    #         #         'product_id': rs.service_product_id.id,
    #         #         'price_unit': rs.service_product_id.standard_price,
    #         #         'product_uom': rs.service_product_id.uom_id.id,
    #         #         'product_qty': rs.product_uom_qty,
    #         #         'date_planned': me.date_order
    #         #     }
    #         #     po_line_obj.create(line)
    #         return True
    #
    #     return False

    # @api.multi
    def action_view_po(self):
        action = self.env.ref('purchase.purchase_rfq').read()[0]

        po_id = self.mapped('po_ids')
        if len(po_id) > 1:
            action['domain'] = [('id', 'in', po_id.ids)]
        elif po_id:
            action['views'] = [(self.env.ref('purchase.purchase_order_form').id, 'form')]
            action['res_id'] = po_id.id
        return action