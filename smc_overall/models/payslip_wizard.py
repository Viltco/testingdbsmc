from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class PayrollWizard(models.TransientModel):
    _name = 'payroll.wizard'
    _description = 'Payroll Payment'

    journal_id = fields.Many2one('account.journal', string="Journal")
    payment_date = fields.Date(string="Payment Date", compute='get_date')
    payslip_line = fields.One2many('payroll.wizard.line', 'payment_id')
#     is_lines_added = fields.Boolean('Is Lines Added?', default =False)

    def create_data(self):
        for rec in self.payslip_line:
            rec.slip_id.conveyance = rec.conveyance
            rec.slip_id.mobile_allowance = rec.mobile_allowance
            rec.slip_id.meal_allowance = rec.meal_allowance
        self.action_compute_deductions()


    def action_compute_deductions(self):
        for rec in self.payslip_line:
            # val = {
            #     'Conveyance': rec.conveyance
            # }
            # vals_list = []
            # category = self.env['hr.salary.rule.category'].search([('code', '=', 'DED')])
            # oad = self.env['hr.salary.rule'].search([('code', '=', 'OAD')])
            # vals_list.append([0, 0, {
            #     'name': 'Old Advance',
            #     'code': 'OAD',
            #     'sequence': 101,
            #     'category_id': category.id,
            #     'salary_rule_id': oad.id,
            #     'amount': rec.conveyance,
            #     'total': rec.conveyance,
            #     'quantity': 1,
            # }])
            #
            # cad = self.env['hr.salary.rule'].search([('code', '=', 'CAD')])
            # vals_list.append([0, 0, {
            #     'name': 'Current Advance',
            #     'code': 'CAD',
            #     'category_id': category.id,
            #     'sequence': 101,
            #     'salary_rule_id': cad.id,
            #     'amount': rec.mobile_allowance,
            #     'total': rec.mobile_allowance,
            #     'quantity': 1,
            # }])
            # ads = self.env['hr.salary.rule'].search([('code', '=', 'ADS')])
            # vals_list.append([0, 0, {
            #     'name': 'Absent Days',
            #     'code': 'ADS',
            #     'sequence': 101,
            #     'category_id': category.id,
            #     'salary_rule_id': ads.id,
            #     'amount': rec.meal_allowance,
            #     'total': rec.meal_allowance,
            #     'quantity': 1,
            # }])
            # rec.slip_id.line_ids = vals_list
            total = rec.meal_allowance + rec.mobile_allowance + rec.conveyance
            for line in rec.slip_id.line_ids:
                if line.code == 'NET':
                    line.amount = line.amount - total
                if line.code == 'OAD':
                    line.amount = rec.conveyance
                    line.total = rec.conveyance
                if line.code == 'CAD':
                    line.amount = rec.mobile_allowance
                    line.total = rec.mobile_allowance
                if line.code == 'ADS':
                    line.amount = rec.meal_allowance
                    line.total = rec.meal_allowance

    def write_amount(self):
        for record in self.payslip_line:
            rec = self.env['hr.payslip'].search([('number', '=', record.number)])
            rec.write({
                'amount_to_pay': record.amount_to_pay,
            })


class PayrollWizardLine(models.TransientModel):
    _name = 'payroll.wizard.line'
    _description = 'Payroll Payment Line'

    payment_id = fields.Many2one('payroll.wizard')
    slip_id = fields.Many2one('hr.payslip')
    employee_id = fields.Many2one('hr.employee')
    conveyance = fields.Float('Old Advance')
    mobile_allowance = fields.Float('Current Advance')
    meal_allowance = fields.Float('Absent Days')

