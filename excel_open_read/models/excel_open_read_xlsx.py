# -*- coding: utf-8 -*-
import datetime

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import csv
import xlrd
import xlwt
import xlsxwriter
from xlrd import open_workbook
import tempfile
import binascii
from datetime import datetime
from datetime import date
import xlrd
import tempfile
import binascii


class ExcelOpenRead(models.Model):
    _inherit = 'sale.order'

    def create_sale_order_xlsx(self):
        loc = ("/home/musadiqfiazch/odoo-14.0/custom-addons/excel_open_read/static/sale_order.xlsx")
        wb = xlrd.open_workbook(loc)
        sheet = wb.sheet_by_index(0)
        # print(sheet.cell_value(0, 0))
        # print(sheet.nrows)
        # print(sheet.ncols)
        # for i in range(sheet.ncols):
            # print(sheet.cell_value(0, i))
        i = 0
        for line in range(sheet.nrows):
            line_val = []
            i = i + 1
            if i != 1:
                if sheet.row_values(line)[1]:
                    partner_records = self.env['res.partner'].search([('name', '=', sheet.row_values(line)[1])], limit=1)
                    if not partner_records:
                        ptr_record = {
                            'name': sheet.row_values(line)[1],
                        }
                        partner_records = self.env['res.partner'].create(ptr_record)

                if sheet.row_values(line)[2]:
                    product_records = self.env['product.template'].search([('name', '=', sheet.row_values(line)[2])])
                    if not product_records:
                        prd_record = {
                            'name': sheet.row_values(line)[2],
                        }
                        product_records = self.env['product.template'].create(prd_record)

                if sheet.row_values(line)[7]:
                    uom_records = self.env['uom.uom'].search([('name', '=', sheet.row_values(line)[7])])
                    uom_cat_records = self.env['uom.category'].search([('name', '=', 'Unit')])
                    if not uom_records:
                        uom_record = {
                            'name': sheet.row_values(line)[7],
                            'uom_type': 'bigger',
                            'category_id': uom_cat_records.id,
                            'rounding': 0.01000,
                        }
                        uom_records = self.env['uom.uom'].create(uom_record)

                if sheet.row_values(line)[1] != '' and sheet.row_values(line)[7] and sheet.row_values(line)[2]:
                    line_val.append((0, 0, {
                        'product_id': product_records.product_variant_id.id,
                        'product_uom_qty': sheet.row_values(line)[3],
                        'product_uom': uom_records.id,
                        'price_unit': sheet.row_values(line)[4],
                    }))
                    vals = {
                        'partner_id': partner_records.id,
                        'company_id': self.env.company.id,
                        'date_order': datetime.today().date(),
                        'order_line': line_val
                    }
                    record = self.env['sale.order'].create(vals)
                else:
                    line_val.append((0, 0, {
                        'product_id': product_records.product_variant_id.id,
                        'product_uom_qty': sheet.row_values(line)[3],
                        'product_uom': uom_records.id,
                        'price_unit': sheet.row_values(line)[4],
                    }))
                    record.update({'order_line':line_val})