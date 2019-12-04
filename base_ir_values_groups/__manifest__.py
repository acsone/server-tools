# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    'name': 'Add groups on ir.values',
    'description': """
        Add groups on ir.values to hide them.""",
    'version': '10.0.1.0.0',
    'license': 'AGPL-3',
    'author': 'ACSONE SA/NV',
    'category': 'Base',
    'website': 'https://acsone.eu/',
    'depends': [
        'base',
    ],
    'data': [
        'security/ir_values.xml',
        'views/ir_values.xml',
    ],
}
