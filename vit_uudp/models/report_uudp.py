from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)



class ReportKason(models.Model):
    _name        = 'report.kasbon'
    _description = 'Laporan Kasbon'


    name         = fields.Char(string='Title')
    date_start   = fields.Date(string='Start Date', default=fields.Date.today())
    date_end     = fields.Date(string='End Date', default=fields.Date.today())
    company_id   = fields.Many2one('res.company', default=lambda self: self.env.company)
    user_id      = fields.Many2one('res.users', string='Responsible', default=lambda self: self.env.user.id)
    currency_id  = fields.Many2one('res.currency', related='company_id.currency_id', store=True,)
    category_ids = fields.Many2many(comodel_name='uudp.category', relation='report_kasbon_catetogory_rel', string='Category')
    line_ids     = fields.One2many('report.kasbon.line', 'report_id', string='Report detail')



    def action_clear(self):
        query = """
                DELETE FROM report_kasbon_line WHERE report_id = %s;
                DELETE FROM report_kasbon_line_history_pengajuan WHERE report_id = %s;
                DELETE FROM report_kasbon_line_history_pencairan WHERE report_id = %s;
                DELETE FROM report_kasbon_line_history_penyelesaian WHERE report_id = %s;
                DELETE FROM report_kasbon_line_history_reimburse WHERE report_id = %s;
                """%(self.id,self.id,self.id,self.id,self.id)
        self._cr.execute(query)


    def action_calculate(self):
        self.action_clear()
        'DO STUFF'
        filter_category = "a.category_id in {}".format(tuple(self.category_ids.ids)) if len(self.category_ids) > 1 else "a.category_id = {}".format(self.category_ids.id)  if self.category_ids else '1=1'
        query = """ 
                WITH report_line AS (
                    INSERT INTO report_kasbon_line (report_id,employee_id,nominal_kasbon,nominal_pencairan,nominal_penyelesaian,nominal_reimburse)(
                        SELECT 
                            %s,
                            employee_id ,
                            SUM(nominal_kasbon) as nominal_kasbon,
                            SUM(nominal_pencairan) as nominal_pencairan,
                            SUM(nominal_penyelesaian) as nominal_penyelesaian,
                            SUM(nominal_reimburse) as nominal_reimburse
                        FROM (
                                SELECT 
                                    ROW_NUMBER() over() as id,
                                    a.employee_id as employee_id,
                                    b.sub_total as nominal_kasbon,
                                    0 as nominal_pencairan,
                                    0 as nominal_penyelesaian,
                                    0 as nominal_reimburse
                                FROM
                                uudp a , uudp_detail b 
                                WHERE 
                                    b.uudp_id = a.id AND 
                                    a.type = 'pengajuan' AND 
                                    a.state in ('confirm_finance','confirm_accounting','done') AND
                                    %s AND
                                    a.date BETWEEN '%s' AND '%s'
                                UNION
                                SELECT 
                                    ROW_NUMBER() over() as id,
                                    a.employee_id as employee_id,
                                    0 as nominal_kasbon,
                                    credit as nominal_pencairan,
                                    0 as nominal_penyelesaian,
                                    0 as nominal_reimburse
                                FROM
                                uudp a , uudp_pencairan b , account_bank_statement_line c
                                WHERE 
                                    b.ajuan_id = a.id AND 
                                    a.pencairan_id = b.id AND
                                    c.pencairan_id = b.id AND
                                    %s AND
                                    a.date BETWEEN '%s' AND '%s'
                                UNION
                                SELECT
                                    ROW_NUMBER() over() as id,
                                    a.employee_id as employee_id,
                                    0 as nominal_kasbon,
                                    0 as nominal_pencairan,
                                    b.sub_total as nominal_penyelesaian,
                                    0 as nominal_reimburse
                                FROM
                                    uudp a , uudp_detail b , uudp c
                                WHERE 
                                    b.uudp_id = a.id AND 
                                    a.ajuan_id = c.id AND
                                    a.type = 'penyelesaian' AND 
                                    %s AND
                                    c.date BETWEEN '%s' AND '%s'
                                UNION
                                SELECT
                                    ROW_NUMBER() over() as id,
                                    a.employee_id as employee_id,
                                    0 as nominal_kasbon,
                                    0 as nominal_pencairan,
                                    0 as nominal_penyelesaian,
                                    b.sub_total as nominal_reimburse
                                FROM
                                    uudp a , uudp_detail b ,uudp c , uudp d
                                WHERE 
                                    b.uudp_id = a.id AND 
                                    c.type = 'pengajuan' AND
                                    d.type = 'penyelesaian' AND
                                    d.ajuan_id = c.id AND
                                    a.id = d.reimburse_id AND
                                    a.type = 'reimberse' AND 
                                    a.state in ('confirm_finance','confirm_accounting','done') AND
                                    c.date BETWEEN '%s' AND '%s'
                        ) as report

                        GROUP BY employee_id
                
                    ) returning *
                ),
                
                history_kasbon AS (
                    INSERT INTO report_kasbon_line_history_pengajuan(report_id,report_line_id,ajuan_id)(
                        SELECT 
                                c.report_id,
                                c.id,
                                a.id
                            FROM
                            uudp a ,report_line c
                            WHERE 
                                a.type = 'pengajuan' AND 
                                c.employee_id = a.employee_id AND
                                a.state in ('confirm_finance','confirm_accounting','done') AND
                                %s AND
                                a.date BETWEEN '%s' AND '%s'
                    )
                    
                ),
                history_pencairan AS (
                    INSERT INTO report_kasbon_line_history_pencairan(report_id,report_line_id,pencairan_id)(
                        SELECT 
                            c.report_id,
                            c.id,
                            b.id
                        FROM
                        uudp a , uudp_pencairan b , report_line c
                        WHERE 
                            b.ajuan_id = a.id AND 
                            a.pencairan_id = b.id AND
                            c.employee_id = a.employee_id AND
                            %s AND
                            a.date BETWEEN '%s' AND '%s'
                    )
                    
                ),
                history_penyelesaian AS (
                    INSERT INTO report_kasbon_line_history_penyelesaian(report_id,report_line_id,penyelesaian_id)(
                        SELECT
                            c.report_id,
                            c.id,
                            a.id
                        FROM
                            uudp a , uudp b, report_line c
                        WHERE 
                            a.type = 'penyelesaian' AND 
                            a.ajuan_id = b.id AND
                            a.state in ('confirm_finance','confirm_accounting','done') AND
                            c.employee_id = a.employee_id AND
                            %s AND
                            b.date BETWEEN '%s' AND '%s'
                    )
                    
                ),
                history_reimburse AS (
                    INSERT INTO report_kasbon_line_history_reimburse(report_id,report_line_id,reimburse_id)(
                        SELECT
                            b.report_id,
                            b.id,
                            a.id
                        FROM
                            uudp a , report_line b ,uudp c , uudp d
                        WHERE 
                            a.type = 'reimberse' AND 
                            b.employee_id = a.employee_id AND
                            c.employee_id = a.employee_id AND
                            d.employee_id = a.employee_id AND
                            c.type = 'pengajuan' AND
                            d.type = 'penyelesaian' AND
                            d.ajuan_id = c.id AND
                            a.id = d.reimburse_id AND
                            a.state in ('confirm_finance','confirm_accounting','done') AND
                            c.date BETWEEN '%s' AND '%s'
                    )
                    
                )
                SELECT * FROM report_line limit 1;
        """%( self.id,
             
            filter_category,
            self.date_start,self.date_end,
            filter_category,
            self.date_start,self.date_end,
            filter_category,
            self.date_start,self.date_end,
            self.date_start,self.date_end,
            #HISTORY
            filter_category,
            self.date_start,self.date_end,
            filter_category,
            self.date_start,self.date_end,
            filter_category,
            self.date_start,self.date_end,
            self.date_start,self.date_end,
            )
        self._cr.execute(query)


class ReportKasonLine(models.Model):
    _name        = 'report.kasbon.line'
    _description = 'Laporan Kasbon Detail'
    _order       = 'employee_id'



    name                     = fields.Char(string='Laporan Kasbon Line')
    report_id                = fields.Many2one('report.kasbon', string='Laporan Kasbon')
    currency_id              = fields.Many2one('res.currency', related='report_id.currency_id', store=True,)
    employee_id              = fields.Many2one('hr.employee', string='Karyawan')
    nominal_kasbon           = fields.Float(string='Kasbon')
    nominal_pencairan        = fields.Float(string='Pencairan')
    nominal_penyelesaian     = fields.Float(string='Realisasi')
    nominal_reimburse        = fields.Float(string='Reimburse')
    nominal_dibebankan       = fields.Float(string='Dibebankan')
    history_ajuan_ids        = fields.One2many('report.kasbon.line.history.pengajuan', 'report_line_id', 'History Pengajuan')
    history_pencairan_ids    = fields.One2many('report.kasbon.line.history.pencairan', 'report_line_id', 'History Pencairan')
    history_penyelesaian_ids = fields.One2many('report.kasbon.line.history.penyelesaian', 'report_line_id', 'History Penyelesaian')
    history_reimburse_ids    = fields.One2many('report.kasbon.line.history.reimburse', 'report_line_id', 'History Reimburse')
   
    
    

class ReportKasonLineHistoryPengajuan(models.Model):
    _name        = 'report.kasbon.line.history.pengajuan'
    _description = 'Laporan Kasbon History Pengajuan'



    ajuan_id         = fields.Many2one('uudp', string='Kasbon')
    report_id        = fields.Many2one('report.kasbon', string='Laporan Kasbon')
    report_line_id   = fields.Many2one('report.kasbon.line', string='Detail Kasbon')
    tanggal          = fields.Datetime(related='ajuan_id.date', string='Tanggal')
    end_date         = fields.Datetime(related='ajuan_id.end_date', string='Batas Realisasi')
    tgl_penyelesaian = fields.Datetime(related='ajuan_id.end_date', string='Tanggal Realisasi')
    total_ajuan      = fields.Float(related='ajuan_id.total_ajuan', string='Nominal')
    employee_id      = fields.Many2one(related='ajuan_id.employee_id', string='Yang Mengajukan')
    user_id          = fields.Many2one(related='ajuan_id.user_id', string='Admin')
    kasir_id         = fields.Many2one(related='ajuan_id.kasir_id', string='Kasir')
    state            = fields.Selection(related='ajuan_id.state', string='Status')
    
    
    

class ReportKasonLineHistoryPencairan(models.Model):
    _name        = 'report.kasbon.line.history.pencairan'
    _description = 'Laporan Kasbon History Pencairan'



    report_id          = fields.Many2one('report.kasbon', string='Laporan Kasbon')
    pencairan_id       = fields.Many2one('uudp.pencairan', string='Pencairan')
    report_line_id     = fields.Many2one('report.kasbon.line', string='Detail Kasbon')
    user_id            = fields.Many2one(related='pencairan_id.user_id', string='Kasir')
    ajuan_id           = fields.Many2one(related='pencairan_id.ajuan_id', string='Pengajuan')
    journal_id         = fields.Many2one(related='pencairan_id.journal_id', string='Journal')
    tgl_pencairan      = fields.Date(related='pencairan_id.tgl_pencairan', string='Tanggal')
    bank_statement_id  = fields.Many2one(related='pencairan_id.bank_statement_id', string='Bank Statement')
    state              = fields.Selection(related='pencairan_id.state', string='Status')
    total_pencairan    = fields.Float(related='pencairan_id.total_pencairan', string='Nominal Pencairan')
    
    
    
    

class ReportKasonLineHistoryPenyelesaian(models.Model):
    _name        = 'report.kasbon.line.history.penyelesaian'
    _description = 'Laporan Kasbon History Penyelesaian'


    report_id        = fields.Many2one('report.kasbon', string='Laporan Kasbon')
    report_line_id   = fields.Many2one('report.kasbon.line', string='Detail Kasbon')
    penyelesaian_id  = fields.Many2one('uudp', string='Penyelesaian')
    ajuan_id         = fields.Many2one(related='penyelesaian_id.ajuan_id', string='Kasbon')
    reimburse_id     = fields.Many2one(related='penyelesaian_id.reimburse_id', string='Reimburse')
    tanggal          = fields.Datetime(related='penyelesaian_id.date', string='Tanggal')
    end_date         = fields.Datetime(related='penyelesaian_id.end_date', string='Batas Realisasi')
    tgl_penyelesaian = fields.Datetime(related='penyelesaian_id.end_date', string='Tanggal Realisasi')
    total_penyelesaian = fields.Float(related='penyelesaian_id.total_penyelesaian', string='Nominal Pencairan')
    total_ajuan      = fields.Float(related='penyelesaian_id.total_ajuan', string='Nominal')
    employee_id      = fields.Many2one(related='penyelesaian_id.employee_id', string='Yang Mengajukan')
    user_id          = fields.Many2one(related='penyelesaian_id.user_id', string='Admin')
    kasir_id         = fields.Many2one(related='penyelesaian_id.kasir_id', string='Kasir')
    state            = fields.Selection(related='penyelesaian_id.state', string='Status')
    
    
    
    
class ReportKasonLineHistoryReimburse(models.Model):
    _name        = 'report.kasbon.line.history.reimburse'
    _description = 'Laporan Kasbon History Reimburse'


    report_id       = fields.Many2one('report.kasbon', string='Laporan Kasbon')
    report_line_id  = fields.Many2one('report.kasbon.line', string='Detail Kasbon')
    reimburse_id    = fields.Many2one('uudp', string='Reimburse')
    tanggal          = fields.Datetime(related='reimburse_id.date', string='Tanggal')
    end_date         = fields.Datetime(related='reimburse_id.end_date', string='Batas Realisasi')
    tgl_penyelesaian = fields.Datetime(related='reimburse_id.end_date', string='Tanggal Realisasi')
    total_ajuan      = fields.Float(related='reimburse_id.total_ajuan', string='Nominal')
    employee_id      = fields.Many2one(related='reimburse_id.employee_id', string='Yang Mengajukan')
    user_id          = fields.Many2one(related='reimburse_id.user_id', string='Admin')
    kasir_id         = fields.Many2one(related='reimburse_id.kasir_id', string='Kasir')
    state            = fields.Selection(related='reimburse_id.state', string='Status')
    
    
    
    
    
    
    
