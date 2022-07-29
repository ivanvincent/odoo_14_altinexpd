from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

from odoo.exceptions import ValidationError

class EstimateConfirmWizard(models.TransientModel):
    _name = 'estimate.confirm.wizard'
    _description = 'Estimate Confirm Wizard'

    reason = fields.Text(string="Reason", required=True )

    def confirm(self):
        for me in self:
            self.ensure_one()

            ids = self.env['estimate'].browse(self._context.get('active_ids'))
            for line in ids:

                #_logger.info("line.id = %s " % (line.id))
                if line.state != 'draft':
                    raise ValidationError("Error Validate: Line(s) not in DRAFT state")

                line.action_confirm()
                line.message_post(body=me.reason)
        
        return


class EstimateValidateWizard(models.TransientModel):
    _name = 'estimate.validate.wizard'
    _description = 'Estimate Validate Wizard'

    reason = fields.Text(string="Reason", required=True )

    def validate(self):
        for me in self:
            self.ensure_one()

            ids = self.env['estimate'].browse(self._context.get('active_ids'))
            data = []
            for line in ids:

                #_logger.info("line.id = %s " % (line.id))
                if line.state != 'confirm':
                    raise ValidationError("Error Validate: Line(s) not in CONFIRM state")
                
                if line.product_qty:
                    data.append({
                        'estimate_id': line.id,
                        'estimate_type': line.estimate_type,
                        'customer_id': line.customer_id,
                        'divisi_id': line.divisi_id,
                        'group_id': line.group_id,
                        'route_id': line.route_id,
                        'route_jwk': line.route_jwk,
                        'commitment_date': str(line.commitment_date.strftime('%Y-%m-%d')),
                        'estimate_date': str(line.estimate_date.strftime('%Y-%m-%d')),
                        'product_id': line.product_id,
                        'product_qty': line.product_qty,
                    })

            #_logger.info("data original = %s " % (data))

            data = sorted(data, key=lambda x: (x['estimate_type'], x['customer_id'], x['commitment_date'][:10], x['estimate_date'][:10], x['product_id']))
            #_logger.info("data sorted = %s " % (data))

            vestimate_item = ''
            vestimate_data = []
            for item in data:

                vestimate_type   = item['estimate_type'] 
                vcustomer_id     = item['customer_id']
                vdivisi_id       = item['divisi_id']
                vgroup_id        = item['group_id']
                vroute_id        = item['route_id']
                vroute_jwk       = item['route_jwk']
                vcommitment_date = item['commitment_date']
                vestimate_date   = item['estimate_date']
                vproduct_id      = item['product_id']
                vproduct_qty     = item['product_qty']

                if vestimate_item != vestimate_type+str(vcustomer_id.id)+vcommitment_date+vestimate_date+str(vproduct_id.id):

                    vestimate_item = vestimate_type+str(vcustomer_id.id)+vcommitment_date+vestimate_date+str(vproduct_id.id)
                    vestimate_data.append({ 'key': vestimate_item,
                                            'estimate_type': vestimate_type,
                                            'customer_id': vcustomer_id,
                                            'divisi_id': vdivisi_id,
                                            'group_id': vgroup_id,
                                            'route_id': vroute_id,
                                            'route_jwk': vroute_jwk,
                                            'commitment_date': vcommitment_date,
                                            'estimate_date': vestimate_date,
                                            'product_id': vproduct_id,
                                            'product_qty': vproduct_qty
                                        })

            #_logger.info("estimate data = %s " % (vestimate_data))

            vestimate_item = ''
            vestimate_keys = []
            for item in vestimate_data:

                vestimate_type   = item['estimate_type'] 
                vcustomer_id     = item['customer_id']
                vdivisi_id       = item['divisi_id']
                vgroup_id        = item['group_id']
                vroute_id        = item['route_id']
                vroute_jwk       = item['route_jwk']
                vcommitment_date = item['commitment_date']
                vestimate_date   = item['estimate_date']
                vproduct_id      = item['product_id']
                vproduct_qty     = item['product_qty']

                if vestimate_item != vestimate_type+str(vcustomer_id.id)+vcommitment_date+vestimate_date:

                    vestimate_item = vestimate_type+str(vcustomer_id.id)+vcommitment_date+vestimate_date
                    vestimate_keys.append({ 'key': vestimate_item,
                                            'estimate_type': vestimate_type,
                                            'customer_id': vcustomer_id,
                                            'divisi_id': vdivisi_id,
                                            'group_id': vgroup_id,
                                            'route_id': vroute_id,
                                            'route_jwk': vroute_jwk,
                                            'commitment_date': vcommitment_date,
                                            'estimate_date': vestimate_date,
                                            'product_id': vproduct_id,
                                            'product_qty': vproduct_qty
                                        })

            vestimate_keys = sorted(vestimate_keys, key=lambda x: (x['commitment_date'][:10]))
            #_logger.info("estimate keys = %s " % (vestimate_keys))

            vso_line = []
            for x in vestimate_keys:

                xestimate_type   = x['estimate_type'] 
                xcustomer_id     = x['customer_id']
                xdivisi_id       = x['divisi_id']
                xgroup_id        = x['group_id']
                xroute_id        = x['route_id']
                xroute_jwk       = x['route_jwk']
                xcommitment_date = x['commitment_date']
                xestimate_date   = x['estimate_date']
                xproduct_id      = x['product_id']
                xproduct_qty     = x['product_qty']

                vestimate_ids = []

                xkey = x['key']
                #_logger.info("x-key = %s " % (xkey))

                for y in vestimate_data:

                    yestimate_type   = y['estimate_type'] 
                    ycustomer_id     = y['customer_id']
                    ydivisi_id       = y['divisi_id']
                    ygroup_id        = y['group_id']
                    yroute_id        = y['route_id']
                    yroute_jwk       = y['route_jwk']
                    ycommitment_date = y['commitment_date']
                    yestimate_date   = y['estimate_date']
                    yproduct_id      = y['product_id']
                    yproduct_qty     = y['product_qty']

                    if xkey == yestimate_type+str(ycustomer_id.id)+ycommitment_date+yestimate_date:

                        vproduct_qty = 0

                        ykey = y['key']
                        #_logger.info("y-key = %s " % (ykey))

                        for item in data:

                            zestimate_id     = item['estimate_id'] 
                            zestimate_type   = item['estimate_type'] 
                            zcustomer_id     = item['customer_id']
                            zdivisi_id       = item['divisi_id']
                            zgroup_id        = item['group_id']
                            zroute_id        = item['route_id']
                            zroute_jwk       = item['route_jwk']
                            zcommitment_date = item['commitment_date']
                            zestimate_date   = item['estimate_date']
                            zproduct_id      = item['product_id']
                            zproduct_qty     = item['product_qty']

                            if ykey == zestimate_type+str(zcustomer_id.id)+zcommitment_date+zestimate_date+str(zproduct_id.id):

                                vproduct_qty += item['product_qty']
                                vestimate_ids.append(zestimate_id)

                        if vproduct_qty:
                            vso_line.append((0,0,{  'type': yestimate_type,
                                                    'product_id': yproduct_id.id,
                                                    'product_uom_qty': vproduct_qty,
                                                    'product_uom': yproduct_id.uom_id.id
                                                }))

                if vso_line:

                    vso_vals = {'date_order': xestimate_date,
                                'commitment_date': xcommitment_date,
                                'partner_id': xcustomer_id.id,
                                'order_line': vso_line
                            }

                    _logger.info("sale order = %s " % (vso_vals))
                    so_id = self.env['sale.order'].create(vso_vals)

                    if so_id:

                        vso_vals = {
                                    'custom_div_id': xdivisi_id.id,
                                    'custom_group_id': xgroup_id.id,
                                    'custom_jalur_id': xroute_id.id,
                                    'custom_jalur_jwk': xroute_jwk,
                                }
                        so_id.write(vso_vals)

                        #_logger.info("estimate ids = %s " % (vestimate_ids))
                        for vest in vestimate_ids:

                            #_logger.info("estimate id = %s " % (vest))

                            est_id = self.env['estimate'].search([('id','=', vest)], limit=1)
                            if est_id:
                                est_id.write({
                                                'so_number': so_id.id,
                                                'state': 'done'
                                            })
                        so_id.sudo().action_confirm()

                    vso_line = []

        return

class EstimateSetToDraftWizard(models.TransientModel):
    _name = 'estimate.settodraft.wizard'
    _description = 'Estimate Set-to-Draft Wizard'

    reason = fields.Text(string="Reason", required=True )

    def settodraft(self):
        for me in self:
            self.ensure_one()

            ids = self.env['estimate'].browse(self._context.get('active_ids'))
            for line in ids:

                _logger.info("line.id = %s " % (line.id))
                if line.state == 'done':
                    raise ValidationError("Error Validate: Line(s) in DONE state")

                line.action_todraft()
                line.message_post(body=me.reason)
        
        return


class EstimateCancelWizard(models.TransientModel):
    _name = 'estimate.cancel.wizard'
    _description = 'Estimate Cancel Wizard'

    reason = fields.Text(string="Reason", required=True )

    def cancel(self):
        for me in self:
            self.ensure_one()

            ids = self.env['estimate'].browse(self._context.get('active_ids'))
            for line in ids:

                _logger.info("line.id = %s " % (line.id))
                if line.state != 'draft':
                    raise ValidationError("Error Validate: Line(s) not in DRAFT state")

                line.action_cancel()
                line.message_post(body=me.reason)
        
        return
