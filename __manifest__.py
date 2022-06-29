# -*- coding: utf-8 -*-
{
    'name' : 'Importadora Solares',
    'summary':"""
        Implementacion Importadora Solares
    """,
    'author':'Alexander Paiz/Lester Paiz',
    'category': 'General',
    'version' : '1.0.0',
    'depends': [
        "sale"
    ],
    'data': [
        'security/solares_security.xml',
        'security/ir.model.access.csv',
        'views/menu_view.xml',
        'views/rangoautorizacion.xml',
        'views/product_category.xml',
        'views/marca.xml',
        'views/product_template.xml',
        'views/sale_order.xml',
        'wizard/autorizacion_pendiente.xml'
    ]
}