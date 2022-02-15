{
    'name': 'import_logistic Module',
    'version': '0.2',
    'category': 'accouting',
    'license': "AGPL-3",
    'summary': " ",
    'author': 'Itech Reosurces',
    'company': 'ItechResources',
    'depends': [
        'base',
        'account',
        'purchase',
        'stock_landed_costs',
        'product_article_finish_no',

    ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/lc_sequence.xml',
        # 'views/account_invoice.xml',
        'views/lc_view.xml',
        'reports/landed_cost.xml',
    ],
    # 'installable': True,
    # 'auto_install': False,
}
