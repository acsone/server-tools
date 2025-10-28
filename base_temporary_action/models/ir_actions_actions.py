# Copyright 2025 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from dateutil.relativedelta import relativedelta

from odoo import fields, models


class IrActionsActions(models.Model):
    _inherit = "ir.actions.actions"

    is_temporary = fields.Boolean()

    def cron_remove_temporary_actions(self):
        cron = self.env.ref("base_temporary_action.remove_temporary_actions_cron")
        temporary_actions = self.search(
            [
                ("is_temporary", "=", True),
                (
                    "create_date",
                    "<",
                    datetime.now()
                    - relativedelta(**{cron.interval_type: cron.interval_number}),
                ),
            ]
        )
        temporary_actions.unlink()
