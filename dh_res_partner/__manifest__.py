# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'EDP - Partner',
    'version': '12.0.1.0.0',
    'category': 'Res Partner',
    'summary': 'Partner Custom Sharon For Odoo 12',
    'sequence': '12',
    'author': 'Dhenz, Odoo SA',
    'company': 'Sangkuriang',
    'maintainer': 'Sangkuriang',
    'support': 'denihida1216@gmail.com',
    'website': '',
    'depends': ['fi_sale_sharon', 'vit_uudp'],
    # 'depends': ['fi_sale_sharon'],
    # 'depends': ['fi_sale_sharon'],
    'demo': [],
    'data': [
        'security/ir.model.access.csv',

        'views/res_partner_cluster.xml',
        #'views/res_partner_dc1.xml',
        #'views/res_partner_divisi1.xml',
        #'views/res_partner_divisi2.xml',
        'views/res_partner_jalur.xml',
        'views/res_partner_jalur_line.xml',
        #'views/res_partner_kategori1.xml',
        #'views/res_partner_kategori2.xml',
        #'views/res_partner_kategori3.xml',
        #'views/res_partner_kategori4.xml',
        #'views/res_partner_kelompok.xml',
        #'views/res_partner_region.xml',
        
        'views/res_partner_view.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'qweb': [],
}
