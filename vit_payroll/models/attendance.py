# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2017  Odoo SA  (http://www.vitraining.com)
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from odoo import api, fields, models, _, SUPERUSER_ID


class HRAttendance(models.Model):
    _inherit = "hr.attendance"

    def real_working_hours_on_day(self, employee_id, datetime_day):
        day = datetime_day.strftime("%Y-%m-%d 00:00:00")
        day2 = datetime_day.strftime("%Y-%m-%d 24:00:00")

        #employee attendance
        att_id = self.search([('employee_id', '=', employee_id), ('check_in', '>', day), ('check_out', '<', day2)], limit=1, order='check_in asc' )
        
        time1=0
        time2=0
        if att_id :
            time1 = datetime.strptime(att_id.check_in,"%Y-%m-%d %H:%M:%S")
            if att_id.check_out :
                time2 = datetime.strptime(att_id.check_out,"%Y-%m-%d %H:%M:%S")
        
        if time2 and time1:
	        delta = (time2 - time1).seconds / 3600.00
        else:
            delta = 0
       
        return delta

HRAttendance()