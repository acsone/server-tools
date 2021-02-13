# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests import SavepointCase


class TestIrExports(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestIrExports, cls).setUpClass()

        cls.user_admin = cls.env.ref("base.user_admin")
        cls.user_demo = cls.env.ref("base.user_demo")
        cls.users = cls.user_admin + cls.user_demo

        ir_model = cls.env["ir.model"]
        domain_user = [("model", "=", "res.users")]
        cls.model_user = ir_model.search(domain_user)
        cls.fields_user = cls.env["ir.model.fields"].search(domain_user)

        cls.model_ir_exports = ir_model.search([("model", "=", "ir.exports")])

        cls.module_base = cls.env["ir.module.module"].search([("name", "=", "base")])

        cls.export_user_test_name = "Test User Export"
        vals_wizard = {"model_id": cls.model_user.id, "name": cls.export_user_test_name}
        cls.wizard = cls.env["ir.exports.wizard"].create(vals_wizard)
