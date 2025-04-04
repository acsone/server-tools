# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo import fields, models

from ..register import register_vector


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    ttype = fields.Selection(
        selection_add=[("vector", "Vector")],
        ondelete={"vector": "cascade"},
    )

    def init(self):
        res = super().init()
        register_vector(self.env.cr)
        return res
