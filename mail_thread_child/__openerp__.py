# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mail_thread_child,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mail_thread_child is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     mail_thread_child is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with mail_thread_child.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': "Mail Thread Child",

    'summary': """
        Track on child object""",
    'author': "ACSONE SA/NV",
    'website': "http://acsone.eu",
    'category': 'Tools',
    'version': '8.0.1.0.0',
    'license': 'AGPL-3',

    'depends': [
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
    ],
}
