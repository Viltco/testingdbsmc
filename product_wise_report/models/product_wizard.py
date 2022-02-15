from odoo import api, fields, models, _


class ProductWizard(models.TransientModel):
    _name = "product.wizard"
    _description = "Product Wizard"

    partner_id = fields.Many2one('res.partner', string='Partner')

    def product_report_action(self):
        data = {
            'form': self.read()[0],
        }
        return self.env.ref('product_wise_report.product_report_repo').report_action(self,data=data)