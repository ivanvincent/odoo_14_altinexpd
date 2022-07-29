# -*- coding: utf-8 -*-
##############################################################################

{
    'name'      : 'Sharon - Sellingout',
    'version'   : '13.0.20.4.27',
    'author'    : 'djoyo503@gmail.com',
    'depends'   : ['base','base_setup','mail', ],
	'qweb'      : ['static/src/xml/qweb.xml'],
    'data': [
        'security/ir.model.access.csv',        
		'views/assets.xml',
        'views/sellingout_view.xml',
        'views/sellingout_xls.xml',

        #'views/menu.xml',

    ],
    'installable': True,
  
}
