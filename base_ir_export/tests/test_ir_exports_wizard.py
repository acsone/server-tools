# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError

from .common import TestIrExports


class TestCreateExportWizard(TestIrExports):
    def test_wrong_field(self):
        domain_field = [("model", "!=", "res.users"), ("name", "=", "numbercall")]
        field = self.env["ir.model.fields"].search(domain_field, limit=1)
        self.wizard.export_field_ids = field

        with self.assertRaises(ValidationError):
            self.wizard.create_ir_export()

    def test_create_export(self):
        # given
        self.wizard.export_field_ids = self.fields_user

        # when
        export = self.wizard._create_ir_export()

        # then
        name_set = lambda r: set(r.mapped("name"))  # noqa
        self.assertEqual(name_set(export.export_fields), name_set(self.fields_user))
