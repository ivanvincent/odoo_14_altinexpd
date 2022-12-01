# -*- coding: utf-8 -*-
{
    'name': 'Sale Contract Management',
    'version': '1.0.0',
    'summary': """
    This module helps to manage/approve/renew sale contracts
    , sale contract 
    , sale order contract 
    , quotation contract 
    , sale contract approval process
    , approve sale contract
    , approve contract sale
    , order contract approval workflow
    , sale contract management
    , customer contract approval
    , client contract
    , sale order template
    , customer invoice template
    , recurring sale order
    , recurring invoice
    , recurring customer invoice
    , recurring sales
    """,
    'category': 'Sales,Accounting,Document Management',
    'author': 'XFanis',
    'support': 'odoo@xfanis.dev',
    'website': 'https://xfanis.dev/odoo.html',
    # 'live_test_url': '',
    'license': 'OPL-1',
    'price': 5,
    'currency': 'EUR',
    'description':
        """
Sale Contract Management
============================
Manage, approve, renew sale contracts
        """,
    'data': [
        'views/partner_contract.xml',
        'views/res_config_settings_views.xml',
        'views/sale_order.xml',
    ],
    'depends': ['xf_partner_contract', 'sale_management'],
    'qweb': [],
    'images': [
        'static/description/xf_partner_contract_sale.png',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
