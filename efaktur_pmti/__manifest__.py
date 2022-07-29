{
    'name': "Inherite Efaktur",
    'version': '1.0',
    'depends': ['account', 'tj_vit_efaktur', 'base'],
    'author': "Wibicon",
    'category': 'Accounting',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        # 'security/ir.model.access.csv',
        # 'data/ir_sequence.xml',
        # 'wizard/update_address_wizard.xml',
        # 'views/account_move.xml',
        # 'views/account_account.xml',
        # 'views/account_move_line.xml',
        # 'views/mutasi_persediaan.xml',
        'views/efaktur.xml',
    ],
}