from odoo import models, fields, api, _
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def group_by_nozle_grade(self):
        # query = """
        #             select
        #             sml.nozle as nozle,
        #             g.name as grade
        #             from stock_move_line sml
        #             left join stock_production_lot spl on sml.lot_id = spl.id
        #             left join makloon_grade g on spl.grade_id = g.id
        #             where picking_id = %s
        #             GROUP BY sml.nozle, g.name
        #             ORDER BY sml.nozle, g.name
        #         """ % (self.id)
        # self._cr.execute(query)
        # res = self._cr.dictfetchall()
        result = []
        for a in set(self.move_line_ids_without_package.mapped('nozle')):
            result.append(self.get_selection_label('stock.move.line', 'nozle', a))
        return sorted(result)

    @api.model
    def get_selection_label(self, object, field_name, field_value):
        return _(dict(self.env[object].fields_get(allfields=[field_name])[field_name]['selection'])[field_value])



    def action_print(self):
        return {
            'type'      : 'ir.actions.act_window',
            'name'      : "Print",
            'res_model' : 'print.stock.wizard',
            'target'    : 'new',
            'view_id'   : self.env.ref('my_report.print_stock_wizard_form').id,
            'view_mode' : 'form',
            'context'   : {'default_picking_id': self.id,},
        }