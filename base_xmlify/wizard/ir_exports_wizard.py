from odoo import fields, models


class IrExportsWizard(models.TransientModel):
    _inherit = "ir.exports.wizard"

    default_xml_export = fields.Boolean(
        string="Default XML export.",
        default=False,
        help="If True this export will be used when exporting records to XML",
    )

    def _get_ir_export_vals(self):
        res = super(IrExportsWizard, self)._get_ir_export_vals()
        res["default_xml_export"] = self.default_xml_export
        return res

    def _create_ir_export(self):
        res = super(IrExportsWizard, self)._create_ir_export()
        domain = [("resource", "=", res.resource), ("default_xml_export", "=", True)]
        previous_defaults = self.env["ir.exports"].search(domain) - res
        previous_defaults.write({"default_xml_export": False})
        return res
