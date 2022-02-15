# -*- coding: utf-8 -*-

from odoo import models, fields, api,_


class AccountMove(models.Model):
    _inherit = 'account.move'

    return_so_ref = fields.Char("Return SO Ref")
    return_do_ref = fields.Char("Return DO Ref")
    return_inv_ref = fields.Char("Return Inv Ref")
    return_date = fields.Date("Return Date")


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    return_so_ref = fields.Char("Return SO Ref")
    return_do_ref = fields.Char("Return DO Ref")
    return_inv_ref = fields.Char("Return Inv Ref")
    return_date = fields.Date("Return Date")

