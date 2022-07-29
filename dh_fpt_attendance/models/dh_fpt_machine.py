import pytz
import datetime
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_datetime
from .zk import ZK, const, finger


class DhFptMachine(models.Model):
    _name = 'dh.fpt.machine'

    name = fields.Char(string='Machine IP', required=True)
    port_no = fields.Integer(string='Port No', required=True, default=4370)
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)
    device_info = fields.Text(string='Device Information')
    device_auto_delete_log = fields.Boolean(string='Device Auto Delete Log', default=False)
    device_last_sync = fields.Datetime(string='Device Last Sync')
    device_checkin = fields.Integer(string='Checkin Code', required=True, default=0)
    device_checkout = fields.Integer(string='Checkout Code', required=True, default=0)

    def machine_test_connection(self):
        for info in self:
            try:
                machine_ip = info.name
                port_no = info.port_no
                timeout = 30
                zk = ZK(machine_ip, port=port_no, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
                zk.connect()
                if zk.is_connect:
                    info.machine_device_info(zk)
                    view = info.env.ref('dh_popup_message.dh_popup_message_wizard')
                    context = dict(info._context or {})
                    context['message'] = "Berhasil terkoneksi mesin fingerprint.\nLast Sync " + str(
                        format_datetime(self.env, info.device_last_sync, dt_format=False)) + "\n\n" + info.device_info
                    return {
                        'name': 'Success',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'dh.popup.message.wizard',
                        'view_id': view.id,
                        'target': 'new',
                        'context': context,
                    }
            except Exception as err:
                raise ValidationError(
                    'Mesin Finger gagal / belum terkoneksi!!!\nKarena %s'%(err))

    def machine_sync_datetime(self):
        for info in self:
            # try:
            machine_ip = info.name
            port_no = info.port_no
            timeout = 30
            zk = ZK(machine_ip, port=port_no, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
            zk.connect()
            if zk.is_connect:
                # user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
                # date_today = pytz.utc.localize(datetime.datetime.now()).astimezone(user_tz)
                zk.set_time(datetime.datetime.now(pytz.timezone('Asia/Jakarta')))
                info.machine_device_info(zk)
                view = info.env.ref('dh_popup_message.dh_popup_message_wizard')
                context = dict(info._context or {})
                context['message'] = "Berhasil sync datetime mesin fingerprint.\nLast Sync " + str(
                    format_datetime(self.env, info.device_last_sync, dt_format=False))
                return {
                    'name': 'Success',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'dh.popup.message.wizard',
                    'view_id': view.id,
                    'target': 'new',
                    'context': context,
                }
            # except:
            #     raise ValidationError(
            #         'Mesin Finger gagal / belum terkoneksi!!!')

    def machine_device_info(self, zk):
        for info in self:
            zk.enable_device()
            device_info = ''
            device_info += 'Device Name : ' + str(zk.get_device_name()) + '\n'
            device_info += 'MAC Address : ' + str(zk.get_mac()) + '\n'
            device_info += 'Platform : ' + str(zk.get_platform()) + '\n'
            device_info += 'Serial Number : ' + str(zk.get_serialnumber()) + '\n'
            device_info += 'FingerPrint Version : ' + str(zk.get_fp_version()) + '\n'
            device_info += 'Frimware Version : ' + str(zk.get_firmware_version()) + '\n'
            info.device_info = device_info
            info.device_last_sync = datetime.datetime.now()
            zk.disconnect()

    @api.model
    def cron_machine_download(self):
        machines = self.env['dh.fpt.machine'].search([])
        for machine in machines:
            print("run machine_cron_download_log")
            machine.machine_download_log(msgDialog=False)

    def machine_clear_data_all(self):
        for info in self:
            try:
                machine_ip = info.name
                port_no = info.port_no
                timeout = 30
                zk = ZK(machine_ip, port=port_no, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
                zk.connect()
                if zk.is_connect:
                    zk.disable_device()
                    zk.clear_data()
                    info.machine_device_info(zk)

                view = self.env.ref('dh_popup_message.dh_popup_message_wizard')
                context = dict(self._context or {})
                context['message'] = "Berhasil hapus semua data mesin fingerprint."
                return {
                    'name': 'Success',
                    'type': 'ir.actions.act_window',
                    'view_mode': 'form',
                    'res_model': 'dh.popup.message.wizard',
                    'view_id': view.id,
                    'target': 'new',
                    'context': context,
                }
            except Exception as err:
                raise ValidationError(
                    'Mesin Finger gagal / belum terkoneksi!!!\nKarena %s'%(err))

    def machine_clear_data_log(self):
        for info in self:
            try:
                machine_ip = info.name
                port_no = info.port_no
                timeout = 30
                zk = ZK(machine_ip, port=port_no, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
                zk.connect()
                if zk.is_connect:
                    zk.disable_device()
                    zk.clear_attendance()
                    info.machine_device_info(zk)
                    view = info.env.ref('dh_popup_message.dh_popup_message_wizard')
                    context = dict(info._context or {})
                    context['message'] = "Berhasil hapus data log mesin fingerprint."
                    return {
                        'name': 'Success',
                        'type': 'ir.actions.act_window',
                        'view_mode': 'form',
                        'res_model': 'dh.popup.message.wizard',
                        'view_id': view.id,
                        'target': 'new',
                        'context': context,
                    }
            except:
                raise ValidationError(
                    'Mesin Finger gagal / belum terkoneksi!!!')

    def machine_upload_users(self):
        employee = self.env['hr.employee']
        for info in self:
            # try:
            machine_ip = info.name
            port_no = info.port_no
            timeout = 30
            zk = ZK(machine_ip, port=port_no, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
            zk.connect()
            if zk.is_connect:
                zk.disable_device()
                data = employee.search([('fpt_machine_ids', 'like', info.id)])
                for emp in data:
                    uid = emp.id
                    if emp.fpt_uid != 0:
                        uid = emp.fpt_uid
                    user_id = emp.id
                    if emp.fpt_user_id != '' or emp.fpt_user_id:
                        user_id = emp.fpt_user_id
                    zk.set_user(uid=int(uid), name=str(emp.name), user_id=str(user_id))
                    emp.fpt_uid = uid
                    emp.fpt_user_id = user_id
                    if emp.fpt_finger_line:
                        fingers = []
                        for f in emp.fpt_finger_line:
                            json = {
                                'uid': f.fpt_uid,
                                'fid': f.fpt_fid,
                                'valid': f.fpt_valid,
                                'template': f.fpt_template
                            }
                            templates = finger.Finger.json_unpack(json)
                            fingers.append(templates)
                        if fingers:
                            zk.save_user_template(user=emp.fpt_uid, fingers=fingers)
                info.machine_device_info(zk)
            view = self.env.ref('dh_popup_message.dh_popup_message_wizard')
            context = dict(self._context or {})
            context['message'] = "Berhasil upload data users mesin fingerprint."
            return {
                'name': 'Success',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'dh.popup.message.wizard',
                'view_id': view.id,
                'target': 'new',
                'context': context,
            }
            # except:
            #     raise ValidationError(
            #         'Mesin Finger gagal / belum terkoneksi!!!')

    def machine_download_users(self):
        employee = self.env['hr.employee']
        finger_line = self.env['dh.fpt.machine.finger']
        for info in self:
            # try:
            machine_ip = info.name
            port_no = info.port_no
            timeout = 30
            zk = ZK(machine_ip, port=port_no, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
            zk.connect()
            if zk.is_connect:
                zk.disable_device()
                data = zk.get_users()
                tpl = zk.get_templates()
                for user in data:
                    check_employee = employee.search([('fpt_user_id', '=', user.user_id)])
                    password = 0
                    if user.password != '':
                        password = int(user.password)
                    if check_employee:
                        check_employee.write({'fpt_uid': int(user.uid),
                                              'fpt_user_id': user.user_id,
                                              'fpt_password': password,
                                              'fpt_card': int(user.card),
                                              'fpt_privilege': int(user.privilege),
                                              'fpt_machine_ids': [(4, info.id)]})
                    else:
                        employee.create({'fpt_uid': int(user.uid),
                                         'name': user.name,
                                         'fpt_user_id': user.user_id,
                                         'fpt_password': password,
                                         'fpt_card': int(user.card),
                                         'fpt_privilege': int(user.privilege),
                                         'fpt_machine_ids': [(4, info.id)]})
                    for user_tpl in tpl:
                        if user_tpl.uid == user.uid:
                            emp = employee.search([('fpt_uid', '=', user.uid)])
                            check_finger_line = finger_line.search(
                                [('fpt_uid', '=', user_tpl.uid), ('fpt_fid', '=', user_tpl.fid)])
                            if check_finger_line:
                                check_finger_line.write({'employee_id': emp.id,
                                                         'fpt_uid': int(user_tpl.uid),
                                                         'fpt_fid': int(user_tpl.fid),
                                                         'fpt_valid': int(user_tpl.valid),
                                                         'fpt_size': int(user_tpl.size),
                                                         'fpt_template': user_tpl.json_pack().get('template')})
                            else:
                                finger_line.create({'employee_id': emp.id,
                                                    'fpt_uid': int(user_tpl.uid),
                                                    'fpt_fid': int(user_tpl.fid),
                                                    'fpt_valid': int(user_tpl.valid),
                                                    'fpt_size': int(user_tpl.size),
                                                    'fpt_template': user_tpl.json_pack().get('template')})
                info.machine_device_info(zk)
        view = self.env.ref('dh_popup_message.dh_popup_message_wizard')
        context = dict(self._context or {})
        context['message'] = "Berhasil download data users mesin fingerprint."
        return {
            'name': 'Success',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'dh.popup.message.wizard',
            'view_id': view.id,
            'target': 'new',
            'context': context,
        }
        # except:
        #     raise ValidationError(
        #         'Mesin Finger gagal / belum terkoneksi!!!')

    def machine_download_log(self, msgDialog=True):
        fpt_machine_log = self.env['dh.fpt.machine.log']
        for info in self:
            machine_ip = info.name
            port_no = info.port_no
            timeout = 30
            zk = ZK(machine_ip, port=port_no, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
            zk.connect()
            if zk.is_connect:
                zk.disable_device()
                attendance = zk.get_attendance()
                users = zk.get_users()
                for user in users:
                    employee = self.env['hr.employee'].search([('fpt_user_id', '=', user.user_id)])
                    if employee:
                        continue
                    else:
                        employee.create({'fpt_uid': int(user.uid),
                                         'name': str(user.name),
                                         'fpt_user_id': str(user.user_id),
                                         'fpt_card': int(user.card),
                                         'fpt_machine_ids': [(4, info.id)]})
                for att in attendance:
                    att_timestamp = att.timestamp
                    att_timestamp = datetime.datetime.strptime(att_timestamp.strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
                    local_tz = pytz.timezone(
                        self.env.user.partner_id.tz or 'GMT')
                    local_dt = local_tz.localize(att_timestamp, is_dst=None)
                    utc_dt = local_dt.astimezone(pytz.utc)
                    utc_dt = utc_dt.strftime("%Y-%m-%d %H:%M:%S")
                    att_timestamp = datetime.datetime.strptime(
                        utc_dt, "%Y-%m-%d %H:%M:%S")
                    att_timestamp = fields.Datetime.to_string(att_timestamp)
                    employee = self.env['hr.employee'].search([('fpt_user_id', '=', att.user_id)])
                    log = fpt_machine_log.search([('fpt_user_id', '=', att.user_id), ('fpt_punch', '=', att.punch),
                                                  ('fpt_timestamp', '=', att_timestamp)])
                    if log:
                        continue
                    else:
                        fpt_machine_log.create({'employee_id': employee.id,
                                                'name': info.name,
                                                'address_id': info.address_id.id,
                                                'fpt_machine_id': info.id,
                                                'fpt_uid': att.uid,
                                                'fpt_user_id': att.user_id,
                                                'fpt_punch': att.punch,
                                                'fpt_status': att.status,
                                                'fpt_timestamp': att_timestamp})
                if (info.device_auto_delete_log == True):
                    zk.clear_attendance()
                info.machine_device_info(zk)
        if msgDialog:
            view = self.env.ref('dh_popup_message.dh_popup_message_wizard')
            context = dict(self._context or {})
            context['message'] = "Berhasil download data log mesin fingerprint."
            return {
                'name': 'Success',
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'dh.popup.message.wizard',
                'view_id': view.id,
                'target': 'new',
                'context': context,
            }
