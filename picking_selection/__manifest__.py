# -*- coding: utf-8 -*-
{
    'name': "Picking Selection",

    'summary': """
        Added a Field On Sale Order Named User Picking Type""",

    'description': """
        Added a Field On Sale Order Named User Picking Type
        1- When Confirm The Sale Order This Field This Field Will be Populated On Delivery Order
        2- It has Two Values 
            o- Self Picking
            o- Deliver to Customer
    """,

    'author': "Viltco",
    'website': "http://www.viltco.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Sales',
    'version': '14.0.0.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail', 'sale', 'stock', 'product_article_finish_no'],

    # always loaded
    'data': [
        'views/picking_selection_views.xml',
    ],

}
