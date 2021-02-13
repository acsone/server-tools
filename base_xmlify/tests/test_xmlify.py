# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from .common import TestXmlIrExports


class TestXmlify(TestXmlIrExports):
    """TODO: Unit tests for the various submethods."""

    def test_module_filter_fields(self):
        # given
        record = self.demo_export
        export_data_all = self.get_fresh_export_data()

        # when
        all_fields = record._get_export_fields(record, export_data_all)

        # then  # we only get the relevant fields
        expected = {"default_xml_export", "export_fields", "name", "resource"}
        self.assertEqual({fn for fn, f in all_fields}, expected)

        # given
        export_data_module = self.get_fresh_export_data()
        export_data_module["module"] = self.module_base

        # when
        module_fields = record._get_export_fields(record, export_data_module)

        # then  # default_xml_export is filtered out
        module_expected = {"export_fields", "name", "resource"}
        self.assertEqual({fn for fn, f in module_fields}, module_expected)
