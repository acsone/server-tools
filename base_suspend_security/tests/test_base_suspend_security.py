# -*- coding: utf-8 -*-
##############################################################################
#
#    This module copyright (C) 2015 Therp BV (<http://therp.nl>).
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
#
##############################################################################
from openerp import exceptions
from openerp.tools import mute_logger
from openerp.tests.common import TransactionCase
from ..base_suspend_security import BaseSuspendSecurityUid


class TestBaseSuspendSecurity(TransactionCase):

    def setUp(self):
        super(TestBaseSuspendSecurity, self).setUp()
        # tests are called before register_hook
        self.env['ir.rule']._register_hook()
        self.user = self.env.ref('base.user_demo')

    def test_base_suspend_security(self):
        user_id = self.user.id
        other_company = self.env['res.company'].create({
            'name': 'other company',
            # without this, a partner is created and mail's constraint on
            # notify_email kicks in
            'partner_id': self.env.ref('base.partner_demo').id,
        })
        # be sure what we try is forbidden
        with self.assertRaises(exceptions.AccessError):
            with mute_logger('openerp.addons.base.ir.ir_model'):
                self.env.ref('base.user_root').sudo(user_id).name = 'test'
        with self.assertRaises(exceptions.AccessError):
            with mute_logger('openerp.addons.base.ir.ir_model'):
                other_company.sudo(user_id).name = 'test'
        # this tests ir.model.access
        self.env.ref('base.user_root').sudo(user_id).suspend_security().write({
            'name': 'test'})
        self.assertEqual(self.env.ref('base.user_root').name, 'test')
        self.assertEqual(self.env.ref('base.user_root').write_uid.id, user_id)
        # this tests ir.rule
        other_company.sudo(user_id).suspend_security().write({'name': 'test'})
        self.assertEqual(other_company.name, 'test')
        self.assertEqual(other_company.write_uid.id, user_id)
        # this tests if _normalize_args conversion works
        self.env['res.users'].browse(
            self.env['res.users'].suspend_security().env.uid)
        # check equality, that's relevant for picking the right environment
        self.assertNotEqual(BaseSuspendSecurityUid(42), 42)
        self.assertNotEqual(
            BaseSuspendSecurityUid(42), BaseSuspendSecurityUid(43),
        )
        self.assertEqual(
            BaseSuspendSecurityUid(42), BaseSuspendSecurityUid(42),
        )

    def test_changing_access_right(self):
        env = self.env(user=self.user.id)
        # we add the access right on company
        group_manager_id = self.ref('base.group_erp_manager')
        self.user.write({'groups_id': [(4, group_manager_id)]})
        env['ir.model.access'].check('res.company', mode='write')
        # we remove the access right on company
        self.user.write({'groups_id': [(3, group_manager_id)]})
        with self.assertRaises(exceptions.AccessError):
            env['ir.model.access'].check('res.company', mode='write')
