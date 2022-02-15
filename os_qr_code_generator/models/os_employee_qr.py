# _*_ coding: utf-8 _*_
import qrcode
import base64

from io import BytesIO

from odoo import models, fields, _
from odoo.exceptions import UserError


class HrQrGenerator(models.Model):
    _inherit = 'hr.employee'

    qr_code = fields.Binary("QR Code")

    def generate_hr_qr(self):
        if self.name:
            if self.job_title:
                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )

                qr.add_data(self.name)
                qr.add_data('\n')
                qr.add_data(self.job_title)
                qr.make(fit=True)
                img = qr.make_image()
                tmp = BytesIO()
                img.save(tmp, format="PNG")
                qr_img = base64.b64encode(tmp.getvalue())
                self.qr_code = qr_img
            else:
                raise UserError(_('Check if Employee Name and Job title empty'))