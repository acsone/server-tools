# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import copy

from odoo.addons.base_ir_export.tests.common import TestIrExports


class TestXmlIrExports(TestIrExports):
    @classmethod
    def setUpClass(cls):
        super(TestXmlIrExports, cls).setUpClass()

        cls.demo_export = cls.env.ref("base_xmlify.ir_exp_user_demo")

        cls.export_data = {
            "export": {},
            "export_fields": {},
            "export_list": [],
            "module": None,
            "xml_ids": {},
        }

    def get_fresh_export_data(self):
        return copy.deepcopy(self.export_data)
