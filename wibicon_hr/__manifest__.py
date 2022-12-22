{
	"name": "HR Extenstion",
	"version": "1.0", 
	"depends": [
		"base",
		"hr_contract",
		"hr_recruitment",
		"wibicon_hr_job",
	],
	"author": "https://www.wibicon.com", 
	"category": "Extra", 
	'website': 'https://www.wibicon.com',
	"description": """\
This addons works for manage data of HR Department
--------------------------------------------------


""",
	"data": [
		"security/ir.model.access.csv",
		"data/hr.job.level.csv",
		"data/hr.job.csv",
		"data/hr.ptkp.csv",
		"data/hr.pkp.csv",
		"data/account.journal.csv",
		"data/hr.contract.type.csv",
		"data/res.bank.csv",
		"data/hr.recruitment.stage.csv",
	],
	"installable": True,
	"auto_install": False,
    "application": True,
}
