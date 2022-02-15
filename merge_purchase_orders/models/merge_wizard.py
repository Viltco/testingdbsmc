from odoo import models, fields
from odoo.exceptions import UserError


class MrpMergeWizard(models.TransientModel):
    _name = 'purchase.merge.wizard'

    picking_id = fields.Many2many('stock.picking')

    def merge_purchase_orders(self):
        selected_ids = self.env.context.get('active_ids', [])
        selected_records = self.env['stock.picking'].browse(selected_ids)
        line_vals = []
        names = []
        for record in selected_records:
            names.append(record.name)
            for line in record.move_ids_without_package:
                # if line.reserved_availability < line.product_uom_qty:
                    line_data = (0, 0, {
                        # 'picking_id': picking.id,
                        'product_id': line.bespoke_product_id.id,
                        'name': line.bespoke_product_id.name,
                        'product_uom': line.bespoke_product_id.uom_id.id,
                        'location_id': line.location_id.id,
                        'location_dest_id': line.location_dest_id.id,
                        'product_uom_qty': line.product_uom_qty,
                    })
                    line_vals.append(line_data)
        my_string = ','.join(names)
        # vals = {
        #     'company_id': self.env.user.company_id.id,
        #     'request_date': fields.Date.today(),
        #     'dest_location_id': selected_records[0].location_id.id,
        #     'requisition_line_ids': line_vals,
        #     'ref': my_string,
        # }
        return {
            'name': 'Requisition',
            'res_model': 'stock.picking',
            'views': [[False, "form"]],
            'type': 'ir.actions.act_window',
            'context': {'default_move_ids_without_package': line_vals,
                        'default_location_dest_id': selected_records[0].location_dest_id.id,
                        'default_request_date': fields.Date.today(),
                        'default_company_id': self.env.user.company_id.id}
        }


    # def merge_purchase_orders(self):
    #     total_list = []
    #     total_qty = 0
    #     names = []
    #     if len(self.purchase_id) > 1:
    #         # flag = True
    #         # for res in self.production_id:
    #             # if self.purchase_id[0].product_id.id == res.product_id.id and self.purchase_id[0].bom_id.id == res.bom_id.id:
    #             #     flag = True
    #             # else:
    #             #     flag = False
    #             #     raise UserError("Product and BOM Should be Same in All Manufacturing Orders")
    #         # if flag:
    #         for rec in self.purchase_id:
    #             if rec.state == 'draft':
    #                 # total_qty = total_qty + rec.product_qty
    #                 names.append(rec.name)
    #                 for line in rec.order_line:
    #                     # if total_list:
    #                     #     for i in total_list:
    #                     #         if i[2]['product_id'] == line.product_id.id:
    #                     #             i[2]['product_qty'] = i[2]['product_qty'] + line.product_qty
    #                     #         else:
    #                                 line_data = (0, 0, {
    #                                     'product_id': line.product_id.id,
    #                                     # 'forecast_availability': line.forecast_availability,
    #                                     'product_qty': line.product_qty,
    #                                     'product_uom': line.product_uom.id,
    #                                     # 'quantity_done': line.quantity_done,
    #                                     'name': line.name,
    #                                     'price_unit': line.price_unit,
    #                                     'unit_pricefc': line.unit_pricefc,
    #                                     'assessed_value': line.assessed_value,
    #                                     'date_planned': line.date_planned,
    #                                     # 'location_id': line.location_id.id,
    #                                     # 'location_dest_id': line.location_dest_id.id,
    #                                 })
    #                                 total_list.append(line_data)
    #                     # else:
    #                     #     line_data = (0, 0, {
    #                     #         'product_id': line.product_id.id,
    #                     #         # 'forecast_availability': line.forecast_availability,
    #                     #         'product_qty': line.product_qty,
    #                     #         'product_uom': line.product_uom.id,
    #                     #         # 'quantity_done': line.quantity_done,
    #                     #         'name': line.name,
    #                     #         'price_unit': line.price_unit,
    #                     #         # 'location_id': line.location_id.id,
    #                     #         # 'location_dest_id': line.location_dest_id.id,
    #                     #     })
    #                     #     total_list.append(line_data)
    #             else:
    #                 raise UserError("Manufacturing Order can be merge in Draft State")
    #         my_string = ','.join(names)
    #         header_data = {
    #             'partner_id': self.purchase_id[0].partner_id.id,
    #             's_for': 'import',
    #             'lc_account': self.purchase_id[0].lc_account.id,
    #             'fx_rate': self.purchase_id[0].fx_rate,
    #             'order_line': total_list,
    #             # 'ref': my_string,
    #         }
    #         mrp = self.env['purchase.order'].create(header_data)
    #         # if mrp:
    #         #     for i in self.production_id:
    #         #         i.action_cancel()
    # # else:
    # #     raise UserError("Cannot Merge Single Manufacturing Order")