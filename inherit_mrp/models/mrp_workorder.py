from email.policy import default
from odoo import models, fields, api, _
from odoo import models, fields, api, _,SUPERUSER_ID
from odoo.exceptions import UserError
from datetime import datetime,timedelta,time
import logging
_logger = logging.getLogger(__name__)

SHIFT_SELECTION = [("A","A"),("B","B"),("C","C")]

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    parameter_ids      = fields.One2many('mrp.workorder.parameter', 'workorder_id', string='Parameter')
    mesin_id           = fields.Many2one('mrp.machine', string='Machine')
    program_id         = fields.Many2one('mrp.program', string='Program')
    hours              = fields.Float(related='program_id.hours', string='Hours')
    program_duration   = fields.Float(related='program_id.duration', string='Duration',store=True,)
    employee_id        = fields.Many2one('hr.employee', string='Operator', store=True,)
    shift              = fields.Selection([("A","A"),("B","B"),("C","C")], string='Shift', store=True,)
    qc_pass            = fields.Selection([("uncheck","Uncheck"),("pass","Passed"),("intermediate","Intermediate"),("fail","Failed")], string='Qc Pass',default="uncheck")
    note               = fields.Text(string='Note')
    is_reprocess       = fields.Boolean(string='Reprocess ?', default=False)
    no_urut            = fields.Integer(string='No Urut', compute="_compute_no_urut")
    is_planning        = fields.Boolean(related='workcenter_id.is_planning', string='Is Planning',store=True,)
    production_type_id = fields.Many2one(related='production_id.type_id', string='Production Type')
    html_color         = fields.Char(related='production_id.html_color', string='Color')
    final_set_id       = fields.Many2one('mrp.production.final.set', string='Final Set')

    def _read(self, fields):
        res = super()._read(fields)
        if self.env.context.get('display_product_and_color') and 'mesin_id' in self.env.context.get('group_by', []):
            name_field = self._fields['name']
            for record in self.with_user(SUPERUSER_ID):
                self.env.cache.set(record, name_field,' '+ record.workcenter_id.name + ' ' + record.production_id.name )
        return res
    
    
    @api.model
    def need_to_sort(self,sort_date):
        query = """
                select 
                    distinct(mesin_id) as mesin_id from mrp_workorder  
                where 
                    state != 'done' 
                and 
                    is_planning = True
                and 
                    date_planned_start >= '%s'
                """%(fields.Datetime.subtract(datetime.combine(fields.Date.to_date(sort_date), datetime.min.time()), hours=7))
                # """%(fields.Datetime.subtract(fields.Date.to_date(sort_date), hours=7))
                
        self._cr.execute(query)
        results = self._cr.dictfetchall()
        for res in results:
            query = """
                    select 
                        mw.id,
                        mw.date_planned_start ,
                        mw.date_planned_finished,
                        mw.program_duration,
                        mw.production_id,
                        mrp.name as batch,
                        mc.name as mesin_name,
                        mw.state
                    from 
                        mrp_workorder mw 
                    left join
                        mrp_production mrp
                    on
                        mw.production_id = mrp.id
                    left join
                        mrp_machine mc
                    on
                        mw.mesin_id = mc.id
                    where 
                        mw.state != 'done' 
                    and 
                        mw.is_planning = True
                    and 
                        mw.date_planned_start >= '%s'
                    and 
                        mw.mesin_id = %s
                    order by mw.id,mw.production_id
            """%(fields.Datetime.subtract(datetime.combine(fields.Date.to_date(sort_date), datetime.min.time()), hours=7),res.get('mesin_id'))
            # """%(fields.Datetime.subtract(fields.Date.to_date(sort_date), hours=7),res.get('mesin_id'))
            self._cr.execute(query)
            wo_list = self._cr.dictfetchall()
            date_list = []
            for idx,row in enumerate(wo_list):
                prev = date_list[idx - 1] if idx >= 1 else None
                # start_prod      = fields.Datetime.subtract(fields.Datetime.add(datetime.combine(fields.Date.to_date(sort_date), datetime.min.time()),hours=6,minutes=30),hours=7)
                workorder_id    = row.get('id')
                duration        = row.get('program_duration')
                date_start      = fields.Datetime.subtract(fields.Datetime.add(datetime.combine(fields.Date.to_date(sort_date), datetime.min.time()),hours=6,minutes=30),hours=7)
                # date_start      = row.get('date_planned_start')
                date_finished   = fields.Datetime.add(date_start,minutes=duration)
                # date_finished   = row.get('date_planned_finished')
                
                
                if prev is not None:
                    date_start = prev.get('date_planned_finished')
                    ext_duration = timedelta(minutes=duration)
                    date_finished = date_start + ext_duration
                
                
                query = """
                    UPDATE 
                        mrp_workorder 
                    SET 
                        date_planned_start = '%s',
                        date_planned_finished = '%s'
                    WHERE
                        id = %s
                    returning id
                    """%(date_start,
                        date_finished,
                        workorder_id)
                self._cr.execute(query)
                self._cr.commit()
                date_list.append({
                        'date_planned_start': date_start,
                        'date_planned_finished': date_finished,
                    })
        
      
        
        
        return True
    
        
    
    @api.onchange('state')
    def _onchange_state(self):
        if self.production_id:
            self.production_id._work_in_progress()
            
    @api.onchange('qc_pass')
    def _onchange_qc_pass(self):
        if self.production_id:
            self.production_id._compute_dyeing_failed()

    def copy(self, default=None):
        default = dict(default or {})
        ctx = self.env.context
        if ctx.get('reprocess', False):
            default.update({
                'duration_expected': False,
                'duration': False,
                'state': False,
                'is_reprocess': True,
                'qc_pass': 'uncheck',
                'note': False,
                'state': 'ready',

            })
        res = super(MrpWorkorder, self).copy(default)
        return res

    def _compute_no_urut(self):
        for rec in self:
            rec.no_urut = int(rec.name)

    def name_get(self):
        result = []
        for wo in self:
            result.append((wo.id, str(wo.name) + " " + str(wo.workcenter_id.name)))
        return result

    @api.model
    def create(self, vals):
        if 'production_id' in vals:
            productin_obj =  self.env['mrp.production'].browse(vals.get('production_id'))
            vals['product_uom_id'] = productin_obj.product_uom_id.id
            vals['consumption'] = productin_obj.consumption
        res = super(MrpWorkorder, self).create(vals)
        return res
class MrpMachine(models.Model):
    _inherit = 'mrp.machine'

    workcenter_id = fields.Many2one('mrp.workcenter', string='Work Center')