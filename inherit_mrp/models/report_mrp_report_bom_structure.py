from odoo import models, fields, api, _
from odoo.exceptions import UserError

class BomStructureReport(models.AbstractModel):
    _inherit = "report.mrp.report_bom_structure"


    def _get_bom(self, bom_id=False, product_id=False, line_qty=False, line_id=False, level=False):
        res = super(BomStructureReport, self)._get_bom(bom_id, product_id, line_qty, line_id, level)
        cost_ids = self.env['mrp.bom.cost'].search([('bom_id', '=', bom_id)])
        flowprocess_ids = self.env['mrp.bom.flowprocess'].search([('bom_id', '=', bom_id)])
        line_cost = []
        line_flowprocess = []
        total_price = 0
        for line in cost_ids:
            line_cost.append({
                        'name' : line.name.name,
                        'amount' : line.amount,
                        'amount_tot' : line.amount_tot,
                        'price_unit' : line.price_unit,
                        'amount_cost' : line.amount_cost,
                        'keterangan' : line.keterangan,
            })
            total_price += line.amount_cost
        for line in flowprocess_ids:
            line_flowprocess.append({
                        'process' : line.proses_master_id.name,
                        'no_urut' : line.no_urut,
                        'mesin'   : line.mesin_id.name,
                        'process_type' : line.process_type_id.name,
                        'price' : line.price,
            })
        print("=========_get_bom=============")
        print(line_flowprocess)
        res['total_price'] = total_price
        res['cost_ids'] = line_cost
        res['line_flowprocess'] = line_flowprocess
        return res