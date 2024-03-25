<<<<<<< HEAD
from odoo import models, fields, api

class ConclusionNew(models.Model):
    _name = 'conclusion.new'
    # _rec_name = 'desc'

    name = fields.Char(string='Conclusion')    
    desc = fields.Char(string='Nama Spefisikasi')
    urutan = fields.Integer(string='Urutan', default=0)
    active = fields.Boolean(string='Active ?', default=True)


class QrfTemplateConc(models.Model):
    _name = 'qrf.template.con.new'
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
    con_ids = fields.One2many('qrf.con.new', 'qrf_template_id', string='Conclusion',)
    urutan = fields.Integer(string='Urutan', default=0)
    active = fields.Boolean(string='Active ?', default=True)
    con_id = fields.Many2one('conclusion.new', string='Conclusion',)
    # con1_id = fields.Many2one('conclusion', string='Conclusion 1',)
    # con2_id = fields.Many2one('conclusion', string='Conclusion 2',)
    # con3_id = fields.Many2one('conclusion', string='Conclusion 3',)
    # con4_id = fields.Many2one('conclusion', string='Conclusion 4',)
    # con5_id = fields.Many2one('conclusion', string='Conclusion 5',)

class QrfConc(models.Model):
    _name = 'qrf.con.new'
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
    con_id = fields.Many2one('conclusion.new', string='Conclusion',)
    urutan = fields.Integer(string='Urutan', default=0)
    active = fields.Boolean(string='Active ?', default=True)
    qrf_template_id = fields.Many2one('qrf.template.con.new', string="QRF Conclusion Template")

class InformConsentAttch(models.Model):
    _name = 'inform.consent.attch.new'

    attch_inform_consent = fields.Binary(string='Attachment')  
    inform_consent = fields.Char(string='Attachment Name')  
=======
from odoo import models, fields, api

class ConclusionNew(models.Model):
    _name = 'conclusion.new'
    # _rec_name = 'desc'

    name = fields.Char(string='Conclusion')    
    desc = fields.Char(string='Nama Spefisikasi')
    urutan = fields.Integer(string='Urutan', default=0)
    active = fields.Boolean(string='Active ?', default=True)


class QrfTemplateConc(models.Model):
    _name = 'qrf.template.con.new'
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
    con_ids = fields.One2many('qrf.con.new', 'qrf_template_id', string='Conclusion',)
    urutan = fields.Integer(string='Urutan', default=0)
    active = fields.Boolean(string='Active ?', default=True)
    con_id = fields.Many2one('conclusion.new', string='Conclusion',)
    # con1_id = fields.Many2one('conclusion', string='Conclusion 1',)
    # con2_id = fields.Many2one('conclusion', string='Conclusion 2',)
    # con3_id = fields.Many2one('conclusion', string='Conclusion 3',)
    # con4_id = fields.Many2one('conclusion', string='Conclusion 4',)
    # con5_id = fields.Many2one('conclusion', string='Conclusion 5',)

class QrfConc(models.Model):
    _name = 'qrf.con.new'
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
    con_id = fields.Many2one('conclusion.new', string='Conclusion',)
    urutan = fields.Integer(string='Urutan', default=0)
    active = fields.Boolean(string='Active ?', default=True)
    qrf_template_id = fields.Many2one('qrf.template.con.new', string="QRF Conclusion Template")

class InformConsentAttch(models.Model):
    _name = 'inform.consent.attch.new'

    attch_inform_consent = fields.Binary(string='Attachment')  
    inform_consent = fields.Char(string='Attachment Name')  
>>>>>>> 42cdb9030f851b5fe403eed06a6fc058da9468d8
    