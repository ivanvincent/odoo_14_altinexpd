from odoo import models, fields, api
from ast import literal_eval

from random import randint
class UudpCategory(models.Model):
    _name = 'uudp.category'

    name                     = fields.Char(string='UUDP Category',required=True, )
    description              = fields.Text(string='Description')
    allowed_position_ids     = fields.Many2many(comodel_name='hr.job', relation='allowed_position_hr_job_rel',string='Allowed Positions')
    allowed_expense_ids      = fields.Many2many(comodel_name='product.template', relation='allowed_expenses',string='Allowed Expenses',domain=[('can_be_expensed','=',1)])
    is_active                = fields.Boolean(string='Active ?',default=True)
    is_limit                 = fields.Boolean(string='Limit ?',default=True)
    is_urgent                = fields.Boolean(string='Urgent ?',default=False)
    is_purchase              = fields.Boolean(string='Purchase ?',default=False)
    is_rute_sale             = fields.Boolean(string='For Rute Sale ?',default=False)
    filter_pengaju           = fields.Boolean(string='Filter Pengaju ?',default=False)
    belum_selesai            = fields.Integer(string='Belum Selesai',compute="get_kasbon")
    belum_pencairan          = fields.Integer(string='Belum Pencairan',compute="get_kasbon")
    
    
    def get_kasbon(self):
        for line in self:
            kasbon_ids    = self.env['uudp'].search([('type','=','pengajuan'),('selesai','!=',True),('category_id','=',line.id)])
            pencairan_ids = self.env['uudp'].search([('type','=','pengajuan'),('selesai','!=',True),('category_id','=',line.id),'|',('pencairan_id.state','!=','done'),('pencairan_id','=',False)])
            line.belum_selesai = len(kasbon_ids)
            line.belum_pencairan = len(pencairan_ids)
    
    def _get_action(self, action_xmlid):
        action = self.env["ir.actions.actions"]._for_xml_id(action_xmlid)
        if self:
            action['display_name'] = self.display_name
        context = {
            'default_search_category_id': self.id,
            'default_search_type':'pengajuan'
        }

        import logging;
        action_context = literal_eval(action['context'])
        context = {**action_context, **context}
        action['context'] = context
        if action['xml_id'] == 'vit_uudp.action_uudp_pengajuan_list_belum_selesai':
            action['domain'] = [('category_id', '=', self.id),('type','=','pengajuan'),('selesai','!=',True)]
        elif action['xml_id'] == 'vit_uudp.action_uudp_pengajuan_list_belum_pencairan':
            action['domain'] = [('category_id', '=', self.id),('type','=','pengajuan'),'|',('pencairan_id.state','!=','done'),('pencairan_id','=',False)]
        else:
            action['domain'] = [('category_id', '=', self.id),('type','=','pengajuan')]
        _logger = logging.getLogger(__name__)
        _logger.warning('='*40)
        _logger.warning('MESSAGE')
        _logger.warning(action['domain'])
        _logger.warning('='*40)
        return action

    
    def action_open_uudp_category(self):
        return self._get_action('vit_uudp.action_uudp_pengajuan_list')
    
    def action_belum_selesai(self):
        return self._get_action('vit_uudp.action_uudp_pengajuan_list_belum_selesai')
    
    def action_belum_pencairan(self):
        return self._get_action('vit_uudp.action_uudp_pengajuan_list_belum_pencairan')