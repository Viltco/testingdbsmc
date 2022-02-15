# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError, Warning
import csv
from datetime import datetime
from datetime import date
import xlrd
import base64


class SMCTransfersXLSX(models.Model):
    _inherit = 'stock.picking'

    file_upload = fields.Binary(string='Upload File')

    def create_test(self):
        wb = xlrd.open_workbook(file_contents=base64.decodestring(self.file_upload))
        for s in wb.sheets():
            first_row = []  # Header
            for col in range(s.ncols):
                first_row.append(s.cell_value(0, col))
            data = []
            for row in range(1, s.nrows):
                elm = {}
                for col in range(s.ncols):
                    elm[first_row[col]] = s.cell_value(row, col)
                data.append(elm)

        for i in data:
            line_val = []
            partner_records = self.env['res.partner'].search([('name', '=', i.get('Contact'))], limit=1)
            product_records = self.env['product.template'].search([('name', '=', i.get('Operations / Product'))], limit=1)
            branch_records = self.env['res.branch'].search([('name', '=', i.get('Branch'))], limit=1)
            uom_records = self.env['uom.uom'].search([('name', '=', i.get('Operations / Unit Of Measure'))], limit=1)
            operation_records = self.env['stock.picking.type'].search([('name', '=', i.get('Operation Type'))],limit=1)
            location_records = self.env['stock.location'].search([('complete_name', '=', i.get('Operations / From'))])
            location_dest_records = self.env['stock.location'].search([('complete_name', '=', i.get('Operations / To'))])

            if i.get('Contact') != '':
                line_val.append((0, 0, {
                    'product_id': product_records.product_variant_id.id,
                    'name': product_records.product_variant_id.name,
                    'product_uom': uom_records.id,
                    'location_id': location_records.id,
                    'location_dest_id': location_dest_records.id,
                    'quantity_done': i.get('Operations / Done'),
                }))
                seconds = (i.get('DO Date') - 25569) * 86400.0
                tin = datetime.utcfromtimestamp(seconds)
                vals = {
                    'partner_id': partner_records.id,
                    'branch_id': branch_records.id,
                    'carrier_tracking_ref': i.get('Tracking Reference'),
                    'picking_type_id': operation_records.id,
                    'location_id': location_records.id,
                    'location_dest_id': location_dest_records.id,
                    'scheduled_date': tin,
                    'stock_link': i.get('Stock Link'),
                    'company_id': self.env.company.id,
                    'move_ids_without_package': line_val
                }
                record = self.env['stock.picking'].create(vals)
                print(record)
                if len(record.move_ids_without_package) > 1:
                    record.move_ids_without_package[0].unlink()
            else:
                line_val.append((0, 0, {
                    'product_id': product_records.product_variant_id.id,
                    'name': product_records.product_variant_id.name,
                    'quantity_done': i.get('Operations / Done'),
                    'product_uom': uom_records.id,
                    'location_id': location_records.id,
                    'location_dest_id': location_dest_records.id,
                }))
                record.update({'move_ids_without_package': line_val})





    # def create_transfer_xlsx(self):
    #     loc = ("/home/musadiqfiazch/odoo-14.0/SMC-UAT-Latest/excel_open_read/static/smc_all_do.xlsx")
    #     wb = xlrd.open_workbook(loc)
    #     sheet = wb.sheet_by_index(0)
    #     i = 0
    #     for line in range(sheet.nrows):
    #         line_val = []
    #         i = i + 1
    #         if i != 1:
    #             if sheet.row_values(line)[10]:
    #                 partner_records = self.env['res.partner'].search([('name', '=', sheet.row_values(line)[10])], limit=1)
    #                 if not partner_records:
    #                     ptr_record = {
    #                         'name': sheet.row_values(line)[10],
    #                     }
    #                     partner_records = self.env['res.partner'].create(ptr_record)
    #
    #             if sheet.row_values(line)[13]:
    #                 product_records = self.env['product.template'].search([('name', '=', sheet.row_values(line)[13])], limit=1)
    #                 if not product_records:
    #                     prd_record = {
    #                         'name': sheet.row_values(line)[13],
    #                     }
    #                     product_records = self.env['product.template'].create(prd_record)
    #
    #             if sheet.row_values(line)[21]:
    #                 uom_records = self.env['uom.uom'].search([('name', '=', sheet.row_values(line)[21])], limit=1)
    #                 uom_cat_records = self.env['uom.category'].search([('name', '=', 'Unit')])
    #                 if not uom_records:
    #                     uom_record = {
    #                         'name': sheet.row_values(line)[21],
    #                         'uom_type': 'bigger',
    #                         'category_id': uom_cat_records.id,
    #                         'rounding': 0.01000,
    #                     }
    #                     uom_records = self.env['uom.uom'].create(uom_record)
    #             branch_records = self.env['res.branch'].search([('name', '=', sheet.row_values(line)[1])], limit=1)
    #             operation_records = self.env['stock.picking.type'].search([('name', '=', sheet.row_values(line)[5])], limit=1)
    #             location_records = self.env['stock.location'].search([('complete_name', '=', sheet.row_values(line)[8])])
    #             location_dest_records = self.env['stock.location'].search([('complete_name', '=', sheet.row_values(line)[9])])
    #             if sheet.row_values(line)[10] != '':
    #                 line_val.append((0, 0, {
    #                     'product_id': product_records.product_variant_id.id,
    #                     'name': product_records.product_variant_id.name,
    #                     'product_uom': uom_records.id,
    #                     'location_id': location_records.id,
    #                     'location_dest_id': location_dest_records.id,
    #                     'quantity_done': sheet.row_values(line)[20],
    #                 }))
    #                 seconds = (sheet.row_values(line)[22] - 25569) * 86400.0
    #                 tin = datetime.utcfromtimestamp(seconds)
    #                 vals = {
    #                     'partner_id': partner_records.id,
    #                     'branch_id': branch_records.id,
    #                     'carrier_tracking_ref': sheet.row_values(line)[0],
    #                     'picking_type_id': operation_records.id,
    #                     'location_id': location_records.id,
    #                     'location_dest_id': location_dest_records.id,
    #                     'scheduled_date': tin,
    #                     'stock_link': sheet.row_values(line)[23],
    #                     'company_id': self.env.company.id,
    #                     'move_ids_without_package': line_val
    #                 }
    #                 record = self.env['stock.picking'].create(vals)
    #                 if len(record.move_ids_without_package) > 1:
    #                     record.move_ids_without_package[0].unlink()
    #             else:
    #                 line_val.append((0, 0, {
    #                     'product_id': product_records.product_variant_id.id,
    #                     'name': product_records.product_variant_id.name,
    #                     'quantity_done': sheet.row_values(line)[20],
    #                     'product_uom': uom_records.id,
    #                     'location_id': location_records.id,
    #                     'location_dest_id': location_dest_records.id,
    #                 }))
    #                 record.update({'move_ids_without_package': line_val})
