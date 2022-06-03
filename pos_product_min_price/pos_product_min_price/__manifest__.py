# -*- coding: utf-8 -*-

{
    'name': 'Min Price POS',
    'summary': '',
    'description': '''
    User can not sale product below minumum price set in the product form.
    ''',
    'author': 'IT Admin',
    'version': '14.1',
    'category': 'Sales/Point of Sale',
    'depends': [
        'product','point_of_sale'
    ],
    'data': [
        'views/product_pricelist.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'application': False,
    'license': 'AGPL-3',
}
