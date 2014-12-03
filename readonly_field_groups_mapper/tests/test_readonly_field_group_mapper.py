# -*- coding: utf-8 -*-
#
###############################################################################
#    Authors: Nemry Jonathan
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
###############################################################################
from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.osv import orm

NAME_GROUP = 'res_groups_test_readonly'


class test_readonly_field_group(SharedSetupTransactionCase):

    _data_files = (
        'data/res_groups.xml',
    )

    _module_ns = 'readonly_field_groups_mapper'

    def setUp(self):
        super(test_readonly_field_group, self).setUp()

        self.mapper_obj = self.env['readonly.field.group.mapper']

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_unicity_mapper(self):
        model = 'res.partner'
        field = 'phone'
        groups = 'base.group_portal'
        vals = {
            'model': model,
            'field': field,
            'groups': groups,
        }
        self.mapper_obj.create(vals)
        self.assertRaises(orm.except_orm, self.mapper_obj.create, vals)
        vals['model_mode'] = 'customer'
        self.mapper_obj.create(vals)
        self.assertRaises(orm.except_orm, self.mapper_obj.create, vals)

    def test_get_groups(self):
        """
        test cases:d
        """
        model = 'res.partner'
        field = 'phone'
        self.assertFalse(self.mapper_obj.get_groups(model, field),
                         'Should not find groups')
        groups = 'base.group_portal'
        vals = {
            'model': model,
            'model_mode': 'customer',
            'field': field,
            'groups': groups,
        }
        ctx = self.env.context.copy()
        ctx['model_mode'] = 'customer'
        self.mapper_obj.create(vals)
        self.assertEqual(self.mapper_obj.with_context(ctx).get_groups(
            model, field), groups, 'Should be the same group')
