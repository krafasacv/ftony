# -*- coding: utf-8 -*-
{
    'name': "POS FTONY",
    'summary': "Modificaciones para FTONY",
    'description': """AGREGA FUNCIONALIDADES AL SISTEMA A PETICIÓN DE FTONY """,
    'author': "FTONY",
    'category': 'Point of Sale',
    'version': '14.0.1',
    'depends': ['point_of_sale'],
    'data': [
        'views/sequence_ff.xml',
        'views/pos_order_to_invoice.xml',
    ],
    'qweb': [
        'static/src/xml/pos_ftony.xml',
    ]
}