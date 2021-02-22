# © 2020 Acsone (http://www.acsone.eu)
# Nans Lefebvre <nans.lefebvre@acsone.eu>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import uuid

from lxml.builder import E
from slugify import slugify

from odoo import api, models, tools


class Base(models.AbstractModel):
    _inherit = "base"

    def xmlify(self, export=None, module=None):
        export_data = {
            "export": {self._name: export} if export else {},  # {model_name: ir.export}
            "export_fields": {},  # {model_name: [field_name]}
            "export_list": [record for record in self],  # records needing export
            "module": module,  # top module to filter export fields
            "xml_ids": {},  # {record: xml_id} (including made-up ones)
        }
        result = []
        for record in self:
            result.append(self._xmlify_record(record, result, export_data))
        return result

    @api.model
    def _get_export(self, name, export_data):
        export = export_data["export"]
        if name not in export:
            domain = [("default_xml_export", "=", True), ("resource", "=", name)]
            default_export = self.env["ir.exports"].search(domain, limit=1)
            export[name] = default_export
        return export[name]

    @api.model
    def _get_export_fields(self, record, export_data):
        export_fields = export_data["export_fields"]
        name = record._name
        if name not in export_fields:
            export = self._get_export(name, export_data)
            if export:
                field_names = export.export_fields.mapped("name")
                field_names = [fn.split("/")[0] for fn in field_names]
            else:
                field_names = set(record._fields.keys())
            to_export = [(f, record._fields[f]) for f in field_names]
            to_export = [(fn, f) for fn, f in to_export if self._keep_field(f, export)]

            module = export_data["module"]
            if module:  # keep only fields that are in dependencies
                dps = module.upstream_dependencies(exclude_states=["uninstallable"])
                dependencies = dps.mapped("name")
                fields_from = [module.name] + dependencies
                filter_module = lambda f: f._module in fields_from  # noqa
                to_export = [(fn, f) for fn, f in to_export if filter_module(f)]
            export_fields[name] = sorted(to_export)
        return export_fields[name]

    def _keep_field(self, f, export):
        """Ignores non-stored and magic fields.
           If we are provided with an export, we only do minimal filtering.
           If there is no provided export, we can remove mail fields
           because in general these are just annoying fields.
        """
        magic = f.name in models.MAGIC_COLUMNS or f.name == "__last_update"
        keep = f.store and not magic
        if not export:
            ignore_type = f.type in ["binary"]
            ignore_modules = f._module in ["mail", "portal"]
            keep = keep and not ignore_type and not ignore_modules
        return keep

    @api.model
    def _needs_export(self, record, export_data):
        # we do export records whose xmlid start by __export__
        # TODO: choose depending on external_id/fields/module
        # i.e. if we get a record that already has an external id,
        # we might do an override to add the fields we are interested in
        export_list = export_data["export_list"]
        xmlid = record.get_xml_id().get(record.id)
        return record not in export_list and (not xmlid or "__export__" in xmlid)

    @api.model
    def _get_xml_id(self, record, export_data):
        xml_ids = export_data["xml_ids"]
        if record not in xml_ids:
            external_id = record.get_xml_id().get(record.id)
            if external_id:
                xml_ids[record] = external_id
            else:
                salt = str(uuid.uuid4())[:6]
                dn = "display_name"
                name = record[dn] if dn in record._fields else ""
                record_xml_id = "_".join([record._name, name, salt])
                xml_ids[record] = slugify(record_xml_id).replace("-", "_")
        return xml_ids[record]

    @api.model
    def _xmlify_record(self, record, result, export_data):
        xml = E.record(id=self._get_xml_id(record, export_data), model=record._name)
        fields = self._get_export_fields(record, export_data)
        for fname, field in fields:
            field_xml = self._xmlify_field(fname, field, record, result, export_data)
            xml.append(field_xml)
            # TODO breaks nice formatting...
            # comment = etree.Comment("from module {}".format(field._module))
            # comment.tail = '\n'
            # xml.append(comment)
        return xml

    @api.model
    def _xmlify_field(self, field_name, field, record, result, export_data):
        export_list = export_data["export_list"]
        value = record[field_name]
        if not value:
            return E.field(eval="False", name=field_name)
        field_dict = {"name": field_name}
        if field.type in ["many2one", "many2many", "one2many"]:
            for subrecord in value:
                if self._needs_export(subrecord, export_data):
                    export_list.append(subrecord)
                    subrecord_xml = self._xmlify_record(subrecord, result, export_data)
                    result.append(subrecord_xml)
            if field.type == "many2one":
                field_dict["ref"] = self._get_xml_id(value, export_data)
            else:
                ids = [self._get_xml_id(r, export_data) for r in value]
                eval_ids = ["ref('{}')".format(i) for i in ids]
                lids = "[" + ", ".join(eval_ids) + "]"
                field_dict["eval"] = "[(6,0," + lids + ")]"
        elif field.type == "boolean":
            field_dict["eval"] = "True"
        elif field.type == "date":
            field_dict["value"] = value.strftime(tools.DEFAULT_SERVER_DATE_FORMAT)
        elif field.type == "datetime":
            field_dict["value"] = value.strftime(tools.DEFAULT_SERVER_DATETIME_FORMAT)
        else:  # TODO: handle all field types: HTML (reference?, binary...)
            field_dict["value"] = str(value)
        if "value" in field_dict:
            xml_value = str(field_dict.pop("value"))
            return E.field(xml_value, **field_dict)
        else:
            return E.field(**field_dict)
