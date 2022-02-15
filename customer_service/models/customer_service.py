# -*- coding: utf-8 -*-


import datetime
from lxml import etree
from odoo import models, fields, api, _
from datetime import timedelta
from odoo.exceptions import UserError, ValidationError
from datetime import datetime
from odoo.tools import float_compare


class CustomerService(models.Model):
    _name = 'customer.service'
    _description = 'Customer Service'
    _rec_name = 'name'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string='Customer Service')


class HelpdeskTicketInherit(models.Model):
    _inherit = 'helpdesk.ticket'

    sr_no = fields.Char(string='SR #')
    brand = fields.Many2one('customer.service', string='Brand')
    sale_agent = fields.Many2one('res.partner', string='Sale Agent')
    service_charge = fields.Float(string='Service Charges')
    date_service = fields.Date(string='Date')
    phone = fields.Char(related='partner_id.phone', string='Contact#')
    street = fields.Char(related='partner_id.street', string='Address')
    street2 = fields.Char(related='partner_id.street2', string='Address')
    city = fields.Char(related='partner_id.city', string='Address')
    state_id = fields.Many2one('res.country.state', related='partner_id.state_id', string='Address')
    zip = fields.Char(related='partner_id.zip', string='Address')
    country_id = fields.Many2one('res.country', related='partner_id.country_id', string='Address')
    problem = fields.Text(string='Problems')
    article_no = fields.Char(string='Article')
    serial_number = fields.Text(string='Serial Numbers')
    warranty = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Warranty')
    client_confirmation = fields.Selection([
        ('yes', 'Yes'),
        ('no', 'No'),
    ], string='Client Confirmation')

    @api.model
    def create(self, vals):
        sequence = self.env.ref('customer_service.customer_service_sr_no')
        vals['sr_no'] = sequence.next_by_id()
        rec = super(HelpdeskTicketInherit, self).create(vals)
        return rec
