from odoo import models, fields, api, _
from odoo.exceptions import UserError

from io import BytesIO
import os
import requests
import urllib
import base64


class AccountMoveLineImages(models.Model):
    _name = 'account.move.line.images'

    image_binary = fields.Char(string='Image',
    compute="_compute_img"
    )
    image_desc = fields.Char(string='Description')
    account_move_line_id = fields.Many2one('account.move.line', string='Move') 
    filename = fields.Char(string='Filename')

    def _compute_img(self):
        for rec in self:
            url = self.env.ref('inherit_inventory.url_image_receipt').read()[0]['value']
            path_url = "%s%s" % (url, rec.filename)
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