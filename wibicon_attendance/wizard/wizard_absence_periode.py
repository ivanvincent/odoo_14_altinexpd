from odoo import models, fields, api, _
from odoo.exceptions import UserError

class WizardAbsencePeriode(models.TransientModel):
    _name = 'wizard.absence.periode'

    date_start = fields.Date(string='Date Start', default=fields.Date.today(), required=True, )
    date_end = fields.Date(string='Date End', default=fields.Date.today(), required=True, )

    def action_input_data(self):        
        query_delete = """ 
                        DELETE FROM hr_attendance where to_char(tanggal, 'YYYY-MM-DD') BETWEEN '%s' AND '%s';
                       """ % (self.date_start, self.date_end)
        self._cr.execute(query_delete)
        query = """ 
                INSERT into hr_attendance (employee_id , tanggal , check_in, check_out)
                select * from (
                select employee_id, tanggal,max(jamin) as jam_in ,max(jamout) as jam_out from (
                select employee_id, tanggal, min(jam) as jamin ,null as jamout from (
                select employee_id,to_date (to_char (checktime, 'YYYY-MM-DD'), 'YYYY-MM-DD') as tanggal,checktime as jam,checktype,sn from checkinout
                where checktype='O' and to_date (to_char (checktime, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s'
                    ) as a group by employee_id,tanggal
                    
                union

                select employee_id, tanggal,null as jami, max(jam) as jamout from (
                select employee_id,to_date(to_char (checktime, 'YYYY-MM-DD'), 'YYYY-MM-DD') as tanggal,checktime as jam,checktype,sn from checkinout
                where checktype='I' and to_date(to_char (checktime, 'YYYY-MM-DD'), 'YYYY-MM-DD') between '%s' and '%s'
                    ) as a group by employee_id,tanggal
                    ) as a group by employee_id,tanggal
                    ) as a where jam_in is not null and jam_out is not null and employee_id is not null
                """ % (self.date_start, self.date_end, self.date_start, self.date_end)
        self._cr.execute(query)