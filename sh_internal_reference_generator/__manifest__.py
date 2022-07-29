# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Product Internal Reference Generator",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",
    "category": "Product",
    "summary": """
 Internal Reference Generator, Make Internal Reference Default Module, Auto Generate Product Name Reference Number, Generate Sequence Reference No, Create Category Wise Reference No, Custom Internal Reference No App, Reference No Attributes Generator Odoo.

""",    
    "description": """Currently, in odoo there is no way to generate automatically internal reference with customization. Our this module will provide that feature, where you can create a pattern for internal reference of product. You can create or customize internal reference using the product name, sequence, category, attribute with separators. Also, you can set auto-generate internal references while creating a new product.
 Internal Reference Generator Odoo
 By Default Make Internal Reference Module, Auto Generate New Product Reference Number By Name, Automatic Generate Sequence Wise Reference No, Auto Create Category Wise Reference No, Custom Internal Reference No With Attributes Generator Odoo.
  Make Internal Reference Default Module, Auto Generate Product Name Reference Number, Generate Sequence Reference No, Create Category Wise Reference No, Custom Internal Reference No App, Reference No Attributes Generator Odoo.
""",
    "version":"13.0.2",
    "depends" : ["base", "base_setup", "sale_management", "account", "product"],
    "application" : True,
    "data" : [
            "views/res_config_setting_view.xml",
            "wizard/sh_internal_reference_wizard_view.xml",
            ],
    "images": ["static/description/background.png", ],
    "live_test_url": "https://www.youtube.com/watch?v=W6szJ_ZeBG4&feature=youtu.be",
    "application" : True,
    "installable" : True,
    "currency": "EUR",
    "price": "15"
}
