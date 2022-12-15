from odoo import models, fields, api, _
from odoo.exceptions import UserError
import pandas_access as mdb
import jaydebeapi
import pandas as pd

class WizardExportAbsence(models.Model):
    _name = 'wizard.export.absent'

    date_start = fields.Date(string='Date Start', default=fields.Date.today(), required=True, )
    date_end = fields.Date(string='Date Ends', default=fields.Date.today(), required=True, )

    def action_export_data(self):
        print("======================")
        ucanaccess_jars = [
            "/home/yugi/UCanAccess/ucanaccess-5.0.0.jar",
            "/home/yugi/UCanAccess/lib/commons-lang3-3.8.1.jar",
            "/home/yugi/UCanAccess/lib/commons-logging-1.2.jar",
            "/home/yugi/UCanAccess/lib/hsqldb-2.5.0.jar",
            "/home/yugi/UCanAccess/lib/jackcess-3.0.1.jar",
        ]
        classpath = ":".join(ucanaccess_jars)
        cnxn = jaydebeapi.connect(
            "net.ucanaccess.jdbc.UcanaccessDriver",
            "jdbc:ucanaccess:///home/yugi/garment_mdb/att2000.mdb",
            ["", ""],
            classpath
            )
        query_delete = """ 
                DELETE FROM hr_attendance where to_char(tanggal, 'YYYY-MM-DD') BETWEEN '%s' AND '%s';
                DELETE FROM checkinout where to_char(checktime, 'YYYY-MM-DD') BETWEEN '%s' AND '%s'; 
                """ % (self.date_start, self.date_end, self.date_start, self.date_end)
        self._cr.execute(query_delete)
        query = """SELECT * FROM CHECKINOUT WHERE to_char(checktime, 'YYYY-MM-DD') BETWEEN '%s' AND '%s' """ % (self.date_start, self.date_end)
        df = pd.read_sql_query(query, cnxn)
        model = self.env['checkinout']
        for index, row in df.iterrows():
            model.create({
                "user_id":row['USERID'],
                "userexfmt":row['UserExtFmt'],
                "sensor_id":row['SENSORID'],
                "checktype":row['CHECKTYPE'],
                "workcode":row['WorkCode'],
                "checktime":row['CHECKTIME'],
                "verifycode":row['VERIFYCODE'],
                "sn":row['sn'],
            })
