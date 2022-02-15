import xlsxwriter

from odoo import models


class PartnerXlsx(models.AbstractModel):
    _name = 'report.bank_details.report_partner_xlsx'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, partners):
        # workbook = xlsxwriter.Workbook("file.xlsx")

        format0 = workbook.add_format({'font_size': 14, 'align': 'vcenter', 'bold': True})
        format1 = workbook.add_format({'font_size': 16, 'align': 'vcenter', 'bold': True})
        format2 = workbook.add_format({'font_size': 14, 'align': 'vcenter', })
        format3 = workbook.add_format({'font_size': 14, 'align': 'center', })
        format4 = workbook.add_format({'font_size': 14, 'align': 'center',  'bold': True})
        sheet = workbook.add_worksheet()

        sheet.set_column(3, 3, 60)
        sheet.set_column(4, 4, 20)
        sheet.set_column(5, 5, 15)
        sheet.set_column(6, 6, 15)
        sheet.set_column(7, 7, 15)
        sheet.set_column(8, 8, 15)

        sheet.write(3, 2, 'Sr#', format1)
        sheet.write(3, 3, 'Name', format1)
        sheet.write(3, 4, 'Date', format4)
        sheet.write(3, 5, 'Salesperson', format4)
        sheet.write(3, 6, 'Credit', format4)
        sheet.write(3, 7, 'Debit', format4)
        sheet.write(3, 8, 'Balance', format4)

        i = 4
        sr = 1
        total_bal = 0
        grand_debit = 0
        grand_credit = 0
        for rec in partners:
            partner_ledger = self.env['account.move.line'].search(
                [('partner_id', '=', rec.id),
                 ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
                 ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
                 ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable'), ],
                order="date asc")
            total_debit = 0
            total_credit = 0
            for res in partner_ledger:
                total_debit = total_debit + res.debit
                total_credit = total_credit + res.credit

            total_bal = total_bal + rec.partner_balance
            grand_debit = grand_debit + total_debit
            grand_credit = grand_credit + total_credit

            sheet.write(i, 2, sr, format3)
            sheet.write(i, 3, rec.name, format2)
            sheet.write(i, 4, rec.create_date.strftime("%d-%m-%Y"), format2)
            sheet.write(i, 5, rec.user_id.name, format2)
            sheet.write(i, 6, total_credit, format2)
            sheet.write(i, 7, total_debit, format2)
            sheet.write(i, 8, rec.partner_balance, format2)
            i = i + 1
            sr = sr + 1

        sheet.write(i+2, 6, grand_credit, format1)
        sheet.write(i+2, 7, grand_debit, format1)
        sheet.write(i+2, 8, total_bal, format1)

