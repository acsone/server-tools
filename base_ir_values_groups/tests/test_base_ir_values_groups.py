# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tests.common import TransactionCase


class TestBaseIrValuesGroups(TransactionCase):

    def setUp(self):
        super(TestBaseIrValuesGroups, self).setUp()

        class DummyModel(models.Model):
            _name = 'dummy.model'

        self.DummyModel = self._init_test_model(DummyModel)

    def _init_test_model(self, model_self):
        registry = self.env.registry
        cr = self.env.cr
        model_self._build_model(registry, cr)
        model = self.env[model_self._name].with_context(todo=[])
        model._prepare_setup()
        model._setup_base(partial=False)
        model._setup_fields(partial=False)
        model._setup_complete()
        model._auto_init()
        model.init()
        model._auto_end()
        return model

    def test_groups_id_on_ir_values(self):
        IrValues = self.env['ir.values']
        ResGroups = self.env['res.groups']
        ResUsers = self.env['res.users']
        test_user = ResUsers.create({
            'name': 'test user',
            'login': 'testuser',
        })
        test_group = ResGroups.create({
            'name': 'group test',
        })
        ir_values_without_group = IrValues.create({
            'name': 'ir values without group',
            'model': 'dummy.model',
        })
        ir_values_without_group_search = IrValues.sudo(test_user.id).search([
            ('id', '=', ir_values_without_group.id)
        ])
        # ir values without groups should be accessible for all users
        self.assertEqual(
            len(ir_values_without_group_search),
            1
        )
        ir_values_with_group = IrValues.create({
            'name': 'ir values with group',
            'model': 'dummy.model',
            'groups_id': [(4, test_group.id)],
        })
        ir_values_with_group_search = IrValues.sudo(test_user.id).search([
            ('id', '=', ir_values_with_group.id)
        ])
        # ir values with groups should be accessible only to users with its
        # groups
        self.assertEqual(
            len(ir_values_with_group_search),
            0
        )
        test_user.write({
            'groups_id': [(4, test_group.id)],
        })
        ir_values_with_group_search = IrValues.sudo(test_user.id).search([
            ('id', '=', ir_values_with_group.id)
        ])
        self.assertEqual(
            len(ir_values_with_group_search),
            1
        )
