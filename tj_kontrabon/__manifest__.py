{
"name": "Kontrabon Order",
"version": "1.0",
"depends": [
"base",
"account",
"sale",
"product",
"fleet",
"stock",
# "tj_stock_picking_invoice",
# "tj_vit_efaktur",
# "tifatex_tj_accounting_custom",
],
"author": "angkringan.com",
"category": "IT support",
'website': 'http://www.prointegrated.com',
"description": """
Kontrabon order
""",
"data": [
         "security/user_groups.xml",
         "security/ir.model.access.csv",

         "data/ir_sequence_data.xml",

         "views/kontrabon_order_view.xml",
         "views/kontrabon_order.xml",
         "views/account_view.xml",
        #  "views/res_partner.xml",
         "data/res_groups.xml",

         "report/report_kb_bca.xml",
        #  "report/report_kb_tunai.xml",
        #  "report/report_kb_utang.xml",
        #  "report/report_kb_va.xml",
        #  "report/report_kontrabon.xml",
         "report/bukti_pengeluaran_bank.xml"
],
"application": True,
"installable": True,
"auto_install": False,
}
