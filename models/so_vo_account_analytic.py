# -*- coding: utf-8 -*-
 
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)
class construction_change_order_extend(models.Model):
	_inherit = 'construction.change.order'

	@api.multi
	def done_state(self):
		budget_obj = self.env['so_vo.budget_change'].create({
				'contract_id':self.analytic_account_id.id,
				'name':self.name,
				'types':'Variation order',
				'reqstr_id':self.user_id.id,
				'apprvr_id':self.approve_by.id,
				'date_apprv':self.approve_date,
				'old_amount':self.original_contract_amount,
				'new_amount':self.total_contract_amount_all_change
			})
		res = super(construction_change_order_extend,self).done_state()

class contract_account_analytic_account(models.Model):
	_inherit = 'account.analytic.account'

	variation_table = fields.One2many('construction.change.order', 'analytic_account_id', 'Variation Order', copy=True)
	budget_change_hist = fields.One2many('so_vo.budget_change', 'contract_id', 'Budget Change History', copy=True)


class so_vo_variation_order(models.Model):
	_name = 'so_vo.budget_change'

	contract_id = fields.Many2one('account.analytic.account', string="Contract ID")
	name = fields.Char('Budget Change Name')
	types = fields.Char('Budget Change Type')
	reqstr_id = fields.Many2one('res.users', string="Requester")
	apprvr_id = fields.Many2one('res.users', string="Approver")
	date_apprv = fields.Date('Date Approved')
	old_amount = fields.Float('Old Planned Amount')
	new_amount = fields.Float('New Planned Amount')

