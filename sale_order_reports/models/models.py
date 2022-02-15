# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from pytz import timezone


class ResCompanyInh(models.Model):
    _inherit = 'res.company'

    cs = fields.Char('CS')


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    def get_print_date(self):
        now_utc_date = datetime.now()
        now_dubai = now_utc_date.astimezone(timezone('Asia/Karachi'))
        return now_dubai.strftime('%d/%m/%Y %H:%M:%S')

    def get_mobile(self, user):
        employee = self.env['hr.employee'].search([('user_id', '=', user.id)], limit=1)
        if employee:
            return employee.mobile_phone
        else:
            return ''
