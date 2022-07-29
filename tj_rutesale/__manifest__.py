{
	"name": "Rute Sale",
	"version": "1.1",
	"depends": [
		"base",
		"sale",
		"stock",
		"account",
		"tj_kontrabon",
		"dh_res_partner",
		"inherit_fleet",
	], 
	"author": "Angkringan", 
	"category": "Sale",
	"website": 'http://www.wibicon.com',
	"description": """\

Features
======================================================================


""",
	"data": [
		"security/security.xml",
		"security/ir.model.access.csv",
		# "views/invoice.xml",
		"views/top_menu.xml", 
		"views/rutesale.xml",
		"views/rute_absen_qr.xml",
		"views/rute_absen_sale.xml",
		"views/rute_group.xml",
		"views/rute_partner.xml",
		"views/rute_sale_new_customer.xml",
		"views/rute_sale_config.xml",
		"views/rute_sale_expense.xml",
		"report/report_rutesale.xml",
		"data/ir_sequence_data.xml",
	],
	"installable": True,
	"auto_install": False,
	"application": True,
}