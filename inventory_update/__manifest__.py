# -*- coding: utf-8 -*-
{
    'name': "Inventory Update",

    'summary': """
        Open Wizard To Update Quantity""",

    'description': """
        Open Wizard To Update Quantity in Inventory Configuration
    """,

    'author': "Viltco",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'stock',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
    ],

}
