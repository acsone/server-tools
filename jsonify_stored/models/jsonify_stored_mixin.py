# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models

from odoo.addons.queue_job.job import identity_exact, job

QUEUE_CHANNEL = "root.jsonify.stored"


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
        self._create_recompute_jobs()
        for record in self:
            record.jsonify_data_trigger = True

    @job(default_channel=QUEUE_CHANNEL)
    @api.depends("jsonify_data_trigger")
    def _compute_jsonify_data(self):
        if self:
            parser = self._jsonify_get_export().get_json_parser()
            data_list = self.jsonify(parser)
            for record, data in zip(self, data_list):
                record.jsonify_data = data

    @api.model
    def _get_batch_size(self):
        key = self._name + ".batch_size"
        return self.env["ir.config_parameter"].sudo().get_param(key, 100)

    def _create_recompute_jobs(self):
        batch_size = self._get_batch_size()
        desc = _("Recompute stored json.")
        for i in range(0, len(self), batch_size):
            records = self[i : i + batch_size]
            delayed = records.with_delay(description=desc, identity_key=identity_exact)
            delayed._compute_jsonify_data()
