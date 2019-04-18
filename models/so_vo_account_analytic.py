# -*- coding: utf-8 -*-
 
from odoo import api, fields, models
import logging
_logger = logging.getLogger(__name__)

_logger.critical('so_vo_account_analytic INSTALLED')
class construction_change_order_extend(models.Model):
	_inherit = 'construction.change.order'

	approve_date = fields.Datetime(
		string='Approved Date',
		readonly=True, 
		copy=False,
	)

	@api.multi
	def done_state(self):
		for rec in self:
			budget_change_obj = self.env['so_vo.budget_change']
			new_group = [] 
			total_plan_amount = 0 
			no_budget_exist = False #flag if it does not have a product budget line
			# for variation order tab
			for record in rec.order_line_ids:
				no_group = False #this is flag if the product does not have a group
				_logger.warning('record.product_id = {}'.format(record.product_id))
				_logger.warning('rec.analytic_account_id.product_budget_lines = {}'.format(rec.analytic_account_id.product_budget_lines))
				if not rec.analytic_account_id.product_budget_lines:
					no_budget_exist = True
				# record.price_total
				for line in rec.analytic_account_id.product_budget_lines:
					exist = False
					_logger.warning('record.product_id = {} AND line.group_product_id.product_ids = {}'.format(record.product_id,line.group_product_id.product_ids))
					if record.product_id in line.group_product_id.product_ids:
						exist = True
					_logger.warning('exist = {}'.format(exist))
					if exist:
						_logger.warning('before line.planned_amount = {}'.format(line.planned_amount))
						line.planned_amount += record.price_total
						_logger.warning('after line.planned_amount = {}'.format(line.planned_amount))
						no_budget_exist = False
						break
					else:
						no_budget_exist = True
				if no_budget_exist:
					_logger.warning('no_budget_exist = {}'.format(no_budget_exist))

					# asdasd
					has_group = False
					group_or_prod_obj = self.env['group.products'].search([])
					_logger.warning('group_or_prod_obj = {}'.format(group_or_prod_obj))
					for grp in group_or_prod_obj:
						_logger.warning('_____________________________')
						_logger.warning('record.product_id = {} AND grp.product_ids = {}'.format(record.product_id,grp.product_ids))

						if record.product_id in grp.product_ids:
							_logger.critical('has_group = True')
							has_group = True
							temp = [(0,0,{
								'name':grp.name,
								'group_product_id':grp.id,
								'start_date':fields.Date.today(),
								'end_date':fields.Date.today(),
								'planned_amount':record.price_total
								})]
							_logger.warning('temp = {}'.format(temp))
							# for x in rec.analytic_account_id.product_budget_lines:
							# 	temp.append(x.id)
							_logger.warning('rec.analytic_account_id.product_budget_lines = {}'.format(rec.analytic_account_id.product_budget_lines))
							rec.analytic_account_id.product_budget_lines = temp
							_logger.warning('rec.analytic_account_id.product_budget_lines = {}'.format(rec.analytic_account_id.product_budget_lines))


							break

					if has_group:
						continue
					else:
						new_group.append(record.product_id.id)
						total_plan_amount += record.price_total

			_logger.warning('new_group = {}'.format(new_group))
			_logger.warning('total_plan_amount = {}'.format(total_plan_amount))

			prod_budget_line_obj = self.env['group.products'].search([('name','=','no_group')])
			_logger.warning('prod_budget_line_obj = {}'.format(prod_budget_line_obj))
			if prod_budget_line_obj:
				if new_group:
					prod_budget_line_obj.product_ids = new_group
					_logger.warning('prod_budget_line_obj.product_ids = {}'.format(prod_budget_line_obj.product_ids))
					
					prod_budget_line_env = self.env['product.budget.lines'].search([('group_product_id','=',prod_budget_line_obj.id)])
					_logger.critical('prod_budget_line_env = {}'.format(prod_budget_line_env))
					if prod_budget_line_env:
						temp = [(1,prod_budget_line_env.id,{
							'name':prod_budget_line_obj.name,
							'group_product_id':prod_budget_line_obj.id,
							'start_date':fields.Date.today(),
							'end_date':fields.Date.today(),
							'planned_amount':prod_budget_line_env.planned_amount + total_plan_amount
							})]
					else:
						temp = [(0,0,{
							'name':prod_budget_line_obj.name,
							'group_product_id':prod_budget_line_obj.id,
							'start_date':fields.Date.today(),
							'end_date':fields.Date.today(),
							'planned_amount':total_plan_amount
							})]

					
					_logger.warning('temp = {}'.format(temp))
					_logger.warning('rec.analytic_account_id.product_budget_lines = {}'.format(rec.analytic_account_id.product_budget_lines))
					rec.analytic_account_id.product_budget_lines = temp
					_logger.warning('rec.analytic_account_id.product_budget_lines = {}'.format(rec.analytic_account_id.product_budget_lines))
			else:
				grp_prod_obj = self.env['group.products']
				created_group = grp_prod_obj.search([('name','=','no_group')])
				if not created_group:
					created_group = grp_prod_obj.create({'name':'no_group','code':'no_group','product_ids':(0,0,new_group)})
				_logger.warning('created_group = {}'.format(created_group))
				temp = [(0,0,{
					'name':'no_group',
					'group_product_id':created_group.id,
					'start_date':fields.Date.today(),
					'end_date':fields.Date.today(),
					'planned_amount':total_plan_amount
					})]
				_logger.warning('temp = {}'.format(temp))
				_logger.warning('rec.analytic_account_id.product_budget_lines = {}'.format(rec.analytic_account_id.product_budget_lines))
				rec.analytic_account_id.product_budget_lines = temp
				_logger.warning('rec.analytic_account_id.product_budget_lines = {}'.format(rec.analytic_account_id.product_budget_lines))



			# for product budget hist
			current_budget_obj = budget_change_obj.search([('contract_id','=',rec.analytic_account_id.id)])
			temp_planned_amount = 0
			if current_budget_obj:
				for record in current_budget_obj:
					temp_planned_amount = record.new_amount
			else:
				temp_planned_amount = rec.original_contract_amount

			if temp_planned_amount < rec.original_contract_amount:
				temp_planned_amount = rec.original_contract_amount

			budget_obj = budget_change_obj.create({
					'contract_id':rec.analytic_account_id.id,
					'name':rec.name,
					'types':'Variation order',
					'reqstr_id':rec.user_id.id,
					'apprvr_id':rec.approve_by.id,
					'date_apprv':rec.approve_date,
					'old_amount':temp_planned_amount,
					'new_amount':temp_planned_amount + (rec.total_contract_amount_all_change - rec.original_contract_amount)
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
	date_apprv = fields.Datetime('Date Approved')
	old_amount = fields.Float('Old Planned Amount')
	new_amount = fields.Float('New Planned Amount')

