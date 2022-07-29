from odoo import api, fields, models, _

class CreateAttendeeWizard(models.TransientModel):
	_name = 'create.do.wizard'

	def _get_active_session(self):
		context = self.env.context

		if context.get('active_model') == 'sale.order':
			return context.get('active_ids', False)
			return False

	# session_id = fields.Many2one(comodel_name="academic.session", string="Session", required=False, default=_get_active_session, )
	so_ids = fields.Many2many(comodel_name="sale.order", string="Saleorders", )
	do_ids = fields.One2many(comodel_name="do.wizard",inverse_name="wizard_id",
								   string="Attendees to Add", required=False, )
	# create method
	@api.multi
	def action_add_do(self):
		self.ensure_one()
		# session = self.session_id
		# session = self.session_ids
		dos = self.do_ids
		att_data = [{'partner_id': att.partner_id.id} for att in self.attendee_ids]
		#session.attendee_ids = [(0, 0, data) for data in att_data]
		for do in dos:
				 do.do_ids = [(0, 0, data) for data in att_data]
		return {'type': 'ir.actions.act_window_close'}

class AttendeeWizard(models.TransientModel):
	_name = 'do.wizard'

	wizard_id = fields.Many2one(comodel_name = "create.do.wizard", string="Wizard", required=False, )
	partner_id = fields.Many2one(comodel_name="res.partner", string="Partner", required=False, )
