{
    "name"          : "Stock",
    "version"       : "1.0",
    "author"        : "Angkringan",
    "website"       : "",
    "category"      : "Warehouse",
    "summary"       : "",
    "description"   : """
        
    """,
    "depends"       : [
        "stock",
        "stock_account",
        "purchase",
    ],
    "data"          : [
        "security/ir.model.access.csv",
        "views/stock_picking_view.xml",
        "views/stock_production_lot_view.xml",
        "views/purchase_order.xml",
        # "views/stock_pack_operation_view.xml",
        "wizard/angkring_duplicate_lot.xml",
        "data/ir_sequence.xml",
        "report/print_barcode.xml",
        "report/stock_picking_print_barcode.xml",
        "report/print_penerimaan.xml",
        "wizard/split_barcode_wizard.xml",
        # ADD CRON TO CALL PRODUCT AGE FUNCTION MODEL STOCK PROD. LOT
        # "data/ir_cron.xml",
    ],
    "demo"          : [],
    "test"          : [],
    "images"        : [],
    "qweb"          : [],
    "css"           : [],
    "application"   : True,
    "installable"   : True,
    "auto_install"  : False,
}