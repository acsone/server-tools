# Copyright 2020 ACSONE
# Nans Lefebvre <nans.lefebvre@acsone.eu>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Base xmlify",
    "summary": "Base module that provide an xmlify method on all models",
    "version": "12.0.1.0.0",
    "category": "Uncategorized",
    "website": "https://github.com/OCA/server-tools",
    "author": "Acsone, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "installable": True,
    "depends": ["base_ir_export"],
    "external_dependencies": {"python": ["slugify"]},
    "data": [
        "views/ir_exports_view.xml",
        "wizard/xml_exports_view.xml",
        "wizard/ir_exports_wizard.xml",
    ],
    "demo": ["demo/export.xml"],
}
