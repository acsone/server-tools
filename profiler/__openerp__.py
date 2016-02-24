# coding: utf-8
# ============================================================================
#                                                                             =
#    profiler module for OpenERP, cProfile integration for Odoo/OpenERP
#    Copyright (C) 2014 Anybox <http://anybox.fr>
#                                                                             =
#    This file is a part of profiler
#                                                                             =
#    profiler is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License v3 or later
#    as published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#                                                                             =
#    profiler is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License v3 or later for more details.
#                                                                             =
#    You should have received a copy of the GNU Affero General Public License
#    v3 or later along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#                                                                             =
# =============================================================================
{
    'name': 'profiler',
    'version': '8.0.1.0.0',
    'category': 'devtools',
    'author': 'Odoo Community Association (OCA),Georges Racinet,Vauxoo',
    'website': 'https://odoo-community.org,'
    'http://anybox.fr,https://www.vauxoo.com/',
    'depends': ['base', 'web'],
    'images': [
        'doc/static/player.png'
        'doc/static/start_profiling.png',
        'doc/static/stop_profiling.png',
        'doc/static/dump_stats.png',
        'doc/static/clear_stats.png',
    ],
    'data': [
        'security/group.xml',
        'views/profiler.xml'
    ],
    'qweb': [
        'static/src/xml/player.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'AGPL-3',
    'post_load': 'post_load',
}
