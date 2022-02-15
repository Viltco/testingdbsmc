# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    do_link = fields.Char()
    invoice_link = fields.Char("Invoice link")
    cus_invoice_link = fields.Many2one("account.move", "Invoice")
    qty_invoice_link = fields.Integer("Sale Order QTY")
    bol_invoice_linked=fields.Boolean("Invoice linked")
    bol_do_linked = fields.Boolean("DO linked")
    cus_do_link = fields.Many2one("stock.picking", "Stock Picking")
    qty_do_link = fields.Integer("DO QTY")

    def _compute_the_do_link(self):
        rec = self.env["sale.order"].search([("bol_do_linked",'=',False)],limit=2000)
        for i in rec:
            obj = self.env["stock.picking"].search([("carrier_tracking_ref", '=', i.do_link)], limit=1)
            if obj:

                i.bol_do_linked=True
                i.cus_do_link = obj.id
                i.qty_do_link = len(self.env["stock.picking"].search([("carrier_tracking_ref", '=', i.do_link)]))

    def smart_delivery_button(self):
        return {
            'name': _('Picking'),
            'view_mode': 'tree,form',
            'res_model': 'stock.picking',
            'domain': [('carrier_tracking_ref', '=', self.do_link)],
            'type': 'ir.actions.act_window',
        }

    def _compute_the_invoice_link(self):
        rec = self.env["sale.order"].search([("bol_invoice_linked", '=', False)],limit=2000)
        for i in rec:
            print(i.name)
            obj = self.env["account.move"].search([("ref", '=', i.invoice_link)],limit=1)
            if obj:
                i.bol_invoice_linked=True
                i.qty_invoice_link=len(self.env["account.move"].search([("ref", '=', i.invoice_link)]))
                i.cus_invoice_link = obj.id
                print(i.cus_invoice_link)
        print("not found")

    def smart_invoice_button(self):
        return {
            'name': _('Invoices'),
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('ref', '=', self.invoice_link)],
            'type': 'ir.actions.act_window',
        }


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    purchase_link = fields.Char("Receipt Link")
    bill_link = fields.Char("Bill Link")
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To')


class AccountMoveInh(models.Model):
    _inherit = 'account.move'

    account_link = fields.Char()
    purchase_link = fields.Char("Purchase Order")
    cus_so_link = fields.Many2one("sale.order", "Sale Order")
    qty_account_link = fields.Integer("Sale Order QTY")
    bol_sale_order_linked = fields.Boolean("Sale Order Linked")

    def _compute_the_invoice_link(self):
        rec = self.env["account.move"].search([("bol_sale_order_linked", '=', False)],limit=2000)
        for i in rec:
            print(i.name)
            obj = self.env["sale.order"].search([("invoice_link", '=', i.ref)],limit=1)
            if obj:
                i.cus_so_link = obj.id
                i.qty_account_link=len(self.env["sale.order"].search([("invoice_link", '=', i.ref)]))

    def smart_sale_order_button(self):
        return {
            'name': _('Sale order'),
            'view_mode': 'tree,form',
            'res_model': 'sale.order',
            'domain': [('invoice_link', '=', self.ref)],
            'type': 'ir.actions.act_window',
        }


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    stock_link = fields.Char()
    purchase_link = fields.Char("Purchase Order")

    cus_do_link = fields.Many2one("sale.order", "Sale Order")
    qty_do_link = fields.Integer("SO QTY")

    def _compute_the_do_link(self):
        for i in self:
            obj = self.env["sale.order"].search([("do_link", '=', i.carrier_tracking_ref)], limit=1)
            i.cus_do_link = obj.id
            i.qty_do_link = len(self.env["sale.order"].search([("do_link", '=', i.carrier_tracking_ref)]))


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    payment_link = fields.Char()
