from odoo import models, fields, api, _
from odoo.exceptions import UserError
import base64
from werkzeug.datastructures import FileStorage
from io import BytesIO
import os
import requests
import urllib

class InsertImage(models.Model):
    _name = 'insert.image'

    image_binary = fields.Char(string='Image',
    compute="_compute_img"
    )
    image_desc = fields.Char(string='Description')
    purchase_id = fields.Many2one('purchase.order', string='Move') 
    format_file = fields.Char(string='Format File')

    def _compute_img(self):
        for rec in self:
            url = self.env.ref('inherit_purchase_order.url_image_receipt').read()[0]['value']
            path_url = "%s%s%s" % (url, rec.id, rec.format_file)
            rec.image_binary = self.load_image_from_url(path_url)
            
    # def load_image_from_url(self, url):
    #     print("================load_image_from_url inventory================")
    #     print("url", url)
    #     localhost = self.env['ir.config_parameter'].search([('key', '=', 'web.base.url')]).value
    #     data = False
    #     if self.exists(url):
    #         data = base64.b64encode(requests.get(url.strip()).content).replace(b'\n', b'')
    #     else:
    #         data = base64.b64encode(requests.get(localhost+'/web/static/src/img/placeholder.png'.strip()).content).replace(b'\n', b'')
    #     return data
    
    # def exists(self, url):  
    #     a=urllib.request.urlopen(url)
    #     return a.getcode() == 200

    # @api.model
    # def create(self, values):
    #     path   = self.env.ref('inherit_inventory.path_image_receipt').read()[0]['value']
    #     result = super(StockMoveImage, self).create(values)
    #     file_name    = result.id
    #     binary       = values['image_binary']
    #     file_data    = BytesIO(base64.b64decode(binary))
    #     content_type = 'image/png' if binary[0] == 'i' else 'image/jpeg'
    #     file         = FileStorage(file_data, filename=file_name, content_type=content_type)
    #     format_file  = '.png' if content_type == 'image/png' else '.jpeg'
    #     file.save(os.path.join(path, str(file_name) + format_file))
    #     self.browse(file_name).write({'format_file' : format_file})
    #     return result

    # def write(self, values):
    #     if values.get('image_binary', False):
    #         path   = self.env.ref('inherit_inventory.path_image_receipt').read()[0]['value']
    #         file_name    = self.id
    #         binary       = values['image_binary']
    #         file_data    = BytesIO(base64.b64decode(binary))
    #         content_type = 'image/png' if binary[0] == 'i' else 'image/jpeg'
    #         file         = FileStorage(file_data, filename=file_name, content_type=content_type)
    #         format_file  = '.png' if content_type == 'image/png' else '.jpeg'
    #         file.save(os.path.join(path, str(file_name) + format_file))
    #     return super(StockMoveImage, self).write(values)
    

    # def unlink(self):
    #     path   = self.env.ref('inherit_inventory.path_image_receipt').read()[0]['value']
    #     for rec in self:
    #         file = "%s%s%s" % (path, rec.id, rec.format_file)
    #         os.remove(file)
    #     return super(StockMoveImage, self).unlink()

    # def action_show_image(self):
    #     action = self.env.ref('inherit_purchase_order.purchase_order_action').read()[0]
    #     action['res_id'] = self.id
    #     action['name'] = "Images of %s" % (self.product_id.name)
    #     return action