
from datetime import datetime
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class Product(models.Model):
    _inherit = 'product.product'
    
    mkt_categ_id        = fields.Many2one('marketing.category', string='Marketing Category')
    kd_product_mkt_id   = fields.Many2one('product.product', string='Kode Product Mkt')
    group_product_id    = fields.Many2one('group.product', string='Group Product')
    line_product_id     = fields.Many2one('line.product', string='Line Product')
    merk_product_id     = fields.Many2one('merk.product', string='Merk Product')
    lead_days           = fields.Integer(string='Lead')
    min_stock           = fields.Float(related="product_tmpl_id.min_stock",string='Mininum Stock')
    usage_daily         = fields.Float(string='Usage Daily',compute="_get_usage_daily")
    order_time          = fields.Float(string='Order Time',compute="_get_order_time")
    lead_time           = fields.Float(string='Lead Purchase',compute="_get_order_time")
    diameter            = fields.Float(string='Diameter')
    variable            = fields.Float(string='Variable')
    
    def _get_usage_daily(self):
        for line in self:
            today = fields.Datetime.now()
            week_ago = fields.Datetime.subtract(today,days=7)
            product_moves = self.env['stock.move.line'].search([('product_id','=',line.id),('picking_code','=','internal'),('date','>=',week_ago),('date','<=',today),('state','=','done')])
            line.usage_daily = sum(product_moves.mapped('qty_done')) / 7
    

    def _get_order_time(self):
        order_line = self.env['purchase.order.line']
        for line in self:
            line.order_time = 0
            order_line      = order_line.search([('product_id','=',line.id)]).sorted(lambda x: x.order_id,reverse = True)
            if order_line and order_line[0].purchase_request_lines and order_line[0].order_id.date_planned and order_line[0].order_id.date_approve:
                order_line      = order_line[0] if order_line else False
                date_pr         = order_line.purchase_request_lines.request_id.date_start 
                lead_receipt    = order_line.order_id.date_planned.date() - order_line.order_id.date_approve.date()
                lead_po         = (order_line.order_id.date_approve.date() - date_pr)
                line.order_time = lead_po.days
                lead_time       = lead_receipt
                line.lead_time  =  line.order_time + lead_time.days or 0
            else:
                line.order_time = 0
                lead_time       = 0
                line.lead_time  = 0

    
    # Start Overide From Base Odoo
    # def name_get(self):
        # # TDE: this could be cleaned a bit I think

        # def _name_get(d):
        #     name = d.get('name', '')
        #     code = self._context.get('display_default_code', True) and d.get('default_code', False) or False
        #     if code:
        #         name = '[%s] %s' % (code,name)
        #     return (d['id'], name)

        # partner_id = self._context.get('partner_id')
        # if partner_id:
        #     partner_ids = [partner_id, self.env['res.partner'].browse(partner_id).commercial_partner_id.id]
        # else:
        #     partner_ids = []
        # company_id = self.env.context.get('company_id')

        # # all user don't have access to seller and partner
        # # check access and use superuser
        # self.check_access_rights("read")
        # self.check_access_rule("read")

        # result = []

        # # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        # # Use `load=False` to not call `name_get` for the `product_tmpl_id`
        # self.sudo().read(['name', 'default_code', 'product_tmpl_id'], load=False)

        # product_template_ids = self.sudo().mapped('product_tmpl_id').ids

        # if partner_ids:
        #     supplier_info = self.env['product.supplierinfo'].sudo().search([
        #         ('product_tmpl_id', 'in', product_template_ids),
        #         ('name', 'in', partner_ids),
        #     ])
        #     # Prefetch the fields used by the `name_get`, so `browse` doesn't fetch other fields
        #     # Use `load=False` to not call `name_get` for the `product_tmpl_id` and `product_id`
        #     supplier_info.sudo().read(['product_tmpl_id', 'product_id', 'product_name', 'product_code'], load=False)
        #     supplier_info_by_template = {}
        #     for r in supplier_info:
        #         supplier_info_by_template.setdefault(r.product_tmpl_id, []).append(r)
        # for product in self.sudo():
        #     variant = product.product_template_attribute_value_ids._get_combination_name()
        #     print('variant==========', variant)
        #     print('variant==========', product.product_template_attribute_value_ids.ids)

        #     name = variant and "%s (%s)" % (product.name, variant) or product.name
        #     sellers = self.env['product.supplierinfo'].sudo().browse(self.env.context.get('seller_id')) or []
        #     if not sellers and partner_ids:
        #         product_supplier_info = supplier_info_by_template.get(product.product_tmpl_id, [])
        #         sellers = [x for x in product_supplier_info if x.product_id and x.product_id == product]
        #         if not sellers:
        #             sellers = [x for x in product_supplier_info if not x.product_id]
        #         # Filter out sellers based on the company. This is done afterwards for a better
        #         # code readability. At this point, only a few sellers should remain, so it should
        #         # not be a performance issue.
        #         if company_id:
        #             sellers = [x for x in sellers if x.company_id.id in [company_id, False]]
        #     if sellers:
        #         for s in sellers:
        #             seller_variant = s.product_name and (
        #                 variant and "%s (%s)" % (s.product_name, variant) or s.product_name
        #                 ) or False
        #             mydict = {
        #                       'id': product.id,
        #                       'name': seller_variant or name,
        #                       'default_code': s.product_code or product.default_code,
        #                       }
        #             temp = _name_get(mydict)
        #             if temp not in result:
        #                 result.append(temp)
        #     else:
        #         mydict = {
        #                   'id': product.id,
        #                   'name': name,
        #                   'default_code': product.default_code,
        #                   }
        #         result.append(_name_get(mydict))
        # return result
    # End Overide From Base Odoo

    def name_get(self):
        res = super(Product, self).name_get()
        for record in self:
            if record.categ_id.name == 'Finished Goods':
                machine = record.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.name == 'MACHINE').name
                size = record.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.name == 'SIZE').name
                shape = record.product_template_attribute_value_ids.filtered(lambda x: x.attribute_id.name == 'SHAPE').name
                # variant = record.product_id.product_template_attribute_value_ids._get_combination_name() or ''
                variant = ' (%s, %s, %s)' % (machine, size, shape)
                res.append((record.id, record.name + variant))
        return res
    
    
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    
    min_stock = fields.Float(string='Mininum Stock')
    alias = fields.Char(string='Alias')
    

class ProductSupplierInfo(models.Model):
    _inherit = 'product.supplierinfo'
    
    usage_daily         = fields.Float(string='Usage Daily',compute="_get_usage_daily")
    order_time          = fields.Float(string='Order Time',compute="_get_order_time")
    min_stock           = fields.Float(string='Minimum Stock')
    
    
    def _get_usage_daily(self):
        for line in self:
            today = fields.Datetime.now()
            week_ago = fields.Datetime.subtract(today,days=7)
            product_id = line.product_tmpl_id.product_variant_id.id
            product_moves = self.env['stock.move.line'].search([('product_id','=',product_id),('picking_code','=','internal'),('date','>=',week_ago),('date','<=',today),('state','=','done')])
            line.usage_daily = sum(product_moves.mapped('qty_done')) / 7
            
    
    def _get_order_time(self):
        order_line = self.env['purchase.order.line']
        for line in self:
            line.order_time = 0
            product_id = line.product_tmpl_id.product_variant_id.id
            order_line = order_line.search([('product_id','=',product_id),('partner_id','=',line.name.id)])
            tes = set(order_line.purchase_request_lines)
            import logging;
            _logger = logging.getLogger(__name__)
            _logger.warning('='*40)
            _logger.warning('order time')
            _logger.warning(tes)
            _logger.warning(order_line.purchase_request_lines.filtered(lambda l: l.purchase_state == 'purchase').mapped('date_start'))
            _logger.warning('='*40)