# -*- coding: utf-8 -*-
##############################################################################

{
    'name'      : 'Sharon - Main Module',
    'version'   : '13.0.20.4.13',
    'author'    : 'djoyo503@gmail.com',
    'depends'   : [
                    "sale",
                    "base",
                    "base_setup",
                    "mail", 
                    "hr",
                    "mdev_sellingout" 
    ],
    'data': [
        'security/ir.model.access.csv',
        #'security/res_groups.xml',
        #'views/webclient_templates.xml',
        #'views/res_partner_account.xml',

        #'views/header.xml',

        
        'views/menu.xml',
        'views/res_config_settings.xml',
        'views/hr_employee.xml',
        'views/product.xml',
        'views/res_partner.xml',
        'views/sale_order.xml',
    ],
    'application': True,
    'installable': True,
}
