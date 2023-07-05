from odoo import models, fields, api, _
from odoo.exceptions import UserError

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model
    def get_data_kanban_production(self):
        print('get_data_kanban_production')
        workcenter = """select id from mrp_workcenter where active = true;"""
        self._cr.execute(workcenter)
        result_workcenter = self._cr.fetchall()

        mo = """select name, option_vip, process_terkini from mrp_production where option_vip = 'HIGH RISK';"""
        self._cr.execute(mo)
        result_mo = self._cr.dictfetchall()
        list_option = []
        dict_mo = {}

        for rm in result_mo:
            name = rm.get('name')
            option_vip = rm.get('option_vip')
            process_now = rm.get('option_terkini')
            if option_vip not in list_option:
                list_option.append(option_vip)
            key = '%s-%s' % (option_vip, process_now)
            dict_mo[key] = name
        record = [{'option_vip': o} for o in list_option]
        for rec in record:
            rec.update({str(key[0]): dict_mo[rec.get('option_vip')+'-'+str(key[0])] for key in result_workcenter})
            

        # print('list_option', record)