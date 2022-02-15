# -*- coding: utf-8 -*-
{
    'name': "SMC Overall",

    'summary': """
        SMC Overall""",

    'description': """
        Customer Sequence, Tree View in Products, Balance on invoice, Balance in Customer Search,
    """,

    'author': "Atif Ali",
    'website': "http://www.abc.co",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'account', 'sale', 'branch', 'sale_stock', 'account_reports', 'stock_landed_costs', 'purchase', 'purchase_stock', 'partner_current_account', 'hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/groups.xml',
        'views/res_partner_views.xml',
        'data/sequence.xml',
        'views/product_views.xml',
        'views/account_views.xml',
        'views/sale_views.xml',
        'reports/ledger_report.xml',
        'reports/purchase_report.xml',
        'reports/payment_report.xml',
        'reports/jv_report.xml',
        'views/purchase.xml',
        'views/hr_view.xml',
        'wizard/payslip_wizard.xml',
    ],
}
