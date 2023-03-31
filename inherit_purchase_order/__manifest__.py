{
    'name': "Inherit Purchase",
    'version': '1.0',
    'depends': ['base', 'purchase'],
    'author': "Wibicon",
    'category': 'Category',
    'description': """
    Description text
    """,
    # data files always loaded at installation
    'data': [
        'security/ir.model.access.csv',
        'security/purchase_security.xml',
        'views/purchase_order_line.xml',
        'views/assets.xml',
        'views/product_product.xml',
        'views/purchase_order.xml',
        'views/purchase_order_category.xml',
        'views/report_po_supplier.xml',
        'views/purchase_custom_report.xml',
        'views/res_partner.xml',
        'report/purchase_order_periode.xml',
        'report/report_po_supplier_global.xml',
        'report/report_po_supplier_global_details.xml',
        'report/report_po_supplier_global_product.xml',
        'report/report_po_supplier_global_product_qty.xml',
        'report/report_po_supplier_product.xml',
        'report/report_po_supplier_product_details.xml',
        'report/report_permintaan_pembelian.xml',
        'wizard/purchase_order_pdf_wizard.xml',
        'wizard/purchase_report_wizard.xml',
        'data/ir.sequence.xml'
    ],
     'qweb': [
    # 'static/src/xml/purchase_report_line.xml',
  ],
}
