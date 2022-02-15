# -*- coding: utf-8 -*-

from odoo import models, fields, api


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    gross_total = fields.Float('Gross Total', compute='_compute_gross_total')
    line_discount = fields.Float('Discount', compute='get_discount')
    second_discount = fields.Float('Second Discount', compute='get_discount')

    @api.depends('order_line.price_unit', 'order_line.product_uom_qty')
    def _compute_gross_total(self):
        total = 0
        for line in self.order_line:
            total = total + line.product_uom_qty * line.price_unit
        self.gross_total = total

    @api.depends('global_order_discount', 'global_discount_type', 'order_line.discount')
    def get_discount(self):
        untaxed = 0
        taxed = 0
        for rec in self:
            for line in rec.order_line:
                untaxed = untaxed + (line.product_uom_qty * line.price_unit)
                taxed = taxed + line.price_subtotal

            rec.line_discount = abs(taxed - untaxed)
            if rec.global_discount_type == 'fixed':
                rec.second_discount = rec.global_order_discount
            if rec.global_discount_type == 'percent':
                per = rec.amount_total * (rec.global_order_discount / 100)
                rec.second_discount = per


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    line_discount = fields.Float('Discount', compute='get_discount')
    second_discount = fields.Float('Second Discount', compute='get_discount')

    @api.depends('global_order_discount', 'global_discount_type')
    def get_discount(self):
        untaxed = 0
        taxed = 0
        for rec in self:
            for line in rec.invoice_line_ids:
                untaxed = untaxed + (line.quantity * line.price_unit)
                taxed = taxed + line.price_subtotal

            rec.line_discount = abs(taxed - untaxed)
            if rec.global_discount_type == 'fixed':
                rec.second_discount = rec.global_order_discount
            if rec.global_discount_type == 'percent':
                per = rec.amount_total * (rec.global_order_discount / 100)
                rec.second_discount = per
