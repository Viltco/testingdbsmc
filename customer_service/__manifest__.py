# -*- coding: utf-8 -*-
{
    'name': "Customer Service",

    'summary': """
        Make Customization On HelpDesk
        """,

    'description': """
        Make Customization On HelpDesk
    """,

    'author': "Viltco",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'helpdesk',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'helpdesk', 'contacts'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/customer_service_seq.xml',
        'views/customer_service_views.xml',
    ],
}
