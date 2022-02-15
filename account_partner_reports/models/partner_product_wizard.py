from odoo import api, fields, models, _


class PartnerProductWizard(models.TransientModel):
    _name = "partner.product.wizard"
    _description = "Partner Product Wizard Report"

    date_to = fields.Date(string='Date To')
    date_from = fields.Date(string='Date From')
    partner_id = fields.Many2one('res.partner', string='Partner')

    def partner_product_report_action(self):
        data = {
            'form': self.read()[0],
        }
        return self.env.ref('account_partner_reports.partner_product_wizard_report').report_action(self, data=data)