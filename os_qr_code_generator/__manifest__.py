# -*- coding: utf-8 -*-
{
    'name': 'QR Code Generator',
    'summary': 'QR Code Generator for Products, Customers and Employees',
    'version': '13.0.1.0.0',
    'category': 'Industries',
    'author': 'Odosquare',
    'company': 'Odosquare',
    'maintainer': 'Odosquare',
    'images': ['static/description/Banner.png'],
    'depends': [
        'base',
        'product',
    ],
    'data': [
        'views/os_customer_qr.xml',
        'views/os_product_qr.xml',
        'views/os_employee_qr.xml',
        'reports/report_qr_code_pdf.xml'
    ],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': True,
}
