from odoo import api, fields, models, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import dateutil.parser
import pandas_access as mdb
import jaydebeapi
import pandas as pd


# """
#         [   { 'name':'Normal Working Days paid at 100%',
#               'cede':'WORK100',
#               'number_of_days':21
#               ........

            
#             }
#         ]
#         """

#         """ cari jumlah kehadiran selt.employee-id"""




class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = 'hr.payslip'

    current_year = datetime.now().year
    date_from = fields.Date(string='Date From', readonly=True, required=True,
        default=lambda self: fields.Date.to_string(date.today().replace(day=1)), states={'draft': [('readonly', False)]})
    date_to = fields.Date(string='Date To', readonly=True, required=True,
        default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
        states={'draft': [('readonly', False)]})
    # field to show previous month of the selected date_to
    prev_period = fields.Date('Previous Period', compute="_compute_prev_period")
    # field to show selections of months
    month_selection = fields.Selection([
                        ("01","Januari %s" % current_year),   
                        ("02","Februari %s" % current_year),
                        ("03","Maret %s" % current_year),
                        ("04","April %s" % current_year),
                        ("05","Mei %s" % current_year),
                        ("06","Juni %s" % current_year),
                        ("07","Juli %s" % current_year),
                        ("08","Agustus %s" % current_year),
                        ("09","September %s" % current_year),
                        ("10","Oktober %s" % current_year),
                        ("11","November %s" % current_year),
                        ("12","Desember %s" % current_year),
                        ],string='Month Selection')

    @api.onchange('month_selection')
    def onchange_date_selector(self):
        for rec in self:
            if rec.month_selection:
                month = rec.month_selection
                year = datetime.now().year

                date_from_str = "%s-%s-21" % (year, month)
                date_end_str = "%s-%s-20" % (year, month)

                date_from = datetime.strptime(date_from_str, "%Y-%m-%d") - relativedelta(months=+1)
                date_end = datetime.strptime(date_end_str, "%Y-%m-%d")

                rec.date_from = date_from
                rec.date_to = date_end
            else:
                rec.date_from = False
                rec.date_to = False

    @api.depends('date_to')
    def _compute_prev_period(self):
        if self.date_to:
            mod_dateTo = self.date_to + relativedelta(months=-1)
            self.prev_period = mod_dateTo
        else:
            self.prev_period = False

    @api.model
    def get_worked_day_lines(self,contracts,date_from,date_to):
        res = super(HrPayslip, self).get_worked_day_lines(contracts,date_from,date_to)        
        
        presense = self.get_presense(contracts, date_from, date_to)
        presense_under_5_hour = self.get_presense_late(contracts, date_from, date_to)

        late = self.get_late(date_from,date_to)

        res = [] # set to empty

        res.append({
            'name':'Kehadiran',
            'sequence':10,
            'code':'PRES',
            'number_of_days': presense + presense_under_5_hour,
            'number_of_hours': 0.0,
            'contract_id': self.contract_id.id})

        res.append({
            'name':'Shift 3',
            'sequence':20,
            'code':'PRES_SHIFT3',
            'number_of_days': self.get_shift_3(date_from,date_to),
            'number_of_hours': 0.0,
            'contract_id': self.contract_id.id})

        res.append({
            'name':'Terlambat',
            'sequence':30,
            'code':'TLT',
            'number_of_days': late,
            'number_of_hours': 0.0,
            'contract_id': self.contract_id.id})

        res.append({
            'name':'Izin Sakit',
            'sequence':40,
            'code':'SKT',
            'number_of_days': self.get_duration_time_off('Izin Sakit'),
            'number_of_hours': 0.0,
            'contract_id': self.contract_id.id})

        res.append({
            'name':'Izin Normatif',
            'sequence':50,
            'code':'NOR',
            'number_of_days': self.get_duration_time_off('Izin Normatif'),
            'number_of_hours': 0.0,
            'contract_id': self.contract_id.id})

        res.append({
            'name':'Izin Maternity',
            'sequence':60,
            'code':'MAT',
            'number_of_days': self.get_duration_time_off('Izin Maternitas'),
            'number_of_hours': 0.0,
            'contract_id': self.contract_id.id})

        res.append({
            'name':'Izin Paternity',
            'sequence':70,
            'code':'PAT',
            'number_of_days': self.get_duration_time_off('Izin Paternitas'),
            'number_of_hours': 0.0,
            'contract_id': self.contract_id.id})

        res.append({
            'name':'Izin Dinas',
            'sequence':80,
            'code':'IDL',
            'number_of_days': self.get_duration_time_off('Izin Dinas'),
            'number_of_hours': 0.0,
            'contract_id': self.contract_id.id})
        
        res.append({
            'name':'Cuti Tahunan',
            'sequence':90,
            'code':'CTH',
            'number_of_days': self.get_duration_time_off('Cuti Tahunan (2023)'),
            'number_of_hours': 0.0,
            'contract_id': self.contract_id.id})

        return res

    @api.model
    def get_inputs(self,contracts,date_from,date_to):
        res = super(HrPayslip, self).get_inputs(contracts,date_from,date_to)        
        
        res.append({
            'name':'Bonus Proyek',
            'sequence':10,
            'code':'LEMBUR',
            'amount': 0.0,
            'contract_id': self.contract_id.id})
        
        res.append({
            'name':'Bonus Bulanan',
            'sequence':20,
            'code':'BONUS',
            'amount': 0.0,
            'contract_id': self.contract_id.id})

        res.append({
            'name':'Tunjangan PPh',
            'sequence':30,
            'code':'TPPH',
            'amount': 0.0,
            'contract_id': self.contract_id.id})

        res.append({
            'name':'Tunjangan Kesehatan Non-BPJS',
            'sequence':40,
            'code':'FASKES',
            'amount': 0.0,
            'contract_id': self.contract_id.id})
        
        res.append({
            'name':'Bonus Tahunan',
            'sequence':50,
            'code':'BOTA',
            'amount': 0.0,
            'contract_id': self.contract_id.id})

        res.append({
            'name':'Tunjangan Hari Raya',
            'sequence':60,
            'code':'THR',
            'amount': 0.0,
            'contract_id': self.contract_id.id})

        res.append({
            'name':'Potongan Resmi',
            'sequence':70,
            'code':'POTONG',
            'amount': 0.0,
            'contract_id': self.contract_id.id})

        res.append({
            'name':'Cicilan PPH21',
            'sequence':80,
            'code':'POTPPH',
            'amount': 0.0,
            'contract_id': self.contract_id.id})

        return res

    def get_presense(self, contracts, date_from, date_to):
        
        sql = """
            select count(*)
            from hr_attendance
            where employee_id = %s
            and check_in between %s and %s and worked_hours >= 5
        """
        cr = self.env.cr
        cr.execute(sql, (contracts.employee_id.id, date_from, date_to))
        res = cr.fetchone()
        return res[0]

    def get_presense_late(self, contracts, date_from, date_to):
        
        sql = """
            select count(id)::float / 2 as late
            from hr_attendance
            where employee_id = %s
            and check_in between %s and %s and worked_hours < 5
        """
        cr = self.env.cr
        cr.execute(sql, (contracts.employee_id.id, date_from, date_to))
        res = cr.fetchone()
        return res[0]

    

    def get_late(self, date_from, date_to):

        late_count = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('check_in','>=',date_from),('check_in','<=',date_to)]).mapped("late_counter")
        return sum(late_count)    

        # """ cari jumlah ke tidak hadiran selt.employee-id"""
        # """jumlah hari kerja dikurangi jumlah kehadiran adalah absense"""

    def get_shift_3(self, date_from, date_to):
        shift_3_count = self.env['hr.attendance'].search([('employee_id','=',self.employee_id.id),('shift_3_counter', '>', 0),('check_in','>=',date_from),('check_in','<=',date_to)]).mapped("shift_3_counter")
        return sum(shift_3_count)    

    def get_duration_time_off(self, type):
        leave_type = self.env['hr.leave.type'].search([('name', '=', type)])
        leave = self.env['hr.leave'].search([('employee_id', '=', self.employee_id.id),
                                             ('request_date_from', '>=', self.date_from),
                                             ('request_date_from', '<=', self.date_to),
                                             ('holiday_status_id', '=', leave_type.id),
                                             ('state', '=', 'validate')])
        return sum(leave.mapped('number_of_days'))



class Hr_employee_attendance(models.Model):
    _name = 'hr.employee.attendance'
    _rec_name = "employee_name"

    code                = fields.Char(string='Kode Absen')
    nip                 = fields.Char(string='NIP')
    employee_name       = fields.Char(string='Nama')
    department          = fields.Char(string='Departemen')
    location            = fields.Char(string='Lokasi')
    workdate            = fields.Date(string='Tanggal')
    check_in            = fields.Char(string='Jam Masuk')
    check_out           = fields.Char(string='Jam Keluar')
    notes               = fields.Char(string='Notes')

    def cron_fill_attendance(self):
        DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
        eksekusi = self.env['hr.employee.attendance'].search([('check_in','!=',False),('check_out','!=',False),('notes','=',False)], order='workdate asc')
        for att in eksekusi:
            employee = self.env['hr.employee'].search([('code','=',att.code)], limit=1)
            if employee:
                date = datetime.strptime(att.workdate, "%Y-%m-%d")
                # jika ada data yang kelewat jadul lewat
                if date < datetime.strptime("2017-09-01", "%Y-%m-%d"):
                    att.write({'notes' : 'Data check in terlalu old'})
                    continue

                #tgl checkout untuk checkout beda hari
                modified_date = date + timedelta(days=1)
                check_out_next_day = modified_date.strftime("%Y-%m-%d")

                #tgl untuk normal checkout (hari yg sama)
                normal_check_out = date.strftime("%Y-%m-%d")

                if len(att.check_in) == 4:
                    sign_in_time = '0' + att.check_in + ':00'
                elif len(att.check_in) == 5:
                    sign_in_time = att.check_in + ':00'
                elif len(att.check_in) == 7:
                    sign_in_time = '0' + att.check_in
                else:
                    sign_in_time = att.check_in

                if len(att.check_out) == 4:
                    sign_out_time = '0' + att.check_out + ':00'
                elif len(att.check_out) == 5:
                    sign_out_time = att.check_out + ':00'
                elif len(att.check_out) == 7:
                    sign_out_time = '0' + att.check_out
                else:
                    sign_out_time = att.check_out

                #query untuk cek apabila ada duplikasi data
                # validity_query = self.env.cr
                # validity_query.execute("SELECT employee_id, check_in FROM hr_attendance WHERE employee_id = %s AND check_in::date = %s", (employee.id, att.workdate))
                # result = validity_query.fetchall()
                # if result:
                #     for r in result:
                #         self._cr.execute("DELETE FROM hr_attendance WHERE employee_id = %s AND check_in::date = %s", (r[0], att.workdate))

                some_space = '  '
                check_in_time = att.workdate + some_space + sign_in_time
                check_out_time = att.workdate + some_space + sign_out_time

                # search checkout terakhir atas employee yg sama
                last_check_out = self.env['hr.attendance'].search([('employee_id','=',employee.id)],order='check_out desc',limit=1)
                if last_check_out.check_out >= check_in_time :
                    att.write({'notes' : 'Check in bentrok dengan check out sebelumnya'})
                    continue

                check_in_ = datetime.strptime(check_in_time, "%Y-%m-%d %H:%M:00")
                check_out_ = datetime.strptime(check_out_time, "%Y-%m-%d %H:%M:00")

                if check_out_ < check_in_:
                    co=check_out_next_day
                else:
                    co=normal_check_out
                check_out = co + some_space + sign_out_time

                # # jika data sama /sudah di create di attendance maka skip
                # attendance_exist = self.env['hr.attendance'].search([('employee_id','=',employee.id),('check_in','=',check_in_time),('check_out','=',check_out)])
                # if attendance_exist:
                #     att.write({'notes' : 'Data sudah import diimport sebelumnya'})
                #     continue
                #import pdb;pdb.set_trace()
                date_in = datetime.strptime(check_in_time,DATETIME_FORMAT)
                date_in_7 = date_in + timedelta(hours=-7)
                date_in_bdg = str(date_in_7)

                date_out = datetime.strptime(check_out,DATETIME_FORMAT)
                date_out_7 = date_out + timedelta(hours=-7)
                date_out_bdg = str(date_out_7)

                data = {
                    'employee_id': employee.id,
                    'check_in': date_in_bdg,
                    'check_out': date_out_bdg,
                }       
                

                self.env['hr.attendance'].create(data)
                self._cr.execute("DELETE FROM hr_employee_attendance WHERE id = %d" %(att.id))
                    

    def cron_clear_finger_print_attendance(self):
        """
            Delete semua data di tabel hr_employee_attendance
        """
        return self._cr.execute("DELETE FROM hr_employee_attendance")

Hr_employee_attendance()


class HRAttendance(models.Model):
    _inherit = 'hr.attendance'

    tanggal = fields.Date(string='Tanggal')
    check_in = fields.Datetime(string="Check In", default=fields.Datetime.now, required=True)
    check_out = fields.Datetime(string="Check Out")
    print("check_in: %s " % check_in)
    print("check_out: %s " % check_out)
    

    @api.model
    def create(self, vals):
        if 'check_out' in vals :
            # check overtime
            DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
            if vals['check_out'] :
                # import pdb;pdb.set_trace()
                # check_out = datetime.strptime(str(vals['check_out']), DATETIME_FORMAT)
                check_out = dateutil.parser.parse(str(vals['check_out'])).date()
                sign_in = dateutil.parser.parse(str(vals['check_in'])).date()
                state = 'validate'
                emp_over = self.env['hr.overtime.employee'].search([('employee_id','=',vals['employee_id']),
                                                                    ('overtime_id.tgl_lembur','=',sign_in),
                                                                    ('overtime_id.state','=',state)])
                if emp_over:
                    lembur = 0
                    for eo in emp_over:
                        start_ovt = datetime.strptime(eo.overtime_id.date_from, DATETIME_FORMAT)
                        end_ovt = datetime.strptime(eo.overtime_id.date_to, DATETIME_FORMAT)
                        if check_out > start_ovt and check_out <= end_ovt:
                            selisih = check_out - start_ovt 
                            lembur = (float(selisih.seconds) / 3600)
                        elif check_out > end_ovt :
                            lembur = eo.overtime_id.number_of_hours_temp
                        eo.write({"ovt_hour":round(lembur,2)})
        return super(HRAttendance, self).create(vals)

HRAttendance()

class CheckInOutModels(models.Model):
    _name = 'checkinout'

    name = fields.Char(string='Name', related='employee_id.name')
    employee_id = fields.Many2one('hr.employee', string="Employee",
     compute='compute_employe',
      store=True)
    user_id   = fields.Integer(string='USERID')
    checktime = fields.Datetime(string='checktime')
    checktype = fields.Char(string='CHECKTYPE')
    verifycode = fields.Integer(string='Verifycode')
    sensor_id = fields.Integer(string='SENSORID')
    workcode = fields.Integer(string='WorkCode')
    sn = fields.Char(string='sn')
    userexfmt = fields.Integer(string='UserExtFmt')

    @api.depends('user_id')
    def compute_employe(self):        
        ucanaccess_jars = [
                "/home/tanjung/UCanAccess/ucanaccess-5.0.0.jar",
                "/home/tanjung/UCanAccess/lib/commons-lang3-3.8.1.jar",
                "/home/tanjung/UCanAccess/lib/commons-logging-1.2.jar",
                "/home/tanjung/UCanAccess/lib/hsqldb-2.5.0.jar",
                "/home/tanjung/UCanAccess/lib/jackcess-3.0.1.jar",
                ]
        classpath = ":".join(ucanaccess_jars)
        cnxn = jaydebeapi.connect(
            "net.ucanaccess.jdbc.UcanaccessDriver",
            "jdbc:ucanaccess:///home/tanjung/att2000.mdb",
            ["", ""],
            classpath
            )
        query = """SELECT * FROM USERINFO"""
        df = pd.read_sql_query(query, cnxn)
        user_info = [{row['USERID']:row['Badgenumber'] for index, row in df.iterrows()}]
        # for index, row in df.iterrows():
        #     user_info.append({
        #         row['USERID']:row['Badgenumber'],
        #     })
        model = self.env['hr.employee']
        for rec in self:
            rec.employee_id = model.search([('barcode','=',user_info[0].get(rec.user_id))]).id

        # def action_generate_absensi(self):
        #     print("======================")
        #     sql_query = """DELETE FROM checkinout"""
        #     self._cr.execute(sql_query)
        #     ucanaccess_jars = [
        #         "/home/tanjung/UCanAccess/ucanaccess-5.0.0.jar",
        #         "/home/tanjung/UCanAccess/lib/commons-lang3-3.8.1.jar",
        #         "/home/tanjung/UCanAccess/lib/commons-logging-1.2.jar",
        #         "/home/tanjung/UCanAccess/lib/hsqldb-2.5.0.jar",
        #         "/home/tanjung/UCanAccess/lib/jackcess-3.0.1.jar",
        #     ]
        #     classpath = ":".join(ucanaccess_jars)
        #     cnxn = jaydebeapi.connect(
        #         "net.ucanaccess.jdbc.UcanaccessDriver",
        #         "jdbc:ucanaccess:///home/tanjung/att2000.mdb",
        #         ["", ""],
        #         classpath
        #         )
        #     query = """SELECT * FROM CHECKINOUT"""
        #     df = pd.read_sql_query(query, cnxn)
        #     model = self.env['checkinout']
        #     print(df)
        #     for index, row in df.iterrows():
        #         model.create({
        #             "user_id":row['USERID'],
        #             "userexfmt":row['UserExtFmt'],
        #             "sensor_id":row['SENSORID'],
        #             "checktype":row['CHECKTYPE'],
        #             "workcode":row['WorkCode'],
        #             "checktime":row['CHECKTIME'],
        #             "verifycode":row['VERIFYCODE'],
        #             "sn":row['sn'],
        #         })

    def action_import_employees(self):
        view_id = self.env.ref('wibicon_attendance.wizard_absence_periode_form').id
        action = {
            'name': "Periode",
            'view_mode': 'form',
            'view_id': view_id,
            'res_model': 'wizard.absence.periode',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [],
        }
        return action
        
class Hremployee(models.Model):
    _inherit = 'hr.employee'
    
    hr_employee_absence = fields.One2many('hr.attendance', 'employee_id', string='Employee absent')

# class Hremployee(models.Model):
#     _name = 'hr.employee.absence'

#     employee_id = fields.Many2one('hr.employee', string='Empoyee')
#     tanggal = fields.Date(string='Tanggal')
#     jam_in = fields.Char(string='Jam In')
#     jam_out = fields.Char(string='Jam Out')