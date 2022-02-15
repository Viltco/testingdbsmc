# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from pytz import timezone


class invone_smc(models.Model):
    _inherit = 'res.partner'

    no_cnic = fields.Char(string='CNIC')
    ntn = fields.Char(string='NTN')


class InheritField(models.Model):
    _inherit = 'account.move'

    freight = fields.Char(string='Details')
    journal_id = fields.Many2one("account.journal", string='Journal id')

    def get_print_date(self):
        now_utc_date = datetime.now()
        now_dubai = now_utc_date.astimezone(timezone('Asia/Karachi'))
        return now_dubai.strftime('%d/%m/%Y %H:%M:%S')


