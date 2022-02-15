# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ResPartnerInh(models.Model):
    _inherit = 'res.partner'

    # customer_code = fields.Char('Customer Code', copy=False, index=True)
    #
    @api.constrains('customer_code')
    def check_code(self):
        if self.customer_code:
            code = self.env['res.partner'].search([('customer_code', '=', self.customer_code)])
            if len(code) > 1:
                raise UserError('User Already Exist')

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s : %s : %s' % (rec.customer_code, rec.name, str(rec.total_due))))
        return res

    # @api.model
    # def create(self, vals):
    #     if vals.get('customer_code', _('New')) == _('New'):
    #         vals['customer_code'] = self.env['ir.sequence'].next_by_code('res.partner.sequence') or _('New')
    #     branch = self.env['res.branch'].browse([vals.get('branch_id')])
    #     vals['customer_code'] = str(1) + '-' + str(self.env.user.agent_code) + '-' + str(branch.branch_code) + vals['customer_code']
    #     result = super(ResPartnerInh, self).create(vals)
    #     return result
