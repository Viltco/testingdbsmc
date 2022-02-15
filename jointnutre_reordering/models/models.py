# -*- coding: utf-8 -*-
from datetime import datetime

from odoo import models, fields, api, _


class ProductTemplateInh(models.Model):
    _inherit = 'product.template'

    def action_check_products(self):
        products = self.env['product.template'].search([('nbr_reordering_rules', '>', 0)])
        for rec in products:
            if rec.nbr_reordering_rules > 0:
                quants = self.env['stock.quant'].search([('product_tmpl_id', '=', rec.id)])
                prd_resrv_qty = 0
                for rsrvqt in quants:
                    prd_resrv_qty = prd_resrv_qty + rsrvqt.reserved_quantity
                if (rec.qty_available - prd_resrv_qty) <= rec.reordering_min_qty:
                    qty = (rec.qty_available - prd_resrv_qty)
                    self.action_create_message(rec, qty)

    def action_create_message(self, rec, qty):
        act_type_xmlid = 'mail.mail_activity_data_todo'
        summary = 'Product Out of Stock'
        note = 'Product [' + rec.name + '] is Out of stock. Its current stock is ' + str(qty) + '.'
        if act_type_xmlid:
            activity_type = self.sudo().env.ref(act_type_xmlid)
        model_id = self.env['ir.model']._get(rec._name).id
        users = self.env['res.users'].search([])
        for user in users:
            if user.has_group('jointnutre_reordering.group_inventory_manager'):
                create_vals = {
                    'activity_type_id': activity_type.id,
                    'summary': summary or activity_type.summary,
                    'automated': True,
                    'note': note,
                    'date_deadline': datetime.today(),
                    'res_model_id': model_id,
                    'res_id': rec.id,
                    'user_id': user.id,
                }
                activities = self.env['mail.activity'].create(create_vals)
