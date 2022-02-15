
{
    'name': '[10% OFF] WhatsApp Integration',
    'version': '13.0.0.0.0',
    'summary': 'Send Message/SaleOrders/Invoices/Employee Handling via just one click',
    'description': """Odoo is a fully integrated suite of business modules that encompass the traditional ERP functionality.
        Use Odoo Whatsapp Integration to send messages, SalesOrders, Quotations, Reminders, Invoices
        and Employee handling on just one click.""",
    'category': 'Contacts',
    'author': 'Dynexcel',
    'maintainer': 'Dynexcel',
    'price': 99,
    'currency': 'EUR',
    'company': 'Dynexcel',
    'website': 'https://www.dynexcel.com',
    'depends': [
        'base', "sale_management", 'hr', 'contacts', 'purchase', 'stock'
        ],
    'data': [
        'security/ir.model.access.csv',
        'views/view.xml',
        'wizard/wizard.xml',
        'wizard/message_wizard.xml',
    ],
    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': '',
}
