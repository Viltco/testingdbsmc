# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from pytz import timezone


class InheritDelivery(models.Model):
    _inherit = 'stock.move.line'

    article_no = fields.Char("Article")
    finish = fields.Char("Finish")


class InheritPicking(models.Model):
    _inherit = 'stock.picking'

    current_user = fields.Many2one('res.users', 'Current User', default=lambda self: self.env.user)

    def get_print_date(self):
        now_utc_date = datetime.now()
        now_dubai = now_utc_date.astimezone(timezone('Asia/Karachi'))
        return now_dubai.strftime('%m/%d/%Y %H:%M:%S')
