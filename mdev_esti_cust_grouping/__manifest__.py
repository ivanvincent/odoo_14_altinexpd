# -*- coding: utf-8 -*-
##############################################################################

{
    'name'      : 'Sharon - Estimate - Customer Grouping Uploader',
    'version'   : '13.0.20.7.10',
    'author'    : 'djoyo503@gmail.com',
    'depends'   : ['base','base_setup','mail','sale','sale_stock','mdev_estimate' ],
	'qweb'      : ['static/src/xml/qweb.xml'],
    'data': [

		'views/assets.xml',
        'views/res_partner_grouping_uploader.xml',
    ],
    'installable': True,
}
