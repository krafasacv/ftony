# -*- coding: utf-8 -*-
{
    'name': "pos_price_min",

    'summary': """
        Agrega la validación del precio minimo en las listas""",

    'description': """
        Agrega el campo de precio minimo a la listas de precios
    """,

    'author': "KRA-FA SA DE CV",
    'website': "http://www.krafa.com.mx",

    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
