from odoo import models, fields, api

class Conclusion(models.Model):
    _name = 'conclusion'
    # _rec_name = 'desc'

    name = fields.Char(string='Conclusion')    
    desc = fields.Char(string='Nama Spefisikasi')
    urutan = fields.Integer(string='Urutan', default=0)
    active = fields.Boolean(string='Active ?', default=True)


class QrfTemplateConc(models.Model):
    _name = 'qrf.template.con'
    # _rec_name = 'desc'

    name = fields.Char(string='master')    
    new_product = fields.Selection(
        [("yes", "Yes"), ("no", "No")], string='New Product', default='yes')
    comp_partial = fields.Selection(
        [("complete", "Complete"), ("partial", "Partial")], string='Complete/Partial', default='complete')
    turret = fields.Selection(
        [("yes", "Yes"), ("no", "No")], string='Reference Turret <= 5 years?', default='yes')
    tooling = fields.Selection(
        [("eu_tsm", "EU / TSM"), ("other", "Other")], string='Tooling Type', default='eu_tsm')
    tooling_qc = fields.Selection(
        [("altinex", "Altinex"), ("other", "Other")], string='Current Tools producing qc-pass tablets', default='altinex')
    con_id = fields.Many2one('conclusion', string='Conclusion',)
    urutan = fields.Integer(string='Urutan', default=0)
    active = fields.Boolean(string='Active ?', default=True)

class QrfConc(models.Model):
    _name = 'qrf.con'
    # _rec_name = 'desc'

    name = fields.Char(string='qrf')    
    new_product = fields.Selection(
        [("yes", "Yes"), ("no", "No")], string='New Product', default='yes')
    comp_partial = fields.Selection(
        [("complete", "Complete"), ("partial", "Partial")], string='Complete/Partial', default='complete')
    turret = fields.Selection(
        [("yes", "Yes"), ("no", "No")], string='Reference Turret <= 5 years?', default='yes')
    tooling = fields.Selection(
        [("eu_tsm", "EU / TSM"), ("other", "Other")], string='Tooling Type', default='eu_tsm')
    tooling_qc = fields.Selection(
        [("altinex", "Altinex"), ("other", "Other")], string='Current Tools producing qc-pass tablets', default='altinex')
    con_id = fields.Many2one('conclusion', string='Conclusion',)
    urutan = fields.Integer(string='Urutan', default=0)
    active = fields.Boolean(string='Active ?', default=True)
    