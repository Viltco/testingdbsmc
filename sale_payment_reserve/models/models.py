# -*- coding: utf-8 -*-
import locale
import urllib
from datetime import datetime
from operator import itemgetter

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta

from odoo.tools import OrderedSet, float_is_zero, float_compare, groupby


class SaleOrderInh(models.Model):
    _inherit = 'sale.order'

    payment_count = fields.Integer(compute='compute_payments')
    commitment_date = fields.Datetime('Delivery Date', copy=False,
                                      states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
                                      help="This is the delivery date promised to the customer. "
                                           "If set, the delivery order will be scheduled based on "
                                           "this date rather than product lead times.")

    @api.depends('name')
    def compute_payments(self):
        for rec in self:
            count = self.env['account.payment'].search_count([('ref', '=', rec.name)])
            rec.payment_count = count

    def action_register_payment(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Apply Advance Payments',
            'view_id': self.env.ref('sale_payment_reserve.view_advance_payment_wizard_form', False).id,
            'context': {'default_ref': self.name, 'default_order_amount': self.amount_total, 'default_user_id': self.user_id.id},
            'target': 'new',
            'res_model': 'advance.payment.wizard',
            'view_mode': 'form',
        }

    def action_show_payments(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Advance Payments',
            'view_id': self.env.ref('account.view_account_payment_tree', False).id,
            'target': 'current',
            'domain': [('ref', '=', self.name)],
            'res_model': 'account.payment',
            'views': [[False, 'tree'], [False, 'form']],
        }

    def action_confirm(self):
        res = super(SaleOrderInh, self).action_confirm()
        for order in self:
            for picking in order.picking_ids:
                picking.do_unreserve()
        if self.warehouse_id.name == 'RAIWIND WAREHOUSE' and self.user_picking_type == 'deliver_at_site':
            flag = False
            for line in self.order_line:
                if line.product_id.type == 'service':
                    flag = True
                    break
            if not flag:
                raise UserError('Please Add Shipping Changes')
        self.action_so_sms_api()
        return res

    def action_so_sms_api(self):
        user = '03334220752'
        password = '03334220752'
        sender = 'SMC'
        to = self.partner_id.mobile
        # locale.setlocale(locale.LC_ALL, '')
        # amnt = str(locale.currency(self.amount_total, grouping=True))
        msg = 'Dear Customer,\nYour Quotation# ' + self.name + ' has been approved. Kindly pay Rs ' + str(self.amount_total) + '\nBest Regards,\nSMC Team'
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


class StockBackorderConfirmationInh(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'

    def process(self):
        pickings_to_do = self.env['stock.picking']
        pickings_not_to_do = self.env['stock.picking']
        for line in self.backorder_confirmation_line_ids:
            if line.to_backorder is True:
                pickings_to_do |= line.picking_id
            else:
                pickings_not_to_do |= line.picking_id

        for pick_id in pickings_not_to_do:
            moves_to_log = {}
            for move in pick_id.move_lines:
                if float_compare(move.product_uom_qty,
                                 move.quantity_done,
                                 precision_rounding=move.product_uom.rounding) > 0:
                    moves_to_log[move] = (move.quantity_done, move.product_uom_qty)
            pick_id._log_less_quantities_than_expected(moves_to_log)

        pickings_to_validate = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate:
            pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate).with_context(
                skip_backorder=True)
            if pickings_not_to_do:
                pickings_to_validate = pickings_to_validate.with_context(
                    picking_ids_not_to_backorder=pickings_not_to_do.ids)

            return pickings_to_validate.action_validate_inh()
        return True

    def process_cancel_backorder(self):
        pickings_to_validate = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate:
            return self.env['stock.picking'] \
                .browse(pickings_to_validate) \
                .with_context(skip_backorder=True, picking_ids_not_to_backorder=self.pick_ids.ids) \
                .action_validate_inh()
        return True


class StockImmediateTransferInh(models.TransientModel):
    _inherit = 'stock.immediate.transfer'

    def process(self):
        pickings_to_do = self.env['stock.picking']
        pickings_not_to_do = self.env['stock.picking']
        for line in self.immediate_transfer_line_ids:
            if line.to_immediate is True:
                pickings_to_do |= line.picking_id
            else:
                pickings_not_to_do |= line.picking_id

        for picking in pickings_to_do:
            # If still in draft => confirm and assign
            if picking.state == 'draft':
                picking.action_confirm()
                if picking.state != 'assigned':
                    picking.action_assign()
                    if picking.state != 'assigned':
                        raise UserError(_("Could not reserve all requested products. Please use the \'Mark as Todo\' button to handle the reservation manually."))
            for move in picking.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
                for move_line in move.move_line_ids:
                    move_line.qty_done = move_line.product_uom_qty

        pickings_to_validate = self.env.context.get('button_validate_picking_ids')
        if pickings_to_validate:
            pickings_to_validate = self.env['stock.picking'].browse(pickings_to_validate)
            pickings_to_validate = pickings_to_validate - pickings_not_to_do
            return pickings_to_validate.with_context(skip_immediate=True).action_validate_inh()
        return True


class StockPickingInh(models.Model):
    _inherit = 'stock.picking'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('waiting', 'Waiting Another Operation'),
        ('confirmed', 'Waiting'),
        ('manager_approval', 'Credit Approval from Manager'),
        ('ceo_approval', 'Credit Approval from CEO'),
        ('reserve_manager_approvals', 'Reserve Extension Approval from Manager'),
        ('reserve_ceo_approval', 'Reserve Extension Approval from CEO'),
        ('reserve_ext_ceo_approval', 'Reserve Extension Approval from CEO'),
        ('duration_manager_approvals', 'Duration Approval from Manager'),
        ('duration_ceo_approval', 'Duration Approval from CEO'),
        ('approved', 'Approved'),
        ('assigned', 'Ready'),
        ('in_transit', 'In Transit'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
    ], string='Status', compute='_compute_state',
        copy=False, index=True, readonly=True, store=True, tracking=True,
        help=" * Draft: The transfer is not confirmed yet. Reservation doesn't apply.\n"
             " * Waiting another operation: This transfer is waiting for another operation before being ready.\n"
             " * Waiting: The transfer is waiting for the availability of some products.\n(a) The shipping policy is \"As soon as possible\": no product could be reserved.\n(b) The shipping policy is \"When all products are ready\": not all the products could be reserved.\n"
             " * Ready: The transfer is ready to be processed.\n(a) The shipping policy is \"As soon as possible\": at least one product has been reserved.\n(b) The shipping policy is \"When all products are ready\": all product have been reserved.\n"
             " * Done: The transfer has been processed.\n"
             " * Cancelled: The transfer has been cancelled.")
    no_enough_amount = fields.Boolean(default=False, compute='compute_payment')
    is_approved_by_manager = fields.Selection([
        ('none', 'None'),
        ('manager', 'Reserve Approved By Manager'), ], string='Reserve Approved By Manager', default='none')
    is_approved_by_ceo = fields.Selection([
        ('none', 'None'),
        ('ceo', 'Reserve Approved By CEO'), ], string='Reserve Approved By CEO', default='none')

    def action_assign(self):
        record = super(StockPickingInh, self).action_assign()
        if self.picking_type_id.code == 'outgoing':
            self.action_availability_sms_api()
        return record

    def action_assign_custom(self):
        self.do_unreserve()
        self.action_assign()

    is_approved_by_manager_credit = fields.Selection([
        ('none', 'None'),
        ('manager', 'Credit Approved By Manager'), ], string='Credit Approved By Manager', default='none')
    is_approved_by_ceo_credit = fields.Selection([
        ('none', 'None'),
        ('ceo', 'Credit Approved By CEO'), ], string='Credit Approved By CEO', default='none')

    def action_ready(self):
        self.state = 'assigned'

    def button_validate(self):
        if self.picking_type_id.code == 'outgoing':
            self.state = 'in_transit'
            self.action_transit_sms_api()
        else:
            record = super(StockPickingInh, self).button_validate()
            return record

    def action_transit_sms_api(self):
        user = '03334220752'
        password = '03334220752'
        sender = 'SMC'
        to = self.partner_id.mobile
        msg = 'Dear Customer,\nYour shipment against Sale Order #: ' + self.origin + ' is on the way.' + '\nDriver Name: ' + self.driver.name + '\nTruck No: ' + self.vehicle_no + '\nMobile: ' + self.mobile + '\nBest Regards,\nSMC Team'
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

    def action_validate_inh(self):
        record = super(StockPickingInh, self).button_validate()
        if self.picking_type_id.code == 'outgoing':
            self.action_validate_sms_api()
        return record

    def action_validate_sms_api(self):
        user = '03334220752'
        password = '03334220752'
        sender = 'SMC'
        to = self.partner_id.mobile
        msg = 'Dear Customer,\nYour Sale Order #: ' + self.origin + ' has been delivered. Thank you for purchasing from SMC.\nBest Regards,\nSMC Team'
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

    def action_reject(self):
        self.state = 'confirmed'

    def action_duration_manager_approval(self):
        self.is_approved_by_manager = 'manager'
        self.state = 'duration_ceo_approval'

    def action_duration_ceo_approval(self):
        self.is_approved_by_ceo = 'ceo'
        self.state = 'approved'

    @api.depends('sale_id.amount_total')
    def compute_payment(self):
        for rec in self:
            partner = self.env['res.partner'].search([('id', '=', rec.partner_id.id)])
            partner_ledger = self.env['account.move.line'].search(
                [('partner_id', '=', partner.id),
                 ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
                 ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|',
                 ('account_id.internal_type', '=', 'payable'), ('account_id.internal_type', '=', 'receivable')])
            bal = 0
            for par_rec in partner_ledger:
                bal = bal + (par_rec.debit - par_rec.credit)
            if partner:
                if -(bal) >= (rec.sale_id.amount_total * 75) / 100:
                    rec.no_enough_amount = False
                else:
                    rec.no_enough_amount = True
            else:
                rec.no_enough_amount = False

    def action_reserve_do(self):
        flag = 0
        for rec in self:
            if rec.picking_type_id.code == 'outgoing':
                partner = self.env['res.partner'].search([('id', '=', rec.partner_id.id)])
                partner_ledger = self.env['account.move.line'].search(
                    [('partner_id', '=', partner.id),
                     ('move_id.state', '=', 'posted'), ('full_reconcile_id', '=', False), ('balance', '!=', 0),
                     ('account_id.reconcile', '=', True), ('full_reconcile_id', '=', False), '|', ('account_id.internal_type', '=', 'payable'),('account_id.internal_type', '=', 'receivable')])
                bal = 0
                for par_rec in partner_ledger:
                    bal = bal + (par_rec.debit - par_rec.credit)
                if partner:
                    if -(bal) >= (rec.sale_id.amount_total * 75)/100:
                        if not rec.sale_id.commitment_date:
                            rec.sale_id.commitment_date = datetime.today() + relativedelta(days=3)
                        if abs((rec.sale_id.commitment_date.date() - datetime.today().date()).days) <= 7:
                            rec.action_assign()
                            flag = 1
                        else:
                            rec.state = 'duration_manager_approvals'
                    else:
                        raise UserError('There is no enough Advance Payment available to Reserve this DO.')
                else:
                    raise UserError('There is no enough Advance Payment available to Reserve this DO.')

            else:
                rec.action_assign()

    def action_availability_sms_api(self):
        user = '03334220752'
        password = '03334220752'
        sender = 'SMC'
        to = self.partner_id.mobile
        msg = 'Dear Customer,\nYour Sale Order #: ' + self.origin + ' has been reserved ' + '\nBest Regards,\nSMC Team'
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

    def action_manager_approval(self):
        self.is_approved_by_manager_credit = 'manager'
        self.state = 'ceo_approval'

    def action_ceo_approval(self):
        self.is_approved_by_ceo_credit = 'ceo'
        self.state = 'approved'

    def action_get_approvals(self):
        self.state = 'manager_approval'


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    user_id = fields.Many2one('res.users', related="partner_id.user_id")
