from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from werkzeug.datastructures import FileStorage
from io import BytesIO
import os
import requests
import urllib

class AccountBankStatementImage(models.Model):
    _name = 'account.bank.statement.image'

    image_binary = fields.Char(string='Image',
    compute="_compute_img"
    )
    image_desc = fields.Char(string='Description')
    account_bank_statement_line_id = fields.Many2one('account.bank.statement.line', string='Move') 
    format_file = fields.Char(string='Format File')

    def _compute_img(self):
        for rec in self:
            url = self.env.ref('tj_bankcash.url_image_statement_line_image').read()[0]['value']
            path_url = "%s%s%s" % (url, rec.id, rec.format_file)
            rec.image_binary = self.load_image_from_url(path_url)
            
    def load_image_from_url(self, url):
        localhost = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')]).value
        data = False
        if self.exists(url):
            data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
        else:
            data = base64.b64encode(requests.get(localhost+'/web/static/src/img/placeholder.png'.strip()).content).replace(b'\n', b'')
        return data
    
    def exists(self, url):  
        a=urllib.request.urlopen(url)
        return a.getcode() == 200

    @api.model
    def create(self, values):
        path   = self.env.ref('tj_bankcash.path_image_statement_line_image').read()[0]['value']
        result = super(AccountBankStatementImage, self).create(values)
        file_name    = result.id
        binary       = values['image_binary']
        file_data    = BytesIO(base64.b64decode(binary))
        content_type = 'image/png' if binary[0] == 'i' else 'image/jpeg'
        file         = FileStorage(file_data, filename=file_name, content_type=content_type)
        format_file  = '.png' if content_type == 'image/png' else '.jpeg'
        file.save(os.path.join(path, str(file_name) + format_file))
        self.browse(file_name).write({'format_file' : format_file})
        return result

    def write(self, values):
        if values.get('image_binary', False):
            path   = self.env.ref('tj_bankcash.url_image_statement_line_image').read()[0]['value']
            file_name    = self.id
            binary       = values['image_binary']
            file_data    = BytesIO(base64.b64decode(binary))
            content_type = 'image/png' if binary[0] == 'i' else 'image/jpeg'
            file         = FileStorage(file_data, filename=file_name, content_type=content_type)
            format_file  = '.png' if content_type == 'image/png' else '.jpeg'
            file.save(os.path.join(path, str(file_name) + format_file))
        return super(AccountBankStatementImage, self).write(values)
    

    def unlink(self):
        path   = self.env.ref('tj_bankcash.url_image_statement_line_image').read()[0]['value']
        for rec in self:
            file = "%s%s%s" % (path, rec.id, rec.format_file)
            os.remove(file)
        return super(AccountBankStatementImage, self).unlink()