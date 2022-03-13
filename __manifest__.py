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
        'views/rangoautorizacion.xml'
    ]
}