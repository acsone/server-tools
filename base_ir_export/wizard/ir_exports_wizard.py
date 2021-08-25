# -*- coding: utf-8 -*-
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class IrExportsWizard(models.TransientModel):
    _name = "ir.exports.wizard"
    _description = "Create an Export"

    model_id = fields.Many2one(comodel_name="ir.model")
    model_name = fields.Char(
        string="Model Name", related="model_id.model", readonly=True,
    )
    name = fields.Char()
    export_field_ids = fields.Many2many(comodel_name="ir.model.fields",)

    @api.onchange("model_id")
    def _onchange_model_id(self):
        return {"domain": {"export_field_ids": [("model_id", "=", self.model_id.id)]}}

    def create_ir_export(self):
        self._create_ir_export()

    def _create_ir_export(self):
        self.ensure_one()
        model = self.env[self.model_name]
        fields = self.export_field_ids
        missing_fields = [f for f in fields if f.name not in model._fields]
        if missing_fields:
            message = "The following fields are not defined on model {}: {}"
            raise ValidationError(_(message).format(self.model_name, missing_fields))
        return self.env["ir.exports"].create(self._get_ir_export_vals())

    def _get_ir_export_vals(self):
        field_vals = [self._get_ir_export_field_vals(f) for f in self.export_field_ids]
        return {
            "name": self.name or _("{} Export").format(self.model_name),
            "resource": self.model_name,
            "export_fields": field_vals,
        }

    def _get_ir_export_field_vals(self, field):
        return (0, 0, {"name": field.name})
