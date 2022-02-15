from odoo import models, fields, api,_
from odoo.exceptions import UserError


class GeneralReportWizard(models.TransientModel):
    _name = 'general.ledger.wizard'

    date_from = fields.Date('Date From')
    date_to = fields.Date('Date To')
    account_id = fields.Many2one('account.account')

    def print_report(self):
        data = {}
        data['form'] = self.read(['account_id', 'date_from', 'date_to'])[0]
        return self.env.ref('general_ledger_report_pdf.action_general_pdf_report').report_action(self, data=data, config=False)
