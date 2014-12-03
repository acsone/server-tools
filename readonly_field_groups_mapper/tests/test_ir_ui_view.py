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
from lxml import etree
from anybox.testing.openerp import SharedSetupTransactionCase
from openerp.addons.readonly_field_groups.models.ir_ui_view import MODIFIER

NAME_GROUP = 'res_groups_test_readonly'


class test_ir_ui_view(SharedSetupTransactionCase):

    _data_files = (
        'data/res_groups.xml',
    )

    _module_ns = 'readonly_field_groups_mapper'

    def setUp(self):
        super(test_ir_ui_view, self).setUp()

        self.mapper_obj = self.registry['readonly.field.group.mapper']
        self.view_obj = self.registry['ir.ui.view']
        self.res_group_obj = self.registry['res.groups']
        self.res_partner_obj = self.registry['res.partner']
        self.res_users_obj = self.registry['res.users']

        self.registry('ir.model').clear_caches()
        self.registry('ir.model.data').clear_caches()

    def test_postprocess(self):
        """
        test cases:
        this test is based on a field that is not `readonly` by default. In
        this case: `phone` from `res.partner` form

        * create a readonly.field.groups.mapper object for model/field/groups
            and check that field is readonly
        """
        cr, uid = self.cr, self.uid
        context = self.res_users_obj.context_get(cr, uid)
        full_group_name = '%s.%s' % (self._module_ns, NAME_GROUP)
        field, model = 'phone', 'res.partner'

        vals = {
            'model': model,
            'field': field,
            'groups': full_group_name,
        }
        self.mapper_obj.create(cr, uid, vals, context=context)

        view_id = self.ref('base.view_partner_form')
        view_values = self.view_obj.read(
            cr, uid, view_id, fields=['arch', 'model'], context=context)
        arch_form = view_values['arch']
        model_form = view_values['model']
        root = etree.fromstring(arch_form)
        fax_node = root.find('.//field[@name="fax"]')
        fax_node.set(MODIFIER, full_group_name)

        xarch = self.view_obj.postprocess_and_fields(
            cr, uid, model_form, root, view_id,
            context=context)[0]

        root = etree.fromstring(xarch)
        phone_node = root.find('.//field[@name="phone"]')
        fax_node = root.find('.//field[@name="fax"]')
        self.assertTrue(phone_node.get('readonly'),
                        'This field should now be "readonly=1"')
        self.assertTrue(fax_node.get('readonly'),
                        'This field should now be "readonly=1"')
