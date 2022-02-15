from datetime import datetime
from pytz import timezone


from odoo import api, fields, models


class PurchaseOrderLineInh(models.Model):
    _inherit = 'purchase.order.line'

    article_no = fields.Char('Article No', related="product_id.article_no")
    finish_no = fields.Char('Finish No', related="product_id.finish_no")


class ResPartner(models.Model):
    _inherit = 'res.partner'

    is_import_vendor = fields.Boolean('Is import Vendor?')


class StockLandedCost(models.Model):
    _inherit = 'stock.landed.cost'

    def create_assess_history(self, assess, inv, line):
         vals = {
             'product_tmpl_id': line.product_id.product_tmpl_id.id,
             'assess_val': assess,
             'inv_val': inv,
             'date': line.order_id.date_planned,
         }
         rec = self.env['product.assessed.line'].create(vals)

    def button_validate(self):
        c_d = 0
        other = 0
        for res in self.cost_lines:
            if res.product_id.is_custom_duty:
                c_d = c_d + res.price_unit
            if res.product_id.is_other:
                other = other + res.price_unit

        for rec in self.picking_ids:
            if rec.purchase_ids:
                for purchase in rec.purchase_ids:
                    total_assessed = 0
                    total_fc = 0
                    for line in purchase.order_line:
                        total_assessed = total_assessed + line.total_assessed_value
                        total_fc = total_fc + line.sub_total_fc

                    for i in purchase.order_line:
                        percent = (i.total_assessed_value / total_assessed) * 100
                        percent_other = (i.sub_total_fc / total_fc) * 100
                        i.cust_duty = (percent * c_d) / 100
                        i.other_charges = (percent_other * other) / 100

                        unit = (i.unit_pricefc * purchase.fx_rate) + (i.cust_duty / i.product_qty) + (
                                    i.other_charges / i.product_qty)
                        print(unit)
                        i.product_id.standard_price = unit
                        self.create_assess_history(i.assessed_value, i.unit_pricefc, i)
                    purchase.lc_cost_origin = self.name

        # for deliv in self.picking_ids:
        #     for i in deliv.purchase_id.order_line:
        #         percent = (i.total_assessed_value/total_assessed)*100
        #         percent_other = (i.sub_total_fc / total_fc) * 100
        #         print(percent)
        #         i.cust_duty = (percent * c_d) / 100
        #         i.other_charges = (percent_other * other) / 100

        # for rec in self.picking_ids:
        #     for line in rec.purchase_id.order_line:
        #         total_assessed = total_assessed + line.total_assessed_value
        #         total_fc = total_fc + line.sub_total_fc
        # for deliv in self.picking_ids:
        #     for i in deliv.purchase_id.order_line:
        #         percent = (i.total_assessed_value/total_assessed)*100
        #         percent_other = (i.sub_total_fc / total_fc) * 100
        #         print(percent)
        #         i.cust_duty = (percent * c_d) / 100
        #         i.other_charges = (percent_other * other) / 100
        # print(total_fc, total_assessed)


# class StockPickingIn(models.Model):
#     _inherit = "stock.picking"
#
#     lc_cost_origin = fields.Char("LC Origin")

    # def get_lc(self):
    #     lc = self.env['stock.landed.cost'].search([('name', '=', self.picking_ids.lc_cost_origin)])
    #     return lc


class ProductTemplateIn(models.Model):
    _inherit = "product.template"

    is_custom_duty = fields.Boolean("Custom Duty")
    is_other = fields.Boolean("Other")

    assess_line = fields.One2many('product.assessed.line', 'product_tmpl_id')


class ProductTemplateAssessedIn(models.Model):
    _name = "product.assessed.line"
    _order = "create_date desc"

    product_tmpl_id = fields.Many2one('product.template')
    assess_val = fields.Float('Assess Value')
    inv_val = fields.Float('Invoice Value')
    date = fields.Date('Date')


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    s_for = fields.Selection([('local', 'LOCAL'), ('import', 'IMPORT')], string="Select For", required=True,
                             default='local',
                             readonly=True, states={'draft': [('readonly', False)]})

    is_lc = fields.Boolean('LC')
    is_tt = fields.Boolean('TT')

    lc_ref = fields.Char('Ref Number')
    tt_ref = fields.Char('TT Ref Number')

    lc_account = fields.Many2one('account.account', string='LC Account', readonly=True,
                                 states={'draft': [('readonly', False)]})
    lc_ids = fields.One2many('lc.tt', 'lc_id', string="LC and TT Field")

    fx_rate = fields.Float('FX Rate')
    # start
    lc_ref_no = fields.Char('Contract No.')
    bank_name = fields.Many2one('account.journal', string="Bank Name")
    condition = fields.Many2one('lc.condition', "Condition")

    lc_cost_origin = fields.Char("LC Origin")
    gd_no = fields.Char('GD No')
    bl_no = fields.Char('BL No')
    inv_no = fields.Char('INV No')
    clearing_no = fields.Char('Clearing Agent Bill No')

    def get_print_date(self):
        now_utc_date = datetime.now()
        now_dubai = now_utc_date.astimezone(timezone('Asia/Karachi'))
        return now_dubai.strftime('%d/%m/%Y %H:%M:%S')

    def get_lc(self):
        lc = self.env['stock.landed.cost'].search([('name', '=', self.lc_cost_origin)])
        return lc

    # end

    # this field show in LC notebook

    # _sql_constraints = [
    #     ('uniq_lc_ref',
    #      'unique(lc_ref)',
    #      'The reference must be unique'),
    # ]

    @api.model
    def create(self, vals):
        if 'lc_ref' not in vals or vals['lc_ref'] == False and vals['is_lc'] == True:
            sequence = self.env.ref('import_logistic.seq_lc_auto')
            vals['lc_ref'] = sequence.next_by_id()

        if 'tt_ref' not in vals or vals['tt_ref'] == False and vals['is_tt'] == True:
            sequence = self.env.ref('import_logistic.seq_tt_auto')
            vals['tt_ref'] = sequence.next_by_id()
        return super(PurchaseOrder, self).create(vals)

    def compute(self):
        total_tt = 0.0
        total_lc = 0.0
        for lc in self.lc_ids:
            total_lc += lc.amount

        for line in self.order_line:
            line.sub_total_fc = line.sub_total_lp = line.sub_total_lp = 0.0
            line.sub_total_fc = line.product_qty * line.unit_pricefc
            line.sub_total_lp = line.sub_total_fc * self.fx_rate
            line.total_assessed_value = line.product_qty * line.assessed_value

        totalunit_pricefc = 0.0
        num_of_product = 0
        for line in self.order_line:
            num_of_product += 1
            totalunit_pricefc += line.unit_pricefc

        #         here other charges mean sum of all charges which created in LC and TT notebook
        lc_othercharges = 0.0

        for lc_id in self.lc_ids:
            lc_othercharges += lc_id.amount

        for line in self.order_line:
            line.lc_cost = ((total_lc / totalunit_pricefc) * line.unit_pricefc)

            if line.qty_received > 0:
                # line.price_unit = (line.lc_cost + line.sub_total_lp) / line.qty_received
                line.price_unit = line.product_id.list_price

            elif line.product_qty != 0:
                # line.price_unit = (line.lc_cost + line.sub_total_lp) / line.product_qty
                line.price_unit = line.product_id.list_price


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    unit_pricefc = fields.Float('Unit Price FC')
    sub_total_fc = fields.Float('Subtotal FC')
    sub_total_lp = fields.Float('Subtotal LP')
    lc_cost = fields.Float('LC Cost')
    s_for = fields.Selection([('local', 'LOCAL'), ('import', 'IMPORT')], string="Select For", related='order_id.s_for')
    article_no = fields.Char('Article No')
    finish_no = fields.Char('Finish No')
    assessed_value = fields.Float('Assessed value FC')
    total_assessed_value = fields.Float('Total Assessed value')
    cust_duty = fields.Float("C.D")
    other_charges = fields.Float("Other Charges")

    @api.onchange('product_id')
    def onchange_get_assess_val(self):
        for rec in self:
            if rec.product_id.assess_line:
                rec.assessed_value = rec.product_id.assess_line[0].assess_val
                rec.unit_pricefc = rec.product_id.assess_line[0].inv_val
            # rec.price_unit = rec.product_id.standard_price

    @api.depends('product_qty', 'price_unit', 'taxes_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.taxes_id.compute_all(line.price_unit, line.order_id.currency_id, line.product_qty,
                                              product=line.product_id, partner=line.order_id.partner_id)
            discount = (line.price_unit * line.discount * line.product_qty) / 100
            if line.s_for != 'import':

                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': taxes['total_excluded'] - discount,
                })
            else:
                line.update({
                    'price_tax': taxes['total_included'] - taxes['total_excluded'],
                    'price_total': taxes['total_included'],
                    'price_subtotal': line.lc_cost + line.sub_total_lp,
                })
                line.price_subtotal = line.lc_cost + line.sub_total_lp
                if line.qty_received > 0:
                    line.price_unit = line.product_id.list_price
                    # line.price_unit = line.price_subtotal / line.qty_received
                else:
                    if line.product_qty >0:
                        line.price_unit = line.product_id.list_price
                        # line.price_unit = line.price_subtotal / line.product_qty

                line.price_subtotal = (line.lc_cost + line.sub_total_lp) - discount


                    # if line.qty_received > 0:
                    #     line.price_unit = line.price_subtotal/line.qty_received
                    # elif line.product_qty !=0:
                    #     line.price_unit = line.price_subtotal/line.product_qty
        # self.order_id.compute()

class LcCharges(models.Model):
    _name = "lc.tt"

    lc_id = fields.Many2one('purchase.order')
    name = fields.Many2one('lc.tt.name', String='Name')
    amount = fields.Float('Amount')


class LcTtName(models.Model):
    _name = "lc.tt.name"

    name = fields.Char('Name')


class LcCondition(models.Model):
    _name = "lc.condition"

    name = fields.Char('Name')


class AccountMove(models.Model):
    _inherit = "account.move"

    lc_ref_po = fields.Many2one('purchase.order', string='PO Ref of LC OR TT')

    lc_insurance = fields.Float('Insurance')
    lc_clearing = fields.Float('Clearing Charges')
    lc_ref = fields.Char('LC Ref Number', related="lc_ref_po.lc_ref")
    tt_ref = fields.Char('TT Ref Number', related="lc_ref_po.tt_ref")

    is_lc_jour_entr = fields.Boolean('Is LC', related="journal_id.is_lc_jour")
    is_tt_jour_entr = fields.Boolean('Is LT', related="journal_id.is_tt_jour")

    @api.onchange('lc_ref_po')
    def add_account(self):
        if self.lc_ref_po.id != False:
            lc_line_ids = []
            r = ({
                'account_id': self.lc_ref_po.lc_account.id,
                #                     'date_maturity': '03-01-2018',
                'name': str(self.lc_ref_po.lc_account.name),
            })
            lc_line_ids.append(r)

            lc_lines = self.line_ids.browse([])

            for r in lc_line_ids:
                lc_lines += lc_lines.new(r)
            self.line_ids = lc_lines

    def button_cancel(self):
        res = super(AccountMove, self).button_cancel()
        # for lc in  self.lc_ref_po.lc_ids:
        #     self.lc_ref_po.write({'lc_ids':[(1, lc.id,{
        #                                                 'amount':0.0})]})
        lc_line = []
        if self.journal_id.is_lc_jour == True and self.lc_ref_po != ' ' or self.journal_id.is_tt_jour == True and self.lc_ref_po != ' ':
            for lc_move in self.line_ids:
                vals = {
                    'po_ref': self.lc_ref_po,
                    'chrg_name': lc_move.lc_charges,
                    'chrg_debit': lc_move.debit,
                    'chrg_credit': lc_move.credit,
                }
                lc_line.append(vals)
        for line in lc_line:
            flag = 0
            for lc in self.lc_ref_po.lc_ids:
                if lc.name == line['chrg_name']:
                    flag = 1
                    prv_amount = lc.amount

                    if line['chrg_debit']:
                        curr_amount = prv_amount - line['chrg_debit']
                        if curr_amount < 0:
                            curr_amount = 0
                    else:
                        curr_amount = prv_amount + line['chrg_credit']
                        if curr_amount > 0:
                            curr_amount = 0
                    self.lc_ref_po.write({'lc_ids': [(1, lc.id, {
                        'amount': curr_amount})]})
            if flag == 0 and line['chrg_name'].id != False:

                if line['chrg_debit']:
                    curr_amount1 = line['chrg_debit']
                    if curr_amount1 < 0:
                        curr_amount1 = 0
                    self.lc_ref_po.write({'lc_ids': [(0, 0, {
                        'name': line['chrg_name'].id,
                        'amount': curr_amount1})]})
                else:
                    curr_amount1 = -line['chrg_credit']
                    if curr_amount1 > 0:
                        curr_amount1 = 0
                    self.lc_ref_po.write({'lc_ids': [(0, 0, {
                        'name': line['chrg_name'].id,
                        'amount': curr_amount1})]})
        return res

    def post(self):
        res = super(AccountMove, self).post()

        lc_line = []
        if self.journal_id.is_lc_jour == True and self.lc_ref_po != ' ' or self.journal_id.is_tt_jour == True and self.lc_ref_po != ' ':
            for lc_move in self.line_ids:
                vals = {
                    'po_ref': self.lc_ref_po,
                    'chrg_name': lc_move.lc_charges,
                    'chrg_debit': lc_move.debit,
                    'chrg_credit': lc_move.credit,
                }
                lc_line.append(vals)
        for line in lc_line:
            flag = 0
            for lc in self.lc_ref_po.lc_ids:
                if lc.name == line['chrg_name']:
                    flag = 1
                    prv_amount = lc.amount

                    if line['chrg_debit']:
                        curr_amount = prv_amount + line['chrg_debit']
                    else:
                        curr_amount = prv_amount - line['chrg_credit']
                    self.lc_ref_po.write({'lc_ids': [(1, lc.id, {
                        'amount': curr_amount})]})
            if flag == 0 and line['chrg_name'].id != False:

                if line['chrg_debit']:
                    curr_amount1 = line['chrg_debit']
                    self.lc_ref_po.write({'lc_ids': [(0, 0, {
                        'name': line['chrg_name'].id,
                        'amount': curr_amount1})]})
                else:
                    curr_amount1 = -line['chrg_credit']
                    self.lc_ref_po.write({'lc_ids': [(0, 0, {
                        'name': line['chrg_name'].id,
                        'amount': curr_amount1})]})
        return res


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"
    lc_charges = fields.Many2one('lc.tt.name', string="Charges")
    is_lc_jour_entr = fields.Char('Is LC', compute="get_lctt")  # related="move_id.lc_ref")
    is_tt_jour_entr = fields.Char('Is LT', compute="get_lc")

    #     is_lc_jour_entr = fields.Boolean('Is LC',related="move_id.is_lc_jour_entr")
    #     is_tt_jour_entr = fields.Boolean('Is LT',related="move_id.is_tt_jour_entr")

    @api.depends('account_id')
    def get_lctt(self):
        for lc in self:
            lc.is_lc_jour_entr = lc.move_id.lc_ref

    @api.depends('account_id')
    def get_lc(self):
        for lc in self:
            lc.is_tt_jour_entr = lc.move_id.tt_ref


class AccountJournal(models.Model):
    _inherit = "account.journal"
    is_lc_jour = fields.Boolean('Is LC')
    is_tt_jour = fields.Boolean('Is TT')
