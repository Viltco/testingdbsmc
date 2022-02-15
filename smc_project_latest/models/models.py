# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from itertools import groupby
from odoo.tools.float_utils import float_is_zero
from lxml import etree
from datetime import datetime, timedelta
import locale
import urllib

def _create_notification(self):
    act_type_xmlid = 'mail.mail_activity_data_todo'
    summary = 'Reserved DO Notification'
    note = '25 Days passed.In 5 days left, DO no: ' + self.name + ' will be unreserved Automatically.'
    if act_type_xmlid:
        activity_type = self.sudo().env.ref(act_type_xmlid)
    model_id = self.env['ir.model']._get(self._name).id
    create_vals = {
        'activity_type_id': activity_type.id,
        'summary': summary or activity_type.summary,
        'automated': True,
        'note': note,
        'date_deadline': datetime.today(),
        'res_model_id': model_id,
        'res_id': self.id,
        'user_id': self.sale_id.user_id.id,
    }
    activities = self.env['mail.activity'].create(create_vals)


class AccountPaymnetInh(models.Model):
    _inherit = 'account.payment'

    def action_post(self):
        rec = super(AccountPaymnetInh, self).action_post()
        self._create_notification()
        self.action_payment_sms_api()

    def action_payment_sms_api(self):
        user = '03334220752'
        password = '03334220752'
        sender = 'SMC'
        to = self.partner_id.mobile
        # locale.setlocale(locale.LC_ALL, '')
        # amnt = str(locale.currency(self.amount, grouping=True))
        msg = 'Dear Customer,\nThank you for the payment against your Sale Order #: ' + self.ref + ' Amount Rs' + str(self.amount) + '\nBest Regards,\nSMC Team'
        params = urllib.parse.urlencode(
            {'Username': user, 'Password': password, 'To': to, 'From': sender, 'Message': msg})
        url = "http://my.ezeee.pk/sendsms_url.html?send_sms&%s" % params
        f = urllib.request.urlopen(url)
        ret = f.read().decode('utf-8')
        if ret:
            print("The message was sent successfully")
        else:
            print("There was an error Parameters")
            print("Error number is [%s]" % ret)

    def _create_notification(self):
        act_type_xmlid = 'mail.mail_activity_data_todo'
        summary = 'Payment Transaction'
        note = 'Payment Processed at Branch : ' + self.branch_id.name + '.'
        ceo = self.env['res.users'].search([('login', '=', 'umer.shahid@smcgroup.pk')])
        if act_type_xmlid:
            activity_type = self.sudo().env.ref(act_type_xmlid)
        model_id = self.env['ir.model']._get(self._name).id
        create_vals = {
            'activity_type_id': activity_type.id,
            'summary': summary or activity_type.summary,
            'automated': True,
            'note': note,
            'date_deadline': datetime.today(),
            'res_model_id': model_id,
            'res_id': self.id,
            'user_id': ceo.id,
        }
        activities = self.env['mail.activity'].create(create_vals)


class SMC(models.Model):
    _inherit = 'product.template'

    sale_discontinued = fields.Boolean("Sales Discontinued Products", compute="_compute_on_hand")
    # hs_code = fields.Char('Hs Code')

    def _compute_on_hand(self):
        for i in self:
            if i.type == 'product':
                if not i.sale_ok or not i.purchase_ok:
                    i.sale_discontinued = True
                else:
                    i.sale_discontinued = False
            else:
                i.sale_discontinued = False

            #     if i.qty_available <= 0 and i.purchase_ok == False:
            #         i.sale_discontinued = True
            #         i.sale_ok = False
            #     elif i.qty_available > 0 and i.purchase_ok == False:
            #         i.sale_discontinued = True
            #         i.sale_ok = True
            #     else:
            #         i.sale_ok = True
            #         i.sale_discontinued = False
            # else:
            #     i.sale_discontinued = False


class PurchaseOrderInh(models.Model):
    _inherit = 'purchase.order'

    def action_view_invoices(self):
        """This function returns an action that display existing vendor bills of
        given purchase order ids. When only one found, show the vendor bill
        immediately.
        """
        invoices = self.env['account.move'].search([('invoice_origin', '=', self.name)])
        if not invoices:
            # Invoice_ids may be filtered depending on the user. To ensure we get all
            # invoices related to the purchase order, we read them in sudo to fill the
            # cache.
            self.sudo()._read(['invoice_ids'])
            invoices = self.invoice_ids

        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        # choose the view_mode accordingly
        if len(invoices) > 1:
            result['domain'] = [('id', 'in', invoices.ids)]
        elif len(invoices) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = invoices.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    def action_create_invoice(self):
        """Create the invoice associated to the PO.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        # 1) Prepare invoice vals and clean-up the section lines
        invoice_vals_list = []
        for order in self:
            if order.invoice_status != 'to invoice':
                continue

            order = order.with_company(order.company_id)
            pending_section = None
            # Invoice values.
            invoice_vals = order._prepare_invoice()
            # Invoice line values (keep only necessary sections).
            for line in order.order_line:
                if line.display_type == 'line_section':
                    pending_section = line
                    continue
                if not float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    if pending_section:
                        invoice_vals['invoice_line_ids'].append((0, 0, pending_section._prepare_account_move_line()))
                        pending_section = None
                    invoice_vals['invoice_line_ids'].append((0, 0, line._prepare_account_move_line()))
            invoice_vals_list.append(invoice_vals)

        if not invoice_vals_list:
            raise UserError(
                _('There is no invoiceable line. If a product has a control policy based on received quantity, please make sure that a quantity has been received.'))

        # 2) group by (company_id, partner_id, currency_id) for batch creation
        new_invoice_vals_list = []
        for grouping_keys, invoices in groupby(invoice_vals_list, key=lambda x: (
        x.get('company_id'), x.get('partner_id'), x.get('currency_id'))):
            origins = set()
            payment_refs = set()
            refs = set()
            ref_invoice_vals = None
            for invoice_vals in invoices:
                if not ref_invoice_vals:
                    ref_invoice_vals = invoice_vals
                else:
                    ref_invoice_vals['invoice_line_ids'] += invoice_vals['invoice_line_ids']
                origins.add(invoice_vals['invoice_origin'])
                payment_refs.add(invoice_vals['payment_reference'])
                refs.add(invoice_vals['ref'])
            ref_invoice_vals.update({
                'ref': ', '.join(refs)[:2000],
                'invoice_origin': ', '.join(origins),
                'payment_reference': len(payment_refs) == 1 and payment_refs.pop() or False,
            })
            new_invoice_vals_list.append(ref_invoice_vals)
        invoice_vals_list = new_invoice_vals_list

        # 3) Create invoices.
        moves = self.env['account.move']
        AccountMove = self.env['account.move'].with_context(default_move_type='in_invoice')
        for vals in invoice_vals_list:
            moves |= AccountMove.with_company(vals['company_id']).create(vals)
        # 4) Some moves might actually be refunds: convert them if the total amount is negative
        # We do this after the moves have been created since we need taxes, etc. to know if the total
        # is actually negative or not
        moves.filtered(
            lambda m: m.currency_id.round(m.amount_total) < 0).action_switch_invoice_into_refund_credit_note()
        return self.action_view_invoices()


class in_invoicing(models.Model):
    _inherit = 'account.move'

    delivery_order = fields.Many2one('stock.picking', compute='_compute_global')
    create_user = fields.Many2one('res.users', string='User', compute="compute_self_id")
    sale_origin = fields.Many2one('sale.order', compute='_compute_sale_origin')
    purchase_origin = fields.Many2one('purchase.order', compute='_compute_purchase_origin')

    def action_post(self):
        rec = super(in_invoicing, self).action_post()
        if self.branch_id:
            self._create_notification()

    def _create_due_date_notification(self):
        bills = self.env['account.move'].search([('move_type', '=', 'in_invoice'), ('state', '=', 'posted'), ('invoice_date_due', '>=', (datetime.today().date())),('invoice_date_due', '<=', (datetime.today().date() + timedelta(days=30)))])
        print(bills)
        for bill in bills:
            # if bill.invoice_date_due <= (datetime.today().date() + timedelta(days=30)):
            act_type_xmlid = 'mail.mail_activity_data_todo'
            summary = 'Bill Due Date Arrived'
            note = 'Due Date of Bill No: ' + bill.name + ' is ' + str(bill.invoice_date_due)
            users = self.env['res.users'].search([])
            if act_type_xmlid:
                activity_type = self.sudo().env.ref(act_type_xmlid)
            model_id = self.env['ir.model']._get(bill._name).id
            for user in users:
                if user.has_group('account.group_account_manager'):
                    create_vals = {
                        'activity_type_id': activity_type.id,
                        'summary': summary or activity_type.summary,
                        'automated': True,
                        'note': note,
                        'date_deadline': datetime.today(),
                        'res_model_id': model_id,
                        'res_id': bill.id,
                        'user_id': user.id,
                    }
                    activities = self.env['mail.activity'].create(create_vals)

    def _create_notification(self):
        act_type_xmlid = 'mail.mail_activity_data_todo'
        summary = 'Transaction Posted'
        note = 'Transaction Processed at Branch : ' + self.branch_id.name + '.'
        ceo = self.env['res.users'].search([('login', '=', 'umer.shahid@smcgroup.pk')])
        if act_type_xmlid:
            activity_type = self.sudo().env.ref(act_type_xmlid)
        model_id = self.env['ir.model']._get(self._name).id
        create_vals = {
            'activity_type_id': activity_type.id,
            'summary': summary or activity_type.summary,
            'automated': True,
            'note': note,
            'date_deadline': datetime.today(),
            'res_model_id': model_id,
            'res_id': self.id,
            'user_id': ceo.id,
        }
        activities = self.env['mail.activity'].create(create_vals)

    def _compute_purchase_origin(self):
        for i in self:
            record = self.env['purchase.order'].search([('name', '=', i.invoice_origin)], limit=1)
            i.purchase_origin = record.id

    def _compute_sale_origin(self):
        for i in self:
            record = self.env['sale.order'].search([('name', '=', i.invoice_origin)], limit=1)
            i.sale_origin = record.id

    def compute_self_id(self):
        for i in self:
            i.create_user = i.env.uid

    def _compute_global(self):
        for i in self:
            record = self.env['stock.picking'].search([('origin', '=', i.invoice_origin)], limit=1)
            i.delivery_order = record.id


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('manager', 'Discount Approval from Manager'),
        ('ceo', 'Discount Approval from CEO'),
        ('confirmed', 'Approved'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
    ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

    max_discount = fields.Float(string='Max Disccount', compute='compute_max_disccount', default=0, store=True)
    allowed_discount = fields.Float(string='Allowed Disccount', related='create_user.allowed_discount')
    create_user = fields.Many2one('res.users', string='User', default=lambda self: self.env.user.id,
                                  compute='compute_self_id')
    is_approved_by_manager_discount = fields.Selection([
        ('none', 'None'),
        ('manager', 'Discount Approved By Manager'), ], string='Discount Approved By Manager', default='none')
    is_approved_by_ceo_discount = fields.Selection([
        ('none', 'None'),
        ('ceo', 'Discount Approved By CEO'), ], string='Discount Approved By CEO', default='none')

    def action_manager_approve(self):
        for sale_order in self:
            if sale_order.max_discount > sale_order.allowed_discount:
                raise UserError(
                    _('Your discount limit is lesser then allowed discount.Click on "Ask for Approval" for Approvals'))
            if sale_order.global_discount_type == 'percent':
                if sale_order.global_order_discount > sale_order.allowed_discount:
                    raise UserError('Global Discount Should be Less than Allowed Discount')

            else:
                amount = (sale_order.allowed_discount / 100) * sale_order.amount_untaxed
                if sale_order.global_order_discount > amount:
                    raise UserError('Global Discount Should be Less than Allowed Discount')
            sale_order.is_approved_by_manager_discount = 'manager'
            sale_order.state = 'confirmed'

    def action_ceo_approve(self):
        for sale_order in self:
            if sale_order.max_discount > sale_order.allowed_discount:
                raise UserError(
                    _('Your discount limit is lesser then allowed discount.Click on "Ask for Approval" for Approvals'))
            if sale_order.global_discount_type == 'percent':
                if sale_order.global_order_discount > sale_order.allowed_discount:
                    raise UserError('Global Discount Should be Less than Allowed Discount')

            else:
                amount = (sale_order.allowed_discount / 100) * sale_order.amount_untaxed
                if sale_order.global_order_discount > amount:
                    raise UserError('Global Discount Should be Less than Allowed Discount')
            sale_order.is_approved_by_ceo_discount = 'ceo'
            sale_order.state = 'confirmed'

    def action_reject(self):
        self.state = 'draft'

    def compute_self_id(self):
        for i in self:
            i.create_user = i.env.user.id

    def from_manager_approval(self):
        self._create_notification()
        self.state = 'manager'

    def from_ceo_approval(self):
        self._create_notification()
        self.state = 'ceo'

    def _create_notification(self):
        act_type_xmlid = 'mail.mail_activity_data_todo'
        summary = 'Discount Approval'
        note = 'Sale order No: ' + self.name + ' is waiting for Approval.'
        if act_type_xmlid:
            activity_type = self.sudo().env.ref(act_type_xmlid)
        model_id = self.env['ir.model']._get(self._name).id
        create_vals = {
            'activity_type_id': activity_type.id,
            'summary': summary or activity_type.summary,
            'automated': True,
            'note': note,
            'date_deadline': datetime.today(),
            'res_model_id': model_id,
            'res_id': self.id,
            'user_id': self.env.user.manager_id.id,
        }
        activities = self.env['mail.activity'].create(create_vals)

    def action_confirm(self):
        for sale_order in self:
            if sale_order.state != 'confirmed':
                if sale_order.max_discount > sale_order.allowed_discount:
                    raise UserError(
                        _('Your discount limit is lesser then allowed discount.Click on "Ask for Approval" for Approvals'))
                if sale_order.global_discount_type == 'percent':
                    if sale_order.global_order_discount > sale_order.allowed_discount:
                        raise UserError('Global Discount Should be Less than Allowed Discount')

                else:
                    amount = (sale_order.allowed_discount / 100) * sale_order.amount_untaxed
                    if sale_order.global_order_discount > amount:
                        raise UserError('Global Discount Should be Less than Allowed Discount')

                # partner_ledger = self.env['account.move.line'].search(
                #     [('partner_id', '=', sale_order.partner_id.id),
                #      ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
                #      ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
                #      ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')])
                # existing_deliveries = self.env['stock.picking'].search([('partner_id', '=', sale_order.partner_id.id), ('state', '=', 'assigned')])
                # existing_bal = 0
                # for delivery in existing_deliveries:
                #     existing_bal = existing_bal + delivery.sale_id.amount_total
                # acc_bal = 0
                # for par_rec in partner_ledger:
                #     acc_bal = acc_bal + (par_rec.debit - par_rec.credit)
                # acc_bal = -(acc_bal) - existing_bal
                # if acc_bal < ((sale_order.amount_total * 75) / 100):
                #     raise UserError('No Enough Amount in Account')
                return super(SaleOrder, self).action_confirm()
            else:
                return super(SaleOrder, self).action_confirm()

    @api.depends("order_line.discount")
    def compute_max_disccount(self):
        for i in self:
            maximum = []
            diss = 0.0
            for rec in i.order_line:
                maximum.append(rec.discount)
            if maximum:
                diss = max(maximum)
            i.max_discount = diss


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_above = fields.Boolean('Above Discount')

    @api.onchange('discount')
    def onchange_discount(self):
        for rec in self:
            if rec.discount > rec.order_id.allowed_discount:
                rec.is_above = True
            else:
                rec.is_above = False


class users_inherit(models.Model):
    _inherit = 'res.users'
    _description = 'adding to users table'

    allowed_discount = fields.Float(string='Discount Allowed')


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    shipping_address = fields.Char(string='Shipping Address', related='partner_id.street')
    partner_mobile = fields.Char(string='Mobile', related='partner_id.mobile')
    create_user = fields.Many2one('res.users', string='User', compute="compute_self_id")
    invoice_origin = fields.Many2one('account.move', compute='_compute_invoice_origin')
    show_origin = fields.Boolean('Show Origin', compute='compute_show_origin')

    @api.depends('sale_id', 'purchase_id')
    def compute_show_origin(self):
        for rec in self:
            if rec.purchase_id:
                rec.show_origin = True
            elif rec.sale_id:
                rec.show_origin = False
            else:
                rec.show_origin = False

    def _compute_invoice_origin(self):
        for i in self:
            record = self.env['account.move'].search([('invoice_origin', '=', i.origin), ('state', '=', 'posted')],
                                                     limit=1)
            i.invoice_origin = record.id

    def compute_self_id(self):
        for i in self:
            i.create_user = i.sale_id.user_id.id
