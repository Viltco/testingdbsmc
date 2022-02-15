from odoo import models
import string


class CustomerExport(models.AbstractModel):
    _name = 'report.xlsx_customer_export.xlsx_customer_export'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, lines):
        format1 = workbook.add_format(
            {'font_size': 12, 'align': 'vcenter', 'bold': True, 'bg_color': '#d3dde3', 'color': 'black',
             'bottom': True, })
        format2 = workbook.add_format(
            {'font_size': 12, 'align': 'vcenter', 'bold': True, 'bg_color': '#edf4f7', 'color': 'black',
             'num_format': '#,##0.00'})
        format3 = workbook.add_format({'font_size': 11, 'align': 'vcenter', 'bold': False, 'num_format': '#,##0.00'})
        format3_colored = workbook.add_format(
            {'font_size': 11, 'align': 'vcenter', 'bg_color': '#f7fcff', 'bold': False, 'num_format': '#,##0.00'})
        format4 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': True})
        format5 = workbook.add_format({'font_size': 12, 'align': 'vcenter', 'bold': False})

        sheet = workbook.add_worksheet("Customer Export")
        customers = self.env['res.partner'].search([])

        sheet.write(1, 0, 'Id', format1)
        sheet.write(1, 1, 'Name', format1)
        sheet.write(1, 2, 'Sales Person', format1)
        sheet.write(1, 3, 'Customer Code', format1)
        sheet.write(1, 4, 'Branch', format1)
        sheet.write(1, 5, 'Tags', format1)
        i = 3
        for customer in customers:
            res = customer.get_external_id()
            sheet.write(i, 0, res[customer.id], format5)
            sheet.write(i, 1, customer.name, format5)
            sheet.write(i, 2, customer.user_id.name, format5)
            sheet.write(i, 3, customer.customer_code, format5)
            sheet.write(i, 4, customer.branch_id.name, format5)
            if customer.category_id:
                sheet.write(i, 5, customer.category_id[0].name, format5)
            i = i + 1