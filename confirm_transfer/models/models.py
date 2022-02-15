# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    is_created = fields.Boolean()

    def create_stock_picking(self):
        obj=self.env['stock.picking'].search([('is_created','=',False),('state','=','draft')],limit=100)
        for rec in obj:
            rec.sudo().action_confirm()
            rec.sudo().button_validate()
            rec.is_created = True

