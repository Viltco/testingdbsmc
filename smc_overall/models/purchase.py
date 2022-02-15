
from odoo import models, fields, api, _


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    status_ref = fields.Selection([
        ('in_production', 'In Production'),
        ('on_the_way', 'On the Way to Khi'),
        ('out_of_way', 'Out of way to Lhr'),
        ('arrived', 'Arrived'),
        ('custom', 'Custom'),
    ], string='Status Ref')

    @api.model
    def _default_picking_type(self):
        # return self._get_picking_type(self.env.context.get('company_id') or self.env.company.id)
        return False

    manual_status = fields.Char('Manual Status')
    picking_type_id = fields.Many2one('stock.picking.type', 'Deliver To', required=True)

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        self.picking_type_id = ''

    # @api.model
    # def _get_picking_type(self, company_id):
    #     print('--------------------------------------------------Hello')
    #     picking_type = self.env['stock.picking.type'].search(
    #         [('code', '=', 'incoming'), ('warehouse_id.company_id', '=', company_id)])
    #     if not picking_type:
    #         picking_type = self.env['stock.picking.type'].search(
    #             [('code', '=', 'incoming'), ('warehouse_id', '=', False)])
    #     return False