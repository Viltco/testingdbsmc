# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ResUserInh(models.Model):
    _inherit = 'res.users'

    manager_id = fields.Many2one('res.users')

    
    

class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    manager_id = fields.Many2one('res.users', related='user_id.manager_id')
