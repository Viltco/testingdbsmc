# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResPartnerInh(models.Model):
    _inherit = 'res.partner'

    partner_balance = fields.Float('Balance')
    partner_balance_1 = fields.Float('Balance', compute='compute_partner_balance')

    def compute_partner_balance(self):
        for rec in self:
            rec.partner_balance_1 = rec.credit - rec.debit
            rec.partner_balance = rec.partner_balance_1

