# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api


class InvoiceReplica(models.Model):
    _name = 'invoice.replica'
    _rec_name = 'partner_id'

    partner_id = fields.Many2one('res.partner')
    currency_id = fields.Many2one('res.currency')
    journal_id = fields.Many2one('account.journal')
    branch_id = fields.Many2one('res.branch')
    invoice_user_id = fields.Many2one('res.users')
    invoice_date = fields.Date('Invoice Date')
    ref = fields.Char('Reference')
    invoice_link = fields.Char('Invoice Link')
    freight = fields.Char('Freight')
    is_created = fields.Boolean('Created')

    invoice_line_ids = fields.One2many('invoice.replica.line', 'move_id')

    def action_create_invoices(self):
        invoices = self.env['invoice.replica'].search([('is_created', '=', False)])
        for rec in invoices:
            line_vals = []
            for line in rec.invoice_line_ids:
                uom_id = self.env['uom.uom'].search([('name', '=', line.uom)], limit=1)
                line_vals.append((0, 0, {
                    'product_id': line.product_id.id,
                    'price_unit': line.price_unit,
                    'quantity': line.quantity,
                    'account_id': line.account_id.id,
                    'journal_id': line.journal_id.id,
                    'currency_id': line.currency_id.id,
                    'company_id': line.company_id.id,
                    'uom_id': uom_id.id,
                    'discount': line.discount,
                }))
            vals = {
                'partner_id': rec.partner_id.id,
                'journal_id': rec.journal_id.id,
                'branch_id': rec.branch_id.id,
                'currency_id': rec.currency_id.id,
                'invoice_date': rec.invoice_date,
                'move_type': 'out_invoice',
                'invoice_line_ids': line_vals,
                'freight': rec.freight,
                'account_link': rec.invoice_link,
                'ref': rec.ref,
                'state': 'draft',
            }
            move = self.env['account.move'].create(vals)
            rec.is_created = True
            print("Invoice Generated!!!!!!")


class InvoiceReplicaLine(models.Model):
    _name = 'invoice.replica.line'

    move_id = fields.Many2one('invoice.replica')
    uom = fields.Char('Uom')
    account_id = fields.Many2one('account.account')
    company_id = fields.Many2one('res.company')
    currency_id = fields.Many2one('res.currency')
    journal_id = fields.Many2one('account.journal')
    product_id = fields.Many2one('product.product')
    # invoice_date = fields.Datetime('Invoice Date')
    quantity = fields.Integer('Quantity')
    price_unit = fields.Float('Price')
    discount = fields.Float('Discount')