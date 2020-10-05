# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class JsonifyStored(models.AbstractModel):
    """Stores the data to export.
       When inheriting this class, _export_xmlid should be set with an export xml_id.
       Note that this xml_id has to exist before the model init,
       i.e. either be in a dependency module, or created in a pre_init_hook
       (however it's fine to modify an existing one in the module data).
    """

    _name = "jsonify.stored.mixin"
    _description = "Stores json data"

    _export_xmlid = ""  # override this key when inheriting this mixin

    jsonify_data = fields.Serialized(
        string="Jsonify: Data",
        compute="_compute_jsonify_data",
        readonly=True,
        store=False,
        help="Json export value. Always up-to-date, triggers a recompute if necessary.",
    )
    jsonify_data_trigger = fields.Boolean(
        string="Jsonify: Trigger",
        compute="_compute_jsonify_data_trigger",
        default=True,
        readonly=True,
        store=True,
        help="Technical field. Always True.",
    )
    jsonify_data_todo = fields.Boolean(
        string="Jsonify: Todo",
        default=True,
        readonly=True,
        store=True,
        help="If True, the stored json data needs to be recomputed.",
    )
    jsonify_data_stored = fields.Serialized(
        string="Jsonify: Stored",
        compute="_compute_jsonify_data_stored",
        readonly=True,
        store=True,
        help="Last computed Json export value. Might not be up to date.",
    )

    @api.model
    def _jsonify_get_export(self):
        xml_id = self._export_xmlid
        return self.env.ref(xml_id) if xml_id else self.env["ir.exports"]

    @api.model
    def _jsonify_get_export_depends(self):
        export_field_names = self._jsonify_get_export().export_fields.mapped("name")
        return tuple(fn.replace("/", ".") for fn in export_field_names)

    @api.depends(lambda self: self._jsonify_get_export_depends())
    def _compute_jsonify_data_trigger(self):
        for record in self:
            record.jsonify_data_todo = True
            record.jsonify_data_trigger = True

    def _compute_jsonify_data_stored(self):
        if self:
            parser = self._jsonify_get_export().get_json_parser()
            data_list = self.jsonify(parser)
            for record, data in zip(self, data_list):
                record.jsonify_data_stored = data
                record.jsonify_data_todo = False

    @api.depends("jsonify_data_todo", "jsonify_data_stored")
    def _compute_jsonify_data(self):
        self.filtered("jsonify_data_todo")._compute_jsonify_data_stored()
        for record in self:
            record.jsonify_data = record.jsonify_data_stored

    @api.model
    def cron_recompute(self, limit=None):
        records = self.search([("jsonify_data_todo", "=", True)], limit=limit)
        records._compute_jsonify_data_stored()
