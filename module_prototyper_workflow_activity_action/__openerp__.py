# -*- coding: utf-8 -*-
# Copyright 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
{
    'name': "Module prototyper extension for workflow activity",
    'summary': """
        Extend the module prototyper to export Workflow activity action""",
    'author': 'ACSONE SA/NV',
    'website': "http://acsone.eu",
    'category': 'Others',
    'version': '9.0.1.0.0',
    'license': 'AGPL-3',
    'depends': [
        'module_prototyper',
        'workflow_activity_action',
    ],
    'data': [
        'views/module_prototyper_view.xml'
    ],
}
