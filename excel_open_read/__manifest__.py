# -*- coding: utf-8 -*-
{
    'name': "Excel Open Read",

    'summary': """
        Open Read Create Data From CSV File""",

    'description': """
        Open Read Create Data From CSV File
    """,

    'author': "Viltco",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'contacts',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'contacts', 'sale', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/excel_open_read_views.xml',
    ],

}
