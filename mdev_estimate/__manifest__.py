# -*- coding: utf-8 -*-
##############################################################################

{
    'name'      : 'Sharon - Estimate',
    'version'   : '13.0.20.5.3',
    'author'    : 'djoyo503@gmail.com',
    'depends'   : ['base','base_setup','mail','sale','sale_stock' ],
	'qweb'      : ['static/src/xml/qweb.xml'],
    'data': [
        'security/ir.model.access.csv',        

		'views/assets.xml',
        'views/estimate_view.xml',
        'views/res_partner_grouping_view.xml',
        'views/res_partner_product_view.xml',
        'views/res_partner_view.xml',
        'views/sale_order_view.xml',

        'wizards/actions_state.xml',
        'wizards/generator.xml',
        'wizards/adjustment.xml',

        'wizards/cust_group_update.xml',
        'wizards/uploader.xml',
        'wizards/action.xml',

        #'datas/init.xml',
    ],
    'installable': True,
}
