# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models


class IrActionsActions(models.Model):
    _inherit = "ir.actions.actions"

    is_temporary = fields.Boolean()

    @api.autovacuum
    def _gc_temporary_actions(self):
        self.search(
            [
                ("is_temporary", "=", True),
                (
                    "create_date",
                    "<",
                    fields.Datetime.now() - relativedelta(hours=1),
                ),
            ]
        ).unlink()
