# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class ReturnRequest(models.Model):
    _name = 'returns.bash'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Return Request'
    _rec_name = 'name'
    _order = 'id desc'

    partner_id = fields.Many2one("res.partner", string="Customer Name")
    branch_id = fields.Many2one("res.branch", string="Branch", default=lambda self: self.env.user.branch_id)
    contact_person_id = fields.Many2one("res.partner", string="Contact Person",
                                        domain="[('id', 'child_of',partner_id)]")
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user.id)
    address = fields.Char(string="Comments")
    date = fields.Datetime(string="Date", default=lambda self: fields.Datetime.now())
    net_total = fields.Integer("Net Total", compute="compute_total_invoice")
    request_lines = fields.One2many("request.line", "request_order_id")
    state = fields.Selection(
        [('user', 'User'), ('manager', 'Manager'), ('director', 'Director'), ('approved', 'Approved'),
         ('done', 'Validated'),
         ('rejected', 'Rejected')], string="State", readonly=True, default="user", tracking=1)
    is_check_qty = fields.Boolean(default=False, compute='compute_check_quantity')
    is_sent_for_second_approval = fields.Boolean(default=False)
    is_second_approved = fields.Boolean(default=False)
    dest_location_id = fields.Many2one('stock.location')
    invoice_id = fields.Many2one('account.move')
    picking_id = fields.Many2one('stock.picking')
    select_invoice_id = fields.Many2one('account.move')
    invoice_ids = fields.Many2many('account.move', compute='onchange_get_invoices')
    name = fields.Char('Return Request', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))

    def action_assign_branch(self):
        object = self.env['return.bash'].search([])
        for rec in object:
            rec.branch_id = rec.user_id.branch_id.id

    @api.onchange('select_invoice_id')
    def onchange_invoice_id(self):
        for line in self.request_lines:
            line.unlink()

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('return.bash.sequence') or _('New')
        result = super(ReturnRequest, self).create(vals)
        return result

    @api.depends('partner_id')
    def onchange_get_invoices(self):
        invoices = self.env['account.move'].search(
            [('partner_id', '=', self.partner_id.id), ('move_type', '=', 'out_invoice')])
        self.invoice_ids = invoices.ids

    def action_add_products(self):
        vals_list = []
        for rec in self.select_invoice_id.invoice_line_ids:
            if rec.product_id.type == 'product':
                if rec.product_id.active == False:
                    new = self.env['product.product'].search(
                        [('system_code', '=', int(float(rec.product_id.system_code)))])
                    vals_list.append([0, 0, {
                        'invoice_id': self.select_invoice_id.id,
                        'product_id': new.id,
                    }])
                else:
                    # product_list.append(rec.product_id.id)
                    vals_list.append([0, 0, {
                        'invoice_id': self.select_invoice_id.id,
                        'product_id': rec.product_id.id,
                    }])
        self.request_lines = vals_list

    # @api.depends('request_lines')
    def compute_check_quantity(self):
        if self.request_lines:
            if self.is_second_approved:
                self.is_check_qty = False
            else:
                is_check = False
                for rec in self.request_lines:
                    if rec.return_quantity != rec.recieved_qty:
                        is_check = True
                        # self.is_check_qty = False
                    # elif self.is_second_approved == True:
                    #     is_check = False
                # print('----------------------',is_check)
                if not is_check:
                    self.is_check_qty = False
                else:
                    self.is_check_qty = True
        else:
            self.is_check_qty = False

    def action_second_approval_from_manager(self):
        self.state = 'manager'
        self.is_sent_for_second_approval = True

    def action_approve(self):
        self.state = 'approved'

    def action_reject(self):
        self.state = 'rejected'

    def action_manager_approval(self):
        if self.is_sent_for_second_approval:
            self.is_second_approved = True
            self.state = 'director'
        else:
            self.state = 'director'

    def action_draft(self):
        self.state = 'user'

    def action_validate(self):
        print(self.is_check_qty)
        if self.is_check_qty == False:
            invoices_list = []
            for rec in self.request_lines:
                invoices_list.append(rec.invoice_id.id)
            products_list = []
            invoices_list = list(dict.fromkeys(invoices_list))
            for inv in invoices_list:
                for line in self.request_lines:
                    if line.invoice_id.id == inv:
                        products_list.append(line.product_id.id)
            self.create_delivery(invoices_list)
            self.create_invoice(invoices_list)
            self.state = 'done'
        else:
            raise UserError("Please Get Approval From Manager.")

    def create_invoice(self, invoices_list):
        record = self.env['account.account'].search([])[0]
        invoices = self.env['account.move'].browse(invoices_list)
        for rec in invoices:
            ref = ''
            lines = self.env['request.line'].search([('invoice_id', '=', rec.id), ('request_order_id', '=', self.id)])
            line_vals = []
            for line in lines:
                if line.invoice_id.name == rec.name:
                    line_vals.append((0, 0, {
                        'product_id': line.product_id.id,
                        'price_unit': line.unit_price,
                        'quantity': line.recieved_qty,
                        'discount': line.discount_qty,
                        'account_id': record.id
                    }))
                    ref = line.invoice_id.name
                    sale_order = line.invoice_id.invoice_origin
                line_vals.append(line_vals)
            inv = self.env['account.move'].search([('name', '=', ref)])
            order = self.env['sale.order'].search([('name', '=', sale_order)])
            vals = {
                'partner_id': self.partner_id.id,
                'invoice_date': datetime.today().date(),
                'move_type': 'out_refund',
                'invoice_line_ids': line_vals,
                'state': 'draft',
                'invoice_origin': order.name,
                'partner_shipping_id': order.partner_invoice_id.id,
                'reversed_entry_id': inv.id,
                'ref': _("Reversal of %s", ref)
            }
            move = self.env['account.move'].create(vals)
            move.action_post()

            self.invoice_id = move.id
            print("Invoice Generated!!!!!!")

    def create_delivery(self, invoices_list):
        picking_incoming = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)
        invoices = self.env['account.move'].browse(invoices_list)
        for rec in invoices:
            request_lines = self.env['request.line'].search(
                [('invoice_id', '=', rec.id), ('request_order_id', '=', self.id)])
            line_vals = []
            for line in request_lines:
                sale_order = line.invoice_id.invoice_origin
                if not sale_order:
                    sale_order = line.invoice_id.account_link
                delivery = self.env['stock.picking'].search([('origin', '=', sale_order)])
                if not delivery:
                    delivery = self.env['stock.picking'].search([('stock_link', '=', sale_order)])
                # print('Dell',delivery)
                if len(delivery) > 1:
                    delivery = delivery[0]
                sale_order = self.env['procurement.group'].search([('name', '=', sale_order)])
                if line.invoice_id.name == rec.name:
                    line_vals.append((0, 0, {
                        'product_id': line.product_id.id,
                        'name': 'Transfer In',
                        'product_uom': line.product_id.uom_id.id,
                        'location_id': delivery.location_dest_id.id,
                        'location_dest_id': self.dest_location_id.id,
                        'product_uom_qty': line.recieved_qty,
                        'quantity_done': line.recieved_qty,
                        'group_id': sale_order.id
                    }))
            new_picking = delivery.copy({
                'move_lines': [],
                'picking_type_id': picking_incoming.id,
                'state': 'done',
                'origin': _("Return of %s", delivery.name),
                'location_id': delivery.location_dest_id.id,
                'location_dest_id': self.dest_location_id.id,
                'group_id': sale_order.id
            })
            new_picking.write({
                'move_lines': line_vals,
            })
            new_picking.action_confirm()
            new_picking.button_validate()
            self.picking_id = new_picking.id
            return new_picking

    def action_confirmed(self):
        for i in self:
            i.state = 'manager'

    def action_done(self):
        for i in self:
            i.state = 'director'

    @api.depends("request_lines.total")
    def compute_total_invoice(self):
        total = 0
        for i in self.request_lines:
            total = total + i.total
        self.update({
            'net_total': total})


class ReturnRequested(models.Model):
    _name = 'request.line'
    _description = 'Return Request Line'

    request_order_id = fields.Many2one("returns.bash")
    invoice_date = fields.Date("Invoice Date", readonly=True, related='invoice_id.invoice_date')
    invoice_id = fields.Many2one("account.move")
    product_id = fields.Many2one("product.product", string="Item Description")
    uom_id = fields.Many2one("uom.uom", related='product_id.uom_id')
    art = fields.Char("Art", related='product_id.article_no')
    sold_quantity = fields.Float("Sold Qty", compute='compute_sold_quantity')
    previous_return_quantity = fields.Float("Previous Return Qty")
    return_quantity = fields.Float("Return Qty")
    discount_qty = fields.Float("Discount")
    unit_price = fields.Float("Unit Price")
    total = fields.Float("Total", compute='compute_total')
    reason_of_return = fields.Char("Reason Of Return")
    finish_no = fields.Char('Finish No', related='product_id.finish_no')
    recieved_qty = fields.Float('Received Qty')
    sqm_box = fields.Float('SQM/Box', related='product_id.sqm_box')
    total_sqm = fields.Float(string="Total Box", compute='_compute_product_uom_qty')

    def unlink(self):
        # print('Hello')
        for rec in self:
            if rec.request_order_id.state not in ('user'):
                raise UserError(
                    _('You can not delete this Return in this state.'))
        return super(ReturnRequested, self).unlink()

    @api.depends('return_quantity')
    def _compute_product_uom_qty(self):
        for rec in self:
            rec.total_sqm = rec.return_quantity / (rec.sqm_box or 1)

    # invoice_id = fields.Many2one('account.move')
    state = fields.Selection(
        [('user', 'User'), ('manager', 'Manager'), ('director', 'Director'), ('approved', 'Approved'),
         ('done', 'Validate'),
         ('rejected', 'Rejected')], string="State", readonly=True, default="user", related='request_order_id.state')

    @api.onchange('return_quantity')
    def verify_return_quantity(self):
        for rec in self:
            if rec.return_quantity:
                sale_order = rec.invoice_id.invoice_origin
                if not sale_order:
                    sale_order = rec.invoice_id.account_link
                sale_id = self.env['sale.order'].search([('name', '=', sale_order)])
                picking_incoming = self.env['stock.picking.type'].search([('code', '=', 'incoming')], limit=1)
                deliveries = self.env['stock.picking'].search([('partner_id', '=', rec.request_order_id.partner_id.id),
                                                               ('picking_type_id', '=', picking_incoming.id),
                                                               ('sale_id', '=', sale_id.id)])
                if not deliveries:
                    deliveries = self.env['stock.picking'].search(
                        [('partner_id', '=', rec.request_order_id.partner_id.id),
                         ('picking_type_id', '=', picking_incoming.id),
                         ('stock_link', '=', sale_order)])
                # print('del', deliveries)
                delivered_quantity = 0
                if deliveries:
                    for delivery in deliveries:
                        for line in delivery.move_ids_without_package:
                            if line.product_id.uom_id.name == 'BOX':
                                delivered_quantity = delivered_quantity + (line.quantity_done * rec.product_id.sqm_box)
                                # delivered_quantity = delivered_quantity + line.quantity_done
                            else:
                                # delivered_quantity = delivered_quantity + (line.quantity_done * rec.product_id.sqm_box)
                                delivered_quantity = delivered_quantity + line.quantity_done
                    rec.previous_return_quantity = delivered_quantity
                    total_returned = rec.previous_return_quantity + rec.return_quantity
                    if total_returned > rec.sold_quantity:
                        raise UserError('Sold Quantity is Already Returned')

    @api.onchange('return_quantity')
    def compute_total(self):
        for rec in self:
            rec.total = ((rec.return_quantity * rec.unit_price) * (rec.discount_qty/100)) - (rec.return_quantity * rec.unit_price)

    @api.onchange('product_id')
    def compute_sold_quantity(self):
        for rec in self:
            qty = ''
            price_unit = ''
            discount = ''
            for line in rec.invoice_id.invoice_line_ids:
                if line.product_id.type == 'product':
                    if not line.product_id.active:
                        new = self.env['product.product'].search(
                            [('system_code', '=', int(float(line.product_id.system_code)))])
                        if new.id == rec.product_id.id:
                            if line.product_id.uom_id.name == 'BOX':
                                qty = line.quantity * rec.product_id.sqm_box
                                price_unit = line.price_unit / rec.product_id.sqm_box
                            else:
                                qty = line.quantity
                                price_unit = line.price_unit
                            discount = line.discount
                    else:
                        if line.product_id.id == rec.product_id.id:
                            qty = line.quantity
                            price_unit = line.price_unit
                            discount = line.discount
            rec.sold_quantity = qty
            rec.unit_price = price_unit
            rec.discount_qty = discount

    @api.onchange('invoice_id')
    def onchange_get_invoices(self):
        invoices = self.env['account.move'].search(
            [('partner_id', '=', self.request_order_id.partner_id.id), ('move_type', '=', 'out_invoice')])
        self.product_id = ''
        return {'domain': {'invoice_id': [('id', 'in', invoices.ids)]}}

    @api.onchange('invoice_id')
    def onchange_get_products(self):
        product_list = []
        for rec in self.invoice_id.invoice_line_ids:
            if rec.product_id.type == 'product':
                # print(rec.product_id.active)
                if rec.product_id.active == False:
                    new = self.env['product.product'].search(
                        [('system_code', '=', int(float(rec.product_id.system_code)))])
                    product_list.append(new.id)
                else:
                    product_list.append(rec.product_id.id)
        return {'domain': {'product_id': [('id', 'in', product_list)]}}
