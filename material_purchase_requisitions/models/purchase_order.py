# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'
    
    custom_requisition_id = fields.Many2one(
        'material.purchase.requisition',
        string='Requisitions',
        copy=False
    )
    # custom_requisition_id
    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        if self.custom_requisition_id:
            self.custom_requisition_id.write({
                'picking_type_id': self.picking_type_id.id
            })

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'
    
    custom_requisition_line_id = fields.Many2one(
        'material.purchase.requisition.line',
        string='Requisitions Line',
        copy=False
    )
