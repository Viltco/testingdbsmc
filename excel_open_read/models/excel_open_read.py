# -*- coding: utf-8 -*-

from odoo import models, fields, api
import csv


class CsvOpenRead(models.Model):
    _inherit = 'res.partner'

    def check_open_read(self):
        with open('/home/musadiqfiazch/odoo-14.0/custom-addons/excel_open_read/static/saleorder.csv') as csv_file:
            csv_reader = csv.reader(csv_file)
            for line in csv_reader:
                print(line)
                # part = self.env['res.partner'].browse([line[2]])
                print(line[2])
                vals = {
                    'partner_id': int(line[2]),
                    'user_id': line[3],
                    'company_id': self.env.company.id,
                    'state': line[5]
                }
                record = self.env['sale.order'].create(vals)
        csv_file.close()
