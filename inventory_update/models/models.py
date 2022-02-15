# -*- coding: utf-8 -*-

from odoo import models, fields, api


class InventoryUpdate(models.TransientModel):
    _name = 'inventory.update'
    _description = 'Inventory Update'

    product_ids = fields.Many2many('product.product')
    location_id = fields.Many2one('stock.location')

    def action_update_products(self):
        for rec in self.product_ids:
            quant_vals = {
                'product_id': rec.id,
                'product_uom_id': rec.uom_id.id,
                'location_id': self.location_id.id,
                'quantity': 100,
                'reserved_quantity': 0,
            }
            self.env['stock.quant'].sudo().create(quant_vals)
