# -*- coding: utf-8 -*-
##############################################################################
#
#    Odoo, Open Source Management Solution
#    Copyright (C) 2015 Dynexcel (<http://dynexcel.com/>).
#
##############################################################################
{
    'name': 'Partner Ledger',
    'version': '14.0',
    'summary': 'This module will add Partner Ledger Report',
    'description': 'This module provides the movement of individual products with opening and closing stocks',
    'author': 'Dynexcel',
    'maintainer': 'Hunain AK',
    'company': 'Hunain AK',
    'website': 'https://www.Hunain AK.com',
    'depends': [
		'base', 'account','contacts',
		],
    'category': 'Accounting',
    'demo': [],
    'data': ['views/partner_ledger_views.xml',
             'security/ir.model.access.csv',
             'report/partner_ledger_report.xml',
             'report/partner_ledger_report_template.xml'],
    'installable': True,
    'images': ['static/description/banner.png'],
    'qweb': [],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,

}
