# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import UserError


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    user_picking_type = fields.Selection([('deliver_at_dha', 'Deliver At DHA S.R'),
                                          ('deliver_at_clg', 'Deliver At CLG RD S.R'),
                                          ('deliver_at_ichra', 'Deliver At Ichra'),
                                          ('deliver_at_site', 'Deliver At Site'),
                                          ('delivery_from_rwnd', 'Delivery From RWND'),
                                          ('hold_material', 'Hold Material'),
                                          ('none', '')],
                                         string='User Picking Type', default='none', tracking=True)

    def action_confirm(self):
        res = super(SaleOrderInherit, self).action_confirm()
        self.picking_ids.write({
            'user_picking_type': self.user_picking_type if self.user_picking_type else '',
            'comments': self.comments,
        })
        return res

    def create_invoices(self):
        res = super(SaleOrderInherit, self).action_create_invoice()


class StockPickingInherit(models.Model):
    _inherit = 'stock.picking'

    comments = fields.Char(string='Comments', tracking=True, related='sale_id.comments')

    user_picking_type = fields.Selection([('deliver_at_dha', 'Deliver At DHA S.R'),
                                          ('deliver_at_clg', 'Deliver At CLG RD S.R'),
                                          ('deliver_at_ichra', 'Deliver At Ichra'),
                                          ('deliver_at_site', 'Deliver At Site'),
                                          ('delivery_from_rwnd', 'Delivery From RWND'),
                                          ('hold_material', 'Hold Material'),
                                          ('none', '')],
                                         string='User Picking Type', default='none', tracking=True, related='sale_id.user_picking_type')


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    comments = fields.Char(string='Comments', tracking=True)

    user_picking_type = fields.Selection([('deliver_at_dha', 'Deliver At DHA S.R'),
                                          ('deliver_at_clg', 'Deliver At CLG RD S.R'),
                                          ('deliver_at_ichra', 'Deliver At Ichra'),
                                          ('deliver_at_site', 'Deliver At Site'),
                                          ('delivery_from_rwnd', 'Delivery From RWND'),
                                          ('hold_material', 'Hold Material'),
                                          ('none', '')],
                                         string='User Picking Type', default='none', tracking=True)


class SaleAdvancePaymentInh(models.TransientModel):
    _inherit = 'sale.advance.payment.inv'

    def create_invoices(self):
        rec = super(SaleAdvancePaymentInh, self).create_invoices()
        print(rec['context']['default_invoice_origin'])
        order = self.env['sale.order'].search(
            [('name', '=', rec['context']['default_invoice_origin'][0])])
        invoices = self.env['account.move'].search([('invoice_origin', '=', rec['context']['default_invoice_origin'][0])])
        invoices.write({
            'user_picking_type': order.user_picking_type,
            'comments': order.comments,
        })




