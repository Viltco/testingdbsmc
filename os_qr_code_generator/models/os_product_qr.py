# _*_ coding: utf-8 _*_
import qrcode
import base64

from io import BytesIO

from odoo import models, fields, _
from odoo.exceptions import UserError


class ProductQrGenerator(models.Model):
    _inherit = 'product.template'

    pro_qr_code = fields.Image("QR Code", max_width=512, max_height=512)
    qr_code = fields.Binary("QR Code")

    def generate_qr(self):
        for records in self:
            if records.name and records.article_no and records.finish_no:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=5,
                    border=5,
                )
                qr.add_data(records.name)
                qr.add_data('\n')
                qr.add_data(records.article_no)
                qr.add_data('\n')
                qr.add_data(records.finish_no)
                qr.make(fit=True)
                img = qr.make_image(fill_color='black',back_color='white')
                tmp = BytesIO()
                img.save(tmp, format="PNG")
                qr_img = base64.b64encode(tmp.getvalue())
                records.pro_qr_code = qr_img
            else:
                raise UserError(_('Check if Product Name, Sales Price or Internal Reference empty'))
            
            
            