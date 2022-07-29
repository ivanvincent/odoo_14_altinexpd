from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

from odoo.exceptions import ValidationError


class EstimateAdjustmentWizard(models.TransientModel):
    _name = 'estimate.adjustment.wizard'
    _description = 'Estimate Adjustment Wizard'

    adjustment_type = fields.Selection([('inc','Increase'),
                                        ('dec','Decrease')],
                                        default="inc", string="Type", required="1")
    compute_value = fields.Selection([  ('fixed', 'Fixed'),
                                        ('percentage', 'Percentage')], 
                                        index=True, default='fixed', required=True)
    fixed_value = fields.Float('Fixed Value')
    percent_value = fields.Float('Percentage Value')

    reason = fields.Text(string="Reason", required=True )

    def adjust(self):
        for me in self:
            self.ensure_one()

            if me.compute_value == 'fixed':
                if me.fixed_value <= 0:
                    raise ValidationError("Error Validate: Value")
            else:
                if me.percent_value <= 0:
                    raise ValidationError("Error Validate: Value")

            ids = self.env['estimate'].browse(self._context.get('active_ids'))
            for line in ids:

                _logger.info("line.id = %s " % (line.id))

                if line.state != 'draft':
                    raise ValidationError("Error Validate: Line(s) not in DRAFT state")

                vproduct_qty = line.product_qty
                _logger.info("line.product_qty => %s " % (vproduct_qty))

                if me.adjustment_type == 'inc':
                    if me.compute_value == 'fixed':
                        vproduct_qty += me.fixed_value
                    else:
                        vproduct_qty += (vproduct_qty *(me.percent_value/100))
                else: 
                    if me.compute_value == 'fixed':
                        vproduct_qty -= me.fixed_value
                    else:
                        vproduct_qty -= (vproduct_qty *(me.percent_value/100))
                    vproduct_qty = max(0,vproduct_qty)

                estimate_vals = {
                    'product_qty': round(vproduct_qty)
                }
                line.write(estimate_vals)
                line.message_post(body=me.reason)

        return 
