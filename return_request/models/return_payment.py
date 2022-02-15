from odoo import models, fields, api, _
from odoo.tools.float_utils import float_round
from odoo.exceptions import UserError, ValidationError
from datetime import datetime


class AccountPaymentInh(models.Model):
    _inherit = 'account.payment'

    return_id = fields.Many2one('returns.payment')

    def action_cancel(self):
        record = super(AccountPaymentInh, self).action_cancel()
        if self.return_id:
            self.return_id.state = 'cancel'

    def action_draft(self):
        record = super(AccountPaymentInh, self).action_draft()
        if self.return_id:
            self.return_id.state = 'draft'


class ReturnPayment(models.Model):
    _name = 'returns.payment'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'id desc'

    partner_id = fields.Many2one('res.partner')
    payment_id = fields.Many2one('account.payment')
    branch_id = fields.Many2one('res.branch', default=lambda self: self.env.user.branch_id)
    user_id = fields.Many2one('res.users' , default=lambda self: self.env.user)
    # currency_id = fields.Many2one('res.currency')
    journal_id = fields.Many2one('account.journal')
    amount = fields.Float('Amount', tracking=1)
    date = fields.Date('Date', tracking=1, default=lambda self: fields.Datetime.now())
    ref = fields.Char('Memo')
    state = fields.Selection(
        [('draft', 'Draft'), ('director', 'Payment Return Approval'),
         ('approved', 'Approved'), ('rejected', 'Rejected'), ('cancel', 'Canceled')], string="State", readonly=True, default="draft", tracking=1)

    corporate_sale = fields.Boolean()
    other_receipt = fields.Boolean()
    name = fields.Char('Return Payment', required=True, copy=False, readonly=True,
                       index=True, default=lambda self: _('New'))

    @api.model
    def create(self, vals):
        if vals.get('name', _('New')) == _('New'):
            vals['name'] = self.env['ir.sequence'].next_by_code('return.payment.sequence') or _('New')
        result = super(ReturnPayment, self).create(vals)
        return result

    def action_draft(self):
        self.state = 'draft'

    def action_confirm(self):
        self.state = 'director'

    def action_cancel(self):
        if self.payment_id.state == 'posted':
            raise UserError('You cannot cancel Posted Payment.')
        else:
            self.state = 'cancel'

    def action_reject(self):
        self.state = 'rejected'

    def action_approve(self):
        payment = self.create_payment()
        self.payment_id = payment.id
        if payment:
            self.state = 'approved'

    def create_payment(self):
        for rec in self:
            vals = {
                'journal_id': rec.journal_id.id,
                'return_id': rec.id,
                'partner_id': rec.partner_id.id,
                'date': rec.date,
                'amount': rec.amount,
                'payment_type': 'outbound',
                'partner_type': 'customer',
                # 'currency_id': rec.currency_id.id,
                'ref': rec.ref,
                # 'user_id': rec.user_id.id,
                'branch_id': rec.branch_id.id,
                'cheques_payment': False,
                'online_credit_payment': False,
                'corporate_sale': rec.corporate_sale,
                'other_receipt': rec.other_receipt,
                'state': 'draft',
            }
            payment = self.env['account.payment'].create(vals)
            return payment
