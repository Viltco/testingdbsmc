from odoo import models, api


class ProductReport(models.AbstractModel):
    _name = 'report.product_wise_report.product_report_temp'
    _description = 'Product Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        rec_model = self.env[model].browse(self.env.context.get('active_id'))
        products = self.env['product.supplierinfo'].search([('name', '=', rec_model.partner_id.id)])
        # for rec in products:
        #     for vendor in
        return {
            'doc': rec_model,
            'doc_model': 'product.wizard',
            'products': products,
        }
