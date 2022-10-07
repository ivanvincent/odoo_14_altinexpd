from datetime import datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
# from odoo.tools.float_utils import float_is_zero, float_compare
# from odoo.exceptions import UserError, AccessError
# from odoo.tools.misc import formatLang
# from odoo.addons.base.res.res_partner import WARNING_MESSAGE, WARNING_HELP
import odoo.addons.decimal_precision as dp


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    makloon_id = fields.Many2one('makloon.order', string="Makor Number")
    