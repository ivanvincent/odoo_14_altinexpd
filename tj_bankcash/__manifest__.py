{
	"name": "Bank & Cash",
	"version": "13.0", 
	"depends": [
		"base",
		"base_setup",
		"mail",
		"product",
		"account",
		"stock",
		"sale",
		"hr",
  		"accounting_pdf_reports",
		"tj_kontrabon"
	
		# "analytic",
		# "report",
		# "web_planner",
	], 
	"author": "angkringan.com",
	"website": "http://www.prointegrated.com",
	"category": "IT support",
	"description": """

Features
======================================================================

* Bank Statement.
* Cash Register.
* No Giro.
* Employe id.
* Expenses
""",
	"data": [
		'data/expenses_data.xml',
		'data/ir_sequence_data.xml',
		'data/res_groups.xml',
		# 'report/quotation_surat_jalan.xml',
        # 'report/quotation_surat_jalan2.xml',e
		"security/makloon_group.xml",
		"security/ir.model.access.csv",
		"report/report_account_bank_statement.xml",
		"report/report_account_bank_statement2.xml",
		"report/report_account_bank_statement_line.xml",
		"report/tj_kasbank_template.xml",
		"report/trial_balance_new_template.xml",
		# "report/tj_kasbank_template.xml",
		"report/report_expenses.xml",
		# "report/expenses_report.xml",
		# "report/expenses_report_views.xml",
		"views/bankcash_view.xml",
		"views/bankcash_tree.xml",
		"views/account_move_tree.xml",
		"views/expenses_views.xml",
		"views/expenses_menu_views.xml",
		"wizard/kasbank.xml",
		"views/product.xml",
		"wizard/trial_balance_view_wizard.xml",
		"wizard/bank_statement_wizard.xml",
		"views/trial_new_balance_view.xml",
		"views/kategori_kas.xml",
		"views/account_journal.xml",
		# "views/res_partner.xml",
	],
	"application": True,
	"installable": True,
	"auto_install": False,
}