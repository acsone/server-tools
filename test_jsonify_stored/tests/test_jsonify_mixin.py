# Copyright 2020 ACSONE SA/NV.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.tools import mute_logger

from .common import TestJsonifyMixin


class TestJsonifyExport(TestJsonifyMixin):
    def jsonify(self, record):
        parser = self.export.get_json_parser()
        return record.jsonify(parser)[0]

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_write_export_fields(self):
        # given # let's start with everything computed
        self.assertEqual(self.record_1.jsonify_data, self.jsonify(self.record_1))
        self.assertEqual(self.record_2.jsonify_data, self.jsonify(self.record_2))
        last_line = self.export.export_fields[-1]
        name = last_line.name.replace("/", ".")

        # when  # we remove an export line from the
        self.export.export_fields = self.export.export_fields[:-1]

        # then  # everything has been recomputed
        self.assertTrue(all(name not in d for d in self.records.mapped("jsonify_data")))

    @mute_logger("odoo.addons.queue_job.models.base")
    def test_create_write_unlink_export_line(self):
        # given
        self.assertEqual(self.record_1.jsonify_data, self.jsonify(self.record_1))
        self.assertEqual(self.record_2.jsonify_data, self.jsonify(self.record_2))

        # when  # we modify an export line
        user_line = self.env.ref("test_jsonify_stored.model_export_line_user")
        user_line.name = "user_id/name"

        # then  # everything was recomputed
        self.assertEqual(self.record_1.jsonify_data, self.jsonify(self.record_1))
        self.assertEqual(self.record_2.jsonify_data, self.jsonify(self.record_2))
        # and we modified the model's depends
        field_depends = self.record_2._fields["jsonify_data_trigger"].depends
        model_depends = self.record_2._jsonify_get_export_depends()
        self.assertEqual(set(field_depends), set(model_depends))

        # when
        self.user_2.name = "newname"  # it's now part of the export

        self.assertEqual(self.record_2.jsonify_data, self.jsonify(self.record_2))

        # when  # we create an export line
        new_user_line = user_line.copy({"name": "user_id/create_date"})

        # then  # everything was recomputed
        self.assertEqual(self.record_1.jsonify_data, self.jsonify(self.record_1))
        self.assertEqual(self.record_2.jsonify_data, self.jsonify(self.record_2))

        # when  # we remove an export line
        new_user_line.unlink()

        # then  # everything was recomputed
        self.assertEqual(self.record_1.jsonify_data, self.jsonify(self.record_1))
        self.assertEqual(self.record_2.jsonify_data, self.jsonify(self.record_2))
