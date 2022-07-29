# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.exceptions import Warning
import time
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
import pytz
from pytz import timezone

class CloseStockPeriod(models.Model):
    _name = "close.stock.period"
    _description = "Close Stock Period"

    def get_default_date(self):
        date_time = pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'Asia/Jakarta'))
        return date_time.strftime('%Y-%m-%d')

    def get_real_date(self):
        return pytz.UTC.localize(datetime.now()).astimezone(timezone(self.env.user.tz or 'Asia/Jakarta'))

    @api.depends('date','warehouse_id')
    def _get_name(self):
        for period in self:
            period.name = '%s %s'%(period.warehouse_id.name, period.date)

    name = fields.Char(string='Name', compute='_get_name', store=True)
    date = fields.Date(
        string='Date',
        required=True,
        default=get_default_date)
    state = fields.Selection([
        ('Draft', 'Draft'),
        ('Closed', 'Closed'),
    ], string='State', default='Draft', copy=False)
    warehouse_id = fields.Many2one(
        comodel_name='stock.warehouse',
        string='Warehouse',
        required=True)

    def is_closed(self, date, warehouse_ids):
        if not date :
            raise Warning(_("Date is not define."))
        if type(date) is not str:
            date = date.strftime('%Y-%m-%d')
        date = date[:10]
        if self.search([
            ('date', '=', date),
            ('state', '=', 'Closed'),
            ('warehouse_id','in',warehouse_ids),
        ], limit=1):
            return True
        return False

    def action_close(self):
        for period in self:
            if period.state != 'Draft':
                continue
            same_period = self.search([
                ('date', '=', period.date),
                ('warehouse_id', '=', period.warehouse_id.id),
                ('state', '=', 'Closed')])
            if same_period:
                raise Warning("This period was closed.")

            period.write({'state': 'Closed'})

    def action_draft(self):
        for period in self:
            if period.state != 'Closed':
                continue
            period.write({'state': 'Draft'})

    def auto_close_stock_period(self):
        three_days_ago = self.get_real_date() - timedelta(days=3)
        three_days_ago = three_days_ago.strftime('%Y-%m-%d')
        print("\n three_days_ago",three_days_ago)
        for warehouse in self.env['stock.warehouse'].search([]):
            try :
                exist_period = self.search([
                    ('date', '=', three_days_ago),
                    ('warehouse_id', '=', warehouse.id),
                    ('state', '=', 'Closed')])
                if exist_period :
                    continue
                period_id = self.create({
                    'date': three_days_ago,
                    'warehouse_id': warehouse.id
                })
                period_id.action_close()
                self._cr.commit()
            except Exception as e :
                print("\n error close period: %s"%(e))
                continue
