# -*- coding: utf-8 -*-


from os.path import dirname, abspath
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import csv
from datetime import datetime
from datetime import date
import xlrd


class SMCInvoicesXLSX(models.Model):
    _inherit = 'account.move'

    def create_invoice_xlsx(self):
        # loc = ("/home/musadiqfiazch/odoo-14.0/SMC-UAT-Latest/excel_open_read/static/smc_invoice.xlsx")
        loc = abspath(dirname(dirname(dirname(__file__)))) + '/excel_open_read/static/smc_invoice.xlsx'
        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)
        m = 0
        i = 0
        for line in range(sheet.nrows):
            line_val = []
            i = i + 1
            if i != 1:
                partner_records = self.env['res.partner'].search([('name', '=', sheet.row_values(line)[7])], limit=1)
                product_records = self.env['product.product'].search([('id', '=',  int(sheet.row_values(line)[13]))])
                uom_records = self.env['uom.uom'].search([('name', '=', sheet.row_values(line)[20])], limit=1)
                branch_records = self.env['res.branch'].search([('name', '=', sheet.row_values(line)[1])], limit=1)
                user_records = self.env['res.users'].search([('name', '=', sheet.row_values(line)[5])], limit=1)
                if sheet.row_values(line)[7] != '':
                    line_val.append((0, 0, {
                        'product_id': product_records.id,
                        'quantity': sheet.row_values(line)[15],
                        'product_uom_id': uom_records.id,
                        'discount': sheet.row_values(line)[17],
                        'price_unit': sheet.row_values(line)[16],
                    }))
                    seconds = (sheet.row_values(line)[22] - 25569) * 86400.0
                    tin = datetime.utcfromtimestamp(seconds)
                    vals = {
                        'partner_id': partner_records.id,
                        'branch_id': branch_records.id,
                        'ref': sheet.row_values(line)[0],
                        'invoice_user_id': user_records.id,
                        'invoice_date': tin,
                        'account_link': sheet.row_values(line)[25],
                        'company_id': self.env.company.id,
                        'invoice_line_ids': line_val
                    }
                    record = self.env['account.move'].sudo().create(vals)
                    m = m + 1
                    print("record is created. ", m)
                else:
                    line_val.append((0, 0, {
                        'product_id': product_records.id,
                        'quantity': sheet.row_values(line)[15],
                        'product_uom_id': uom_records.id,
                        'price_unit': sheet.row_values(line)[16],
                    }))
                    record.sudo().update({'invoice_line_ids': line_val})
