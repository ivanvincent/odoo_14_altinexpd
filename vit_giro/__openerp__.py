{
	"name": "Giro Rev By Imat 2018-09-05",
	"version": "1.1",
	"depends": [
		"account_voucher"
	], 
	"author": "akhmad.daniel@gmail.com", 
	"category": "Accounting",
	"website": 'http://www.vitraining.com',
	"description": """\
Revisi By Imat. 5 September 2018
Features
======================================================================

* mencatat data cek dan giro yg dikeluarkan atau diterima perusahaan untuk membayar hutang atau pelunasan piutang
* created menu:
	* Accounting / Giro / Giro
* created object
	* vit.giro
* created views
	* giro
	* invoice
* logic:
	* user mencatat giro dan mengalokasikan ke invoice-invoice yg hendak di bayar
	* user bisa lihat daftar giro yg jatuh tempo per hari
	* jika dicek ke rek bank, giro tersebut sdh clearing maka user klik tombol clearing
	* system akan membuat invoice payment sesuai alokasi pada giro


Special thanks to Mr Tiongsin for the business logics :)

""",
	"data": [
		"security/security.xml", 
		"security/ir.model.access.csv", 
		"menu.xml", 
		"view/giro.xml",
		"view/invoice.xml",
		"wizard/giro_wizard.xml",
	],
	"installable": True,
	"auto_install": False,
	"application": True,
}