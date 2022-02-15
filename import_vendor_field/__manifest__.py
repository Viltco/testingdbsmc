# -*- coding: utf-8 -*-
{
    'name': "Import Vendor Field",

    'summary': """
        import_vendor_field boolean fieldin res partner""",

    'description': """
       import_vendor_field boolean fieldin res partner
    """,

    'author': "Viltco",
    'website': "http://www.Viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','contacts'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        #'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
