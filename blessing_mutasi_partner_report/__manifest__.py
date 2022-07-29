{
"name": "Blessing Mutasi Partner Report #1",
"version": "1.0",
"depends": [
"base",
"account",
# "account_financial_report_qweb",
],
"author": "asepimat@gmail.com",
"category": "Accounting support",
'website': 'http://www.odoobandung.com',
"description": """
   Require install pip pandas python
	Mutasi Partner Report :
	- Payable (Vendor Trial Balance) -
	- Receivable (Customer Trial Balance) -
	- Payable Card Transaction -
	- Receivable Card Transaction -

""",
"data": [
         "security/ir.model.access.csv",
         "data/ir_sequence_data.xml",
         "views/blessing_mutasi_partner_report_name.xml",
         "views/blessing_mutasi_partner_report_view.xml",
         "views/blessing_mutasi_partner_report_form.xml",
         "views/account_account.xml",
         "report/blessing_mutasi_partner_report_template.xml",
         "report/blessing_mutasi_partner_report_template2.xml",
         "report/layout.xml",
         ],
"application": True,
"installable": True,
"auto_install": False,
}
