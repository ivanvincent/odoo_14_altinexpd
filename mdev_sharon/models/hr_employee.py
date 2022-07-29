from odoo import api, fields, models
from odoo.exceptions import ValidationError

class Employee(models.Model):
	_inherit = 'hr.employee'

	_sql_constraints = [
        ('employee_id_uniq', 'unique(employee_id)', 'DUPLICATED [Employee ID]'),
    ]

	@api.constrains('employee_id')
	def _check_emp_no(self):
		if self.employee_id:
			v = self.employee_id
			if not v.isdigit():
				raise ValidationError('NO_ACCEPTED [Employee ID]')

	employee_id = fields.Char(size=8, string='Employee ID' )
