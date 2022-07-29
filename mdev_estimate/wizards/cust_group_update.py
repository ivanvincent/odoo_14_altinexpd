from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)

from odoo.exceptions import ValidationError


class EstimateAdjustmentWizard(models.TransientModel):
    _name = 'cust.group.update.wizard'
    _description = 'Customer Update Wizard'

    update_type = fields.Selection([
                                    ('cust_tdlv', 'Cust. Dlv Time'),
                                    ('type',      'Type'),
                                    ('cluster',   'Cluster'),
                                    ('account',   'Account'),
                                    ('division',  'Division'),
                                    ('group',     'Group'),
                                    ('group_tdlv','Group Dlv Time'),
                                    ('route',     'Route'),
                                    ('sales',     'Salesperson'),
                                    ('schedule',  'Schdl. Day'),
                                    ('hour',      'Schdl. Hour')],
                                    default='route', string="Type")

    cust_type = fields.Selection([  ('mt', 'MT'),
                                    ('gt', 'GT'),
                                    ('po', 'PO'),
                                    ('ro', 'RO'),
                                    ('to', 'TO')],
                                    default='mt' )

    cust_cdlv = fields.Float(string="Delivery", default=0 )

    cust_acc = fields.Selection([(  'indomaret','Indomaret'),
									('alfagroup','Alfa Group'),
									('lainnya','Lainnya')
                                ], string="Account" )
    cust_div = fields.Many2one('res.partner.divisi', string="Division" )

    cust_group = fields.Many2one('res.partner.group', string="Group" )
    cust_cluster = fields.Many2one('res.partner.cluster', string="Cluster" )
    cust_gdlv = fields.Float(string="Delivery", default=0 )

    cust_route = fields.Many2one('res.partner.jalur', string="Route" )
    cust_sales = fields.Many2one("hr.employee", "Salesperson" )

    cust_dschdl = fields.Selection([
                                    ('1', 'Senin'),
                                    ('2', 'Selasa'),
                                    ('3', 'Rabu'),
                                    ('4', 'Kamis'),
                                    ('5', 'Jumat'),
                                    ('6', 'Sabtu'),
                                    ('7', 'Minggu')
                                ], string='Schdl. Day')
    cust_hschdl = fields.Float("Schdl. Hr", default=0 )

    #reason = fields.Text(string="Reason", required=True )

    def update(self):
        for me in self:
            self.ensure_one()

            if not me.update_type:
                raise ValidationError("ValidationError: Update Type not selected")
            
            vtype = me.update_type
            vValue = True
            if vtype == 'type':
                vValue = me.cust_type

            elif vtype == 'cluster':
                vValue = me.cust_cluster

            elif vtype == 'account':
                vValue = me.cust_acc

            elif vtype == 'division':
                vValue = me.cust_div

            elif vtype == 'group':
                vValue = me.cust_group
                
            elif vtype == 'route':
                vValue = me.cust_route

            elif vtype == 'sales':
                vValue = me.cust_sales

            elif vtype == 'schedule':
                vValue = me.cust_dschdl

            elif vtype == 'hour':
                vValue = me.cust_hschdl
                
            if not vValue:
                raise ValidationError("ValidationError: Value not defined")

            ids = self.env['res.partner.jalur.line'].browse(self._context.get('active_ids'))
            for line in ids:

                _logger.info("line.id = %s " % (line.id))
                
                if vtype == 'type':
                    line.jalur_line_id.customer_type = me.cust_type

                elif vtype == 'cluster':
                    line.jalur_line_id.cluster_id = me.cust_cluster

                elif vtype == 'cust_tdlv':
                    line.jalur_line_id.customer_lead = me.cust_cdlv

                elif vtype == 'account':
                    line.jalur_line_id.custom_acc_id = me.cust_acc

                elif vtype == 'division':
                    line.jalur_line_id.custom_div_id = me.cust_div

                elif vtype == 'group':
                    line.jalur_line_id.custom_group_id = me.cust_group

                elif vtype == 'group_tdlv':
                    line.jalur_line_id.custom_group_id.delivery_days = me.cust_gdlv

                elif vtype == 'route':
                    line.jalur_id = me.cust_route

                elif vtype == 'sales':
                    line.salesperson_id = me.cust_sales

                elif vtype == 'schedule':
                    line.jwk = me.cust_dschdl

                elif vtype == 'hour':
                    line.jam = me.cust_hschdl
                
                #line.message_post(body=me.reason)

        return 
