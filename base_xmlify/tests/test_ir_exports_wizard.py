# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestXmlIrExports


class TestCreateExportWizard(TestXmlIrExports):
    def test_create_default_export(self):
        """When we create a new default mxl export, others should be un-defaulted"""
        # given
        self.demo_export.default_xml_export = True
        self.wizard.default_xml_export = True

        # when
        export = self.wizard._create_ir_export()

        # then
        self.assertTrue(export.default_xml_export)
        self.assertFalse(self.demo_export.default_xml_export)
