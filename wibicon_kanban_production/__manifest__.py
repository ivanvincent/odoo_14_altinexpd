{
	"name": "Wibicon Kanban Production",
	"version": "1.0", 
	"depends": [
		"base",
		"mrp"
	],
	"author": "Yugi, Wibicon", 
	"category": "Extra", 
	'website': 'https://www.wibicon.com',
	"description": """\
This addons works for manage data of HR Department
--------------------------------------------------


""",
	"data": [
		'views/kanban_production.xml'
	],
     'qweb': [
        'static/src/xml/kanban_production.xml', 
    ],
	"installable": True,
	"auto_install": False,
    "application": True,
}
