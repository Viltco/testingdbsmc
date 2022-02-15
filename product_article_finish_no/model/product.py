import base64
from io import BytesIO

import qrcode

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.osv import expression
import re


class ProductProduct(models.Model):
    _inherit = "product.product"

    forecasted_qty = fields.Float('Forecasted Qty', compute='compute_forecasted_qty')
    free_sold_qty = fields.Float('Available Qty', compute='compute_free_sold_qty')

    @api.depends('qty_available')
    def compute_free_sold_qty(self):
        for rec in self:
            quants = self.env['stock.quant'].search([('product_id', '=', rec.id)])
            prd_resrv_qty = 0
            for rsrvqt in quants:
                prd_resrv_qty = prd_resrv_qty + rsrvqt.reserved_quantity
            rec.free_sold_qty = rec.qty_available - prd_resrv_qty

    def compute_forecasted_qty(self):
        for rec in self:
            products = self.env['stock.move'].search([('picking_type_id.code', '=', 'incoming'), ('product_id','=', rec.id),
                                                      ('picking_id.state', '=', 'assigned')])
            qty = 0
            # so_list = []
            for line in products:
                qty = qty + line.product_uom_qty
                # so_list.append('(' + line.picking_id.purchase_id.name + ':' + str(qty) + ')' )
            # joined_string = ",".join(so_list)
            rec.forecasted_qty = qty
            # quants = self.env['stock.quant'].search([('product_id', '=', rec.id)])
            # prd_resrv_qty = 0
            # for rsrvqt in quants:
            #     prd_resrv_qty = prd_resrv_qty + rsrvqt.reserved_quantity
            # rec.free_sold_qty = rec.qty_available - prd_resrv_qty

    def name_get(self):
        res = []
        for rec in self:
            res.append((rec.id, '%s : %s : %s' % (rec.name, rec.article_no, rec.finish_no)))
        return res

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            product_ids = []
            if operator in positive_operators:
                product_ids = list(self._search(['|', ('default_code', '=', name), '|', ('article_no', 'ilike', name), ('finish_no', 'ilike', name)] + args, limit=limit, access_rights_uid=name_get_uid))
                if not product_ids:
                    product_ids = list(self._search(['|', ('barcode', '=', name), '|', ('article_no', 'ilike', name), ('finish_no', 'ilike', name)] + args, limit=limit, access_rights_uid=name_get_uid))
            if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                product_ids = list(self._search(args + [('default_code', operator, name)], limit=limit))
                if not limit or len(product_ids) < limit:
                    limit2 = (limit - len(product_ids)) if limit else False
                    product2_ids = self._search(args + [('name', operator, name), ('id', 'not in', product_ids)], limit=limit2, access_rights_uid=name_get_uid)
                    product_ids.extend(product2_ids)
            elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR([
                    ['&', ('default_code', operator, name), ('name', operator, name)],
                    ['&', ('default_code', '=', False), ('name', operator, name)]
                ])
                domain = expression.AND([args, domain])
                product_ids = list(self._search(domain, limit=limit, access_rights_uid=name_get_uid))
            if not product_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    product_ids = list(self._search([('default_code', '=', res.group(2))] + args, limit=limit, access_rights_uid=name_get_uid))
            if not product_ids and self._context.get('partner_id'):
                suppliers_ids = self.env['product.supplierinfo']._search([
                    ('name', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)], access_rights_uid=name_get_uid)
                if suppliers_ids:
                    product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit, access_rights_uid=name_get_uid)
        else:
            product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return product_ids


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    article_no = fields.Char()
    finish_no = fields.Char()
    sqm_box = fields.Float(string="SQM/Box", digits=(12, 4))
    pcs_box = fields.Integer(string="PCS/Box")
    system_code = fields.Char(string="System Code")
    sqft_box = fields.Float('SQFT/BOX')
    rft_box = fields.Float('RFT/BOX')
    forecasted_qty = fields.Float('Forecasted Qty', compute='compute_forecasted_qty')
    free_sold_qty = fields.Float('Available Qty', compute='compute_free_sold_qty')

    @api.model
    def create(self, vals):
        products = self.env['product.template'].search([], order="id desc")
        vals['system_code'] = int(products[0].system_code) + 1
        result = super(ProductTemplate, self).create(vals)
        return result

    @api.depends('qty_available')
    def compute_free_sold_qty(self):
        for rec in self:
            prd_resrv_qty = 0.0
            quants = self.env['stock.quant'].search([('product_tmpl_id', '=', rec.id)])
            for rsrvqt in quants:
                prd_resrv_qty = prd_resrv_qty + rsrvqt.reserved_quantity
            rec.free_sold_qty = rec.qty_available - prd_resrv_qty

    # @api.depends('qty_available')
    def compute_forecasted_qty(self):
        for rec in self:
            products = self.env['stock.move'].search(
                [('picking_type_id.code', '=', 'incoming'), ('product_id.product_tmpl_id', '=', rec.id),
                 ('picking_id.state', '=', 'assigned')])
            qty = 0
            so_list = []
            for line in products:
                qty = qty + line.product_uom_qty
                # so_list.append('(' + line.picking_id.purchase_id.name + ':' + str(qty) + ')' )
            # joined_string = ",".join(so_list)
            rec.forecasted_qty = qty

    @api.constrains('system_code')
    def unique_system_code(self):
        product = self.env['product.template'].search([('system_code', '=', self.system_code)])
        if len(product) > 1:
            raise UserError('System Code Already Exist')

    @api.constrains('name')
    def unique_product_desc(self):
        name = self.name
        article_no = self.article_no
        finish_no = self.finish_no
        product = self.env['product.template'].search([('name', '=', name)])
        article = self.env['product.template'].search([('article_no', '=', article_no)])
        finish = self.env['product.template'].search([('finish_no', '=', finish_no)])
        if len(product) > 1 and len(article) > 1 and len(finish) > 1:
            raise UserError('Product Already Exists!!!!')


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    address = fields.Char("Address", related="partner_id.street")
    mobile_no = fields.Char("Mobile No", related="partner_id.mobile")
    email_id = fields.Char(string="Email Id", related="partner_id.email")
    architect = fields.Char(string="Architect")
    project_description = fields.Text("Project Description")
    comments = fields.Char("Comments")


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    article_no = fields.Char("Article#", related="product_id.article_no")
    finish_no = fields.Char("Finish", related="product_id.finish_no")
    total_sqm = fields.Float(string="Total Box")
    total_pcs = fields.Float(string="Total Pcs")
    sqm_box = fields.Float(string="SQM/Box", related='product_id.sqm_box')

    @api.onchange('product_uom_qty')
    def _compute_product_uom_qty(self):
        for rec in self:
            rec.total_sqm = round(rec.product_uom_qty / (round(rec.product_id.sqm_box, 4) or 1), 4)
            rec.total_pcs = rec.total_sqm * rec.product_id.pcs_box
            sqm = rec.total_sqm - int(rec.total_sqm)
            print((round(rec.product_id.sqm_box, 4)))
            print(sqm)
            if sqm != 0:
                raise UserError('Plz Add Rounded Qty')


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    sqm_box = fields.Float(string="SQM/Box", related='product_id.sqm_box')
    total_sqm = fields.Float(string="Total Box", compute='_compute_product_uom_qty')

    @api.depends('product_uom_qty', 'qty_done')
    def _compute_product_uom_qty(self):
        for rec in self:
            if rec.state not in ['done']:
                if rec.qty_done == 0:
                    rec.total_sqm = rec.product_uom_qty / (round(rec.product_id.sqm_box, 4) or 1)
                else:
                    rec.total_sqm = round(rec.qty_done / (round(rec.product_id.sqm_box, 4) or 1), 4)
                    sqm = rec.total_sqm - int(rec.total_sqm)
                    print(sqm)
                    if sqm != 0:
                        raise UserError('Plz Add Rounded Qty')
            else:
                rec.total_sqm = rec.qty_done / (round(rec.product_id.sqm_box, 4) or 1)
