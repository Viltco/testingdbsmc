# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    def remove_duplicate_sale_order(self):
        rec_list = []
        dup_list = []
        for i in self:
            if i.name not in rec_list:
                rec_list.append(i.name)
            else:
                dup_list.append(i.id)
        duplicate = self.env['sale.order'].search([('id', 'in', dup_list)]).unlink()


class ProductTemplateInh(models.Model):
    _inherit = 'product.template'

    def remove_duplicate_products(self):
        all = self.env['product.template'].search([("active","=",True)],limit=500)
        for i in all:
           i.active=False


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    def remove_duplicate_account_move(self):
        rec_list = []
        dup_list = []
        for i in self:
            if i.ref not in rec_list:
                rec_list.append(i.ref)
            else:
                dup_list.append(i.id)
        duplicate = self.env['account.move'].search([('id', 'in', dup_list)]).unlink()






