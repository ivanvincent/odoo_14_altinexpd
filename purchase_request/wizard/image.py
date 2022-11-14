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

    # image_binary = fields.Char(string='Image',
    # compute="_compute_img"
    # )
    image_binary = fields.Binary(string='Image')
    image_desc = fields.Char(string='Description')
    purchase_line_id = fields.Many2one('purchase.request.line', string='Move') 
    format_file = fields.Char(string='Format File')

    def _compute_img(self):
        for rec in self:
            url = self.env.ref('purchase_request.url_image_receipt').read()[0]['value']
            path_url = "%s%s%s" % (url, rec.id, rec.format_file)
            rec.image_binary = self.load_image_from_url(path_url)