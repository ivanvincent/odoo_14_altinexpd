from odoo import models, fields, api, _ ,tools
from odoo.exceptions import UserError

class ReportingStockRequest(models.Model):
    _name = 'reporting.stock.request'

    name         = fields.Char(string='Reporting')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    date_start   = fields.Date(string='Date Start', default=fields.Date.today())
    date_end     = fields.Date(string='Date End', default=fields.Date.today())
    line_ids     = fields.One2many('reporting.stock.request.line', 'report_id', string='Detals')
    
    
    
    
    def action_calculate(self):
        query = "DELETE FROM reporting_stock_request_line where report_id = %s"%(self.id)
        self._cr.execute(query)
        query = """ 
                insert into reporting_stock_request_line (
                    report_id,rr_id,rr_date,spesification,product_id,location_id,rr_qty,pr_id,pr_date,pr_qty,po_id,po_date,po_qty,po_receipt,po_sisa
                    )(
                        select %s as report_id , report.rr_id,report.rr_date,report.spesification,report.product_id,report.location_id,sum(report.qty_rr) as rr_qty,
 		                report.pr_id , report.pr_date,sum(report.pr_qty) as pr_qty,report.po_id,date(report.po_date) as po_date,sum(report.po_qty),sum(report.po_receipt) as po_receipt ,sum(report.po_qty) - sum(report.po_receipt) as po_sisa
                    from (
                        select row_number () over (),  rr.id as rr_id ,rr.request_date as rr_date,rrl.spesification ,rr.location_id as location_id,rrl.product_id as product_id,rrl.quantity as qty_rr,0 as qty_kirim,0 as rr_qty_sisa ,
                        pr.id  as pr_id , pr.date_start  as pr_date, 0 as pr_qty , po.id as po_id , po.date_approve  as po_date ,0 as po_qty,0 as po_receipt,0 as po_sisa
                        from request_requisition rr 
                        left join request_requisition_line rrl on rrl.order_id = rr.id 
                        left join purchase_request pr on rr.request_id = pr.id 
                        left join purchase_request_line prl on prl.request_id = pr.id
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_request_line_id = prl.id 
                        left join purchase_order_line pol on prpolr.purchase_order_line_id = pol.id
                        left join purchase_order po on pol.order_id = po.id
                        where rr.warehouse_id = '%s' and rr.request_date between '%s' and '%s'
                        union 
                        select row_number () over (),  rr.id as rr_id ,rr.request_date as rr_date,rrl.spesification ,rr.location_id as location_id,rrl.product_id as product_id,0 as qty_rr,0 as qty_kirim,0 as rr_qty_sisa ,
                        pr.id as pr_id , pr.date_start  as pr_date, prl.product_qty  as pr_qty , po.id as po_id , po.date_approve  as po_date,0 as po_qty, 0  as po_receipt,0  as po_sisa
                        from request_requisition rr 
                        left join request_requisition_line rrl on rrl.order_id = rr.id 
                        left join stock_picking sp on sp.request_requisition_id = rr.id 
                        left join stock_move sm on sm.picking_id = sp.id
                        left join stock_move_line sml on sml.move_id =sm.id
                        left join purchase_request pr on rr.request_id = pr.id 
                        left join purchase_request_line prl on prl.request_id = pr.id
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_request_line_id = prl.id 
                        left join purchase_order_line pol on prpolr.purchase_order_line_id = pol.id
                        left join purchase_order po on pol.order_id = po.id
                        where rr.warehouse_id = '%s' and rr.request_date between '%s' and '%s'
                        union 
                        select row_number () over (),  rr.id as rr_id ,rr.request_date as rr_date,rrl.spesification ,rr.location_id as location_id,rrl.product_id as product_id,0 as qty_rr,0 as qty_kirim,0 as rr_qty_sisa ,
                        pr.id as pr_id , pr.date_start  as pr_date, 0  as pr_qty , po.id as po_id , po.date_approve  as po_date,0 as po_qty, pol.qty_received  as po_receipt,0  as po_sisa
                        from request_requisition rr 
                        left join request_requisition_line rrl on rrl.order_id = rr.id 
                        left join stock_picking sp on sp.request_requisition_id = rr.id 
                        left join stock_move sm on sm.picking_id = sp.id
                        left join stock_move_line sml on sml.move_id =sm.id
                        left join purchase_request pr on rr.request_id = pr.id 
                        left join purchase_request_line prl on prl.request_id = pr.id
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_request_line_id = prl.id 
                        left join purchase_order_line pol on prpolr.purchase_order_line_id = pol.id
                        left join purchase_order po on pol.order_id = po.id
                        where rr.warehouse_id = '%s' and rr.request_date between '%s' and '%s'
                        union
                        select row_number () over (),  rr.id as rr_id ,rr.request_date as rr_date,rrl.spesification ,rr.location_id as location_id,rrl.product_id as product_id,0 as qty_rr,sml.qty_done as qty_kirim,0 as rr_qty_sisa ,
                        pr.id as pr_id , pr.date_start  as pr_date, 0  as pr_qty , po.id as po_id , po.date_approve  as po_date,0 as po_qty, 0  as po_receipt,0  as po_sisa
                        from request_requisition rr 
                        left join request_requisition_line rrl on rrl.order_id = rr.id 
                        left join stock_picking sp on sp.request_requisition_id = rr.id 
                        left join stock_move sm on sm.picking_id = sp.id
                        left join stock_move_line sml on sml.move_id =sm.id
                        left join purchase_request pr on rr.request_id = pr.id 
                        left join purchase_request_line prl on prl.request_id = pr.id
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_request_line_id = prl.id 
                        left join purchase_order_line pol on prpolr.purchase_order_line_id = pol.id
                        left join purchase_order po on pol.order_id = po.id
                        where rr.warehouse_id = '%s' and rr.request_date between '%s' and '%s'
                        union
                        select row_number () over (),  rr.id as rr_id ,rr.request_date as rr_date,rrl.spesification ,rr.location_id as location_id,rrl.product_id as product_id,0 as qty_rr,0 as qty_kirim,0 as rr_qty_sisa ,
                        pr.id as pr_id , pr.date_start  as pr_date, 0  as pr_qty , po.id as po_id , po.date_approve  as po_date,pol.product_qty as po_qty, 0 as po_receipt,0  as po_sisa
                        from request_requisition rr 
                        left join request_requisition_line rrl on rrl.order_id = rr.id 
                        left join stock_picking sp on sp.request_requisition_id = rr.id 
                        left join stock_move sm on sm.picking_id = sp.id
                        left join stock_move_line sml on sml.move_id =sm.id
                        left join purchase_request pr on rr.request_id = pr.id 
                        left join purchase_request_line prl on prl.request_id = pr.id
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_request_line_id = prl.id 
                        left join purchase_order_line pol on prpolr.purchase_order_line_id = pol.id
                        left join purchase_order po on pol.order_id = po.id
                        where rr.warehouse_id = '%s' and rr.request_date between '%s' and '%s'
                        union
                        select row_number () over (),  rr.id as rr_id ,rr.request_date as rr_date,rrl.spesification ,rr.location_id as location_id,rrl.product_id as product_id,0 as qty_rr,0 as qty_kirim,0 as rr_qty_sisa ,
                        pr.id as pr_id , pr.date_start  as pr_date, 0  as pr_qty , po.id as po_id , po.date_approve  as po_date,0 as po_qty, pol.qty_received as po_receipt,0  as po_sisa
                        from request_requisition rr 
                        left join request_requisition_line rrl on rrl.order_id = rr.id 
                        left join stock_picking sp on sp.request_requisition_id = rr.id 
                        left join stock_move sm on sm.picking_id = sp.id
                        left join stock_move_line sml on sml.move_id =sm.id
                        left join purchase_request pr on rr.request_id = pr.id 
                        left join purchase_request_line prl on prl.request_id = pr.id
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_request_line_id = prl.id 
                        left join purchase_order_line pol on prpolr.purchase_order_line_id = pol.id
                        left join purchase_order po on pol.order_id = po.id
                        where rr.warehouse_id = '%s' and rr.request_date between '%s' and '%s'
                        ) as report
                        group by report.rr_id,report.rr_date,report.spesification,report.location_id,report.product_id,report.pr_id,report.pr_date,report.po_id,report.po_date
                        order by report.rr_id,report.product_id
                    )
                """%(self.id,self.warehouse_id.id,self.date_start,self.date_end,
                     self.warehouse_id.id,self.date_start,self.date_end,
                     self.warehouse_id.id,self.date_start,self.date_end,
                     self.warehouse_id.id,self.date_start,self.date_end,
                     self.warehouse_id.id,self.date_start,self.date_end,
                     self.warehouse_id.id,self.date_start,self.date_end,
                     )
        self._cr.execute(query)
        import logging;
        _logger = logging.getLogger(__name__)
        _logger.warning('='*40)
        _logger.warning(query)
        _logger.warning('='*40)
        
        

class ReportingStockRequestLine(models.Model):
    _name = 'reporting.stock.request.line'

    report_id    = fields.Many2one(string='Reporting')
    location_id  = fields.Many2one('stock.location', string='Location')
    product_id   = fields.Many2one('product.product', string='Product')
    uom_id       = fields.Many2one('uom.uom', related='product_id.uom_id', string='Uom')
    rr_id        = fields.Many2one('request.requisition', string='RR Number')
    rr_date      = fields.Date(string='RR Date')
    rr_qty       = fields.Float(string='RR Quantity')
    spesification= fields.Char(string='Specification')
    rr_kirim     = fields.Float(string='RR Qty Kirim',compute='get_rr_kirim',)
    rr_sisa      = fields.Float(string='RR Qty Sisa',compute='get_rr_kirim')
    pr_id        = fields.Many2one('purchase.request', string='PR Number')
    pr_date      = fields.Date(string='PR Date')
    pr_qty       = fields.Float(string='PR Quantity')
    po_id        = fields.Many2one('purchase.order', string='PO Number')
    po_date      = fields.Date(string='PO Date')
    po_qty       = fields.Float(string='PO Quantity')
    po_receipt   = fields.Float(string='PO Receipt')
    po_sisa      = fields.Float(string='PO Sisa')
    
    
    def get_rr_kirim(self):
        for line in self:
            picking_ids = self.env['stock.picking'].search([('request_requisition_id','=',line.rr_id.id),('state','=','done')])
            if len(picking_ids) == 1:
                line.rr_kirim = sum(picking_ids.move_ids_without_package.filtered(lambda m:m.product_id.id == line.product_id.id).mapped('quantity_done'))
                line.rr_sisa = line.rr_qty - line.rr_kirim
            elif len(picking_ids) > 1:
                line.rr_kirim = sum(picking_ids.move_ids_without_package.filtered(lambda m:m.product_id.id == line.product_id.id).mapped('quantity_done'))
                line.rr_sisa = line.rr_qty - line.rr_kirim
            else:
                line.rr_kirim = 0
                line.rr_sisa = 0
                
        