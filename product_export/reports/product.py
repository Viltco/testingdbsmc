from odoo import models
import string


class ProductExport(models.AbstractModel):
    _name = 'report.xlsx_product_export.xlsx_product_export'
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

        sheet = workbook.add_worksheet("Product Export")
        products = self.env['product.template'].search([])
        # res = products[0].get_external_id()
        # print(res.values()[0])

        sheet.write(1, 0, 'Id', format1)
        sheet.write(1, 1, 'Product Name', format1)
        sheet.write(1, 2, 'Article No', format1)
        sheet.write(1, 3, 'Finish No', format1)
        sheet.write(1, 4, 'System Code', format1)
        i = 3
        for product in products:
            res = product.get_external_id()
            sheet.write(i, 0, res[product.id], format5)
            sheet.write(i, 1, product.name, format5)
            sheet.write(i, 2, product.article_no, format5)
            sheet.write(i, 3, product.finish_no, format5)
            sheet.write(i, 4, product.system_code, format5)
            i = i + 1
        # print(products)