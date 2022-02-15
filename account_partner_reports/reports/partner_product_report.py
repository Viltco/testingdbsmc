# -*- coding: utf-8 -*-


from odoo import models, api
from datetime import datetime
from pytz import timezone


class AccountReport(models.AbstractModel):
    _name = "report.account_partner_reports.partner_product_wise_report"

    @api.model
    def _get_report_values(self, docids, data=None):
        # print('Hello')
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        invoices = self.env['account.move'].search([('move_type', '=', 'out_invoice'), ('invoice_date', '>=', rec_model.date_from), ('invoice_date', '<=', rec_model.date_to), ('partner_id', '=', rec_model.partner_id.id)])
        return {
            'docs': rec_model,
            'doc_model': 'partner.product.wizard',
            'invoices': invoices
        }
