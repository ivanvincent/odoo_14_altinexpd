from odoo import models, fields, api, _
from odoo.exceptions import UserError

class ReportingPurchaseOrder(models.Model):
    _name = 'reporting.purchase.order'

    name       = fields.Char(string='Report Name')
    start_date = fields.Date(string='Start Date', default=fields.Date.today())
    end_date   = fields.Date(string='End Date', default=fields.Date.today())
    line_ids   = fields.One2many('reporting.purchase.order.line', 'report_id', string='Details')
    
    
    def clear_line(self):
        query = """ DELETE FROM reporting_purchase_order_line WHERE report_id = %s ;
                    DELETE FROM reporting_purchase_order_history WHERE report_id = %s ;"""%(self.id,self.id)
        self._cr.execute(query)
    
    
    def action_calculate(self):
        self.clear_line()
        date_start = " %s 00:00:00 "%self.start_date
        date_end = " %s 23:59:59 "%self.end_date
        
        query = """
        
                    insert into reporting_purchase_order_line (report_id,purchase_id,po_qty,po_received,po_remain_qty,pr_qty,rr_qty)(
                        select %s as report_id,po_id,sum(po_qty),sum(po_received),sum(po_qty) - sum(po_received),sum(pr_qty),sum(rr_qty)
                    FROM (
                 --  RR 
                    select row_number () over (),  
                        po.id as po_id ,
                        rrl.quantity as rr_qty,
                        0 as pr_qty ,
                        0 as po_qty,
                        0 as po_received,
                        0 as po_sisa
                        from purchase_order po 
                        left join purchase_order_line pol on pol.order_id = po.id 
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_order_line_id = pol.id 
                        left join purchase_request_line prl on prpolr.purchase_request_line_id = prl.id
                        left join purchase_request pr on prl.request_id = pr.id
                        left join request_requisition rr on rr.request_id = pr.id
                        left join request_requisition_line rrl on rrl.order_id = rr.id
                        where po.date_approve between '%s' and '%s' and po.state = 'purchase'
                    union
                    -- PR
                    select row_number () over (),  
                        po.id as po_id , 
                        0 as rr_qty,
                        prl.product_qty as pr_qty ,
                        0 as po_qty,
                        0 as po_received,
                        0 as po_sisa
                        from purchase_order po 
                        left join purchase_order_line pol on pol.order_id = po.id 
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_order_line_id = pol.id 
                        left join purchase_request_line prl on prpolr.purchase_request_line_id = prl.id
                        left join purchase_request pr on prl.request_id = pr.id
                        left join request_requisition rr on rr.request_id = pr.id
                        left join request_requisition_line rrl on rrl.order_id = rr.id
                        where po.date_approve between '%s' and '%s' and po.state = 'purchase'
                    union
                    -- PO
                    select row_number () over (),  
                        po.id as po_id , 
                        0 as rr_qty,
                        0 as pr_qty ,     
                        pol.product_qty as po_qty,
                        pol.qty_received as po_received,
                        0 as po_sisa
                        from purchase_order po 
                        left join purchase_order_line pol on pol.order_id = po.id 
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_order_line_id = pol.id 
                        left join purchase_request_line prl on prpolr.purchase_request_line_id = prl.id
                        left join purchase_request pr on prl.request_id = pr.id
                        left join request_requisition rr on rr.request_id = pr.id
                        left join request_requisition_line rrl on rrl.order_id = rr.id
                        where po.date_approve between '%s' and '%s' and po.state = 'purchase'
                        
                    ) as report group by po_id
                    );
                    
                    
                    insert into reporting_purchase_order_history (report_id,purchase_id,pr_id,rr_id,product_id,specification,pr_qty,rr_qty)(
                    select %s as report_id, 
 		                history.po_id , 
 		                history.pr_id , 
                        history.rr_id,
                        history.product_id,
                        history.spesification,
                        sum(history.pr_qty) as pr_qty,
                        sum(history.qty_rr) as rr_qty
                    from (
                        --RR
                        select row_number () over (),  
                            rr.id as rr_id ,
                            rrl.spesification,
                            rr.location_id as location_id,
                            pol.product_id as product_id,
                            rrl.quantity as qty_rr,
                            0 as qty_kirim,
                            0 as rr_qty_sisa ,
                            pr.id  as pr_id , 
                            pr.date_start  as pr_date,
                            0 as pr_qty , 
                            po.id as po_id , 
                            po.date_approve as po_date ,
                            0 as po_qty,
                            0 as po_receipt,
                            0 as po_sisa
                        from purchase_order po 
                        left join purchase_order_line pol on pol.order_id = po.id 
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_order_line_id = pol.id 
                        left join purchase_request_line prl on prpolr.purchase_request_line_id = prl.id
                        left join purchase_request pr on prl.request_id = pr.id
                        left join request_requisition rr on rr.request_id = pr.id
                        left join request_requisition_line rrl on rrl.order_id = rr.id
                        where po.date_approve between '%s' and '%s' and po.state = 'purchase'
                        union 
                        select row_number () over (), 
                            rr.id as rr_id ,
                            rrl.spesification ,
                            rr.location_id as location_id,
                            pol.product_id as product_id,
                            0 as qty_rr,
                            0 as qty_kirim,
                            0 as rr_qty_sisa ,
                            pr.id as pr_id , 
                            pr.date_start  as pr_date, 
                            prl.product_qty  as pr_qty , 
                            po.id as po_id ,
                            po.date_approve  as po_date,
                            0 as po_qty, 
                            0  as po_receipt,
                            0  as po_sisa
                        from purchase_order po 
                        left join purchase_order_line pol on pol.order_id = po.id 
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_order_line_id = pol.id 
                        left join purchase_request_line prl on prpolr.purchase_request_line_id = prl.id
                        left join purchase_request pr on prl.request_id = pr.id
                        left join request_requisition rr on rr.request_id = pr.id
                        left join request_requisition_line rrl on rrl.order_id = rr.id
                        left join stock_picking sp on sp.request_requisition_id = rr.id
                        left join stock_move_line sml on sml.picking_id = sp.id
                        where po.date_approve between '%s' and '%s' and po.state = 'purchase'
                        union 
                        select row_number () over (),  
                            rr.id as rr_id ,
                            rrl.spesification ,
                            rr.location_id as location_id,
                            pol.product_id as product_id,
                            0 as qty_rr,
                            0 as qty_kirim,
                            0 as rr_qty_sisa ,
                            pr.id as pr_id , 
                            pr.date_start  as pr_date, 
                            0  as pr_qty , 
                            po.id as po_id ,
                            po.date_approve  as po_date,
                            0 as po_qty, 
                            pol.qty_received  as po_receipt,
                            0 as po_sisa
                        from purchase_order po 
                        left join purchase_order_line pol on pol.order_id = po.id 
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_order_line_id = pol.id 
                        left join purchase_request_line prl on prpolr.purchase_request_line_id = prl.id
                        left join purchase_request pr on prl.request_id = pr.id
                        left join request_requisition rr on rr.request_id = pr.id
                        left join request_requisition_line rrl on rrl.order_id = rr.id
                        left join stock_picking sp on sp.request_requisition_id = rr.id
                        left join stock_move_line sml on sml.picking_id = sp.id
                        where po.date_approve between '%s' and '%s' and po.state = 'purchase'
                        union
                        select row_number () over (),  
                            rr.id as rr_id ,
                            rrl.spesification ,
                            rr.location_id as location_id,
                            pol.product_id as product_id,
                            0 as qty_rr,
                            sml.qty_done as qty_kirim,
                            0 as rr_qty_sisa ,
                            pr.id as pr_id , 
                            pr.date_start  as pr_date, 
                            0 as pr_qty , 
                            po.id as po_id , 
                            po.date_approve  as po_date,
                            0 as po_qty, 
                            0 as po_receipt,
                            0 as po_sisa
                        from purchase_order po 
                        left join purchase_order_line pol on pol.order_id = po.id 
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_order_line_id = pol.id 
                        left join purchase_request_line prl on prpolr.purchase_request_line_id = prl.id
                        left join purchase_request pr on prl.request_id = pr.id
                        left join request_requisition rr on rr.request_id = pr.id
                        left join request_requisition_line rrl on rrl.order_id = rr.id
                        left join stock_picking sp on sp.request_requisition_id = rr.id
                        left join stock_move_line sml on sml.picking_id = sp.id
                        where po.date_approve between '%s' and '%s'  and po.state = 'purchase'
                        union
                        select row_number () over (),  
                            rr.id as rr_id ,
                            rrl.spesification ,
                            rr.location_id as location_id,
                            pol.product_id as product_id,
                            0 as qty_rr,
                            0 as qty_kirim,
                            0 as rr_qty_sisa ,
                            pr.id as pr_id , 
                            pr.date_start  as pr_date, 
                            0 as pr_qty , 
                            po.id as po_id , 
                            po.date_approve  as po_date,
                            pol.product_qty as po_qty, 
                            0 as po_receipt,
                            0 as po_sisa
                        from purchase_order po 
                        left join purchase_order_line pol on pol.order_id = po.id 
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_order_line_id = pol.id 
                        left join purchase_request_line prl on prpolr.purchase_request_line_id = prl.id
                        left join purchase_request pr on prl.request_id = pr.id
                        left join request_requisition rr on rr.request_id = pr.id
                        left join request_requisition_line rrl on rrl.order_id = rr.id
                        left join stock_picking sp on sp.request_requisition_id = rr.id
                        left join stock_move_line sml on sml.picking_id = sp.id
                        where po.date_approve between '%s' and '%s'  and po.state = 'purchase'
                        union
                        select row_number () over (), 
                            rr.id as rr_id ,
                            rrl.spesification ,
                            rr.location_id as location_id,
                            pol.product_id as product_id,
                            0 as qty_rr,
                            0 as qty_kirim,
                            0 as rr_qty_sisa ,
                            pr.id as pr_id , 
                            pr.date_start as pr_date,
                            0 as pr_qty,
                            po.id as po_id,
                            po.date_approve as po_date,
                            0 as po_qty, 
                            pol.qty_received as po_receipt,
                            0 as po_sisa
                        from purchase_order po 
                        left join purchase_order_line pol on pol.order_id = po.id 
                        left join purchase_request_purchase_order_line_rel prpolr on prpolr.purchase_order_line_id = pol.id 
                        left join purchase_request_line prl on prpolr.purchase_request_line_id = prl.id
                        left join purchase_request pr on prl.request_id = pr.id
                        left join request_requisition rr on rr.request_id = pr.id
                        left join request_requisition_line rrl on rrl.order_id = rr.id
                        left join stock_picking sp on sp.request_requisition_id = rr.id
                        left join stock_move_line sml on sml.picking_id = sp.id
                        where po.date_approve between '%s' and '%s' and po.state = 'purchase'
                        ) as history
                        group by history.po_id,history.rr_id,history.pr_id,history.product_id,history.spesification
                        order by history.pr_id,history.product_id
                    )
                    
                    
                    
                    
                    
                    
        """%(self.id,date_start,date_end,
             date_start,date_end,
             date_start,date_end,
             self.id,date_start,date_end,
             date_start,date_end,
             date_start,date_end,
             date_start,date_end,
             date_start,date_end,
             date_start,date_end,
             )
        self._cr.execute(query)
        import logging;
        _logger = logging.getLogger(__name__)
        _logger.warning('='*40)
        _logger.warning(query)
        _logger.warning('='*40)
        for line in self.line_ids:
            line.update_reporting_line()

    


class ReportingPurchaseOrderLine(models.Model):
    _name = 'reporting.purchase.order.line'

    
    report_id     = fields.Many2one('reporting.purchase.order', string='Report')
    purchase_id   = fields.Many2one('purchase.order', string='Purchase')
    partner_id    = fields.Many2one('res.partner',related="purchase_id.partner_id", string='Vendor')
    po_date       = fields.Datetime(related='purchase_id.date_approve', string='Date Approve')
    po_qty        = fields.Integer(string='PO Quantity')
    po_received   = fields.Integer(string='Received')
    po_remain_qty = fields.Integer(string='Sisa PO')
    pr_qty        = fields.Integer(string='PR Quantity')
    rr_qty        = fields.Integer(string='RR Quantity')
    history_ids = fields.One2many('reporting.purchase.order.history', 'report_line_id', string='History')
    
    
    def update_reporting_line(self):
        for rec in self:
            query = " update reporting_purchase_order_history set report_line_id = %s  where report_id = %s and purchase_id = %s  " % (
                rec.id, rec.report_id.id, rec.purchase_id.id)
            self._cr.execute(query)
    
    

class ReportingPurchaseOrderHistory(models.Model):
    _name = 'reporting.purchase.order.history'

    
    report_id       = fields.Many2one('reporting.purchase.order', string='Report')
    report_line_id  = fields.Many2one('reporting.purchase.order.line', string='Report Line')
    purchase_id     = fields.Many2one('purchase.order', string='Purchase')
    warehouse_id    = fields.Many2one('stock.warehouse', string='Stock Warehouse')
    location_id     = fields.Many2one('stock.location', string='Location',related='rr_id.location_id')
    pr_id           = fields.Many2one('purchase.request', string='Purchase Request')
    rr_id           = fields.Many2one('request.requisition', string='Request Requisition')
    specification   = fields.Char(string='Specification')
    product_id      = fields.Many2one('product.product', string='Product')
    product_uom_id  = fields.Many2one(related="product_id.uom_id", string='Satuan')
    pr_qty          = fields.Float(string='PR Quantity')
    rr_qty          = fields.Float(string='RR Quantity')
    
    
    