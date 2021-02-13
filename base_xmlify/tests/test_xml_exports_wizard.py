# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import os

from odoo import tools

from .common import TestXmlIrExports


class TestXmlExportWizard(TestXmlIrExports):
    def test_export_import(self):
        # given
        name = "demo_export.xml"
        destination = "/tmp/"
        vals_wizard = {
            "domain": [("id", "in", self.users.ids)],
            "model_id": self.model_user.id,
            "destination": destination,
            "filename": name,
        }
        wizard = self.env["ir.exports.xml.wizard"].create(vals_wizard)

        # when
        wizard.export_to_xml()

        # then
        with open(os.path.join(destination, name), "rb") as fp:
            res = tools.convert_xml_import(self.env.cr, "base_xmlify", fp)
        self.assertTrue(res, "Data could not be loaded.")
