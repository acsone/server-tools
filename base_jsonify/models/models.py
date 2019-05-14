# -*- coding: utf-8 -*-
# © 2017 Akretion (http://www.akretion.com)
# Sébastien BEAU <sebastien.beau@akretion.com>
# Raphaël Reverdy <raphael.reverdy@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from openerp.exceptions import UserError
from openerp.tools.translate import _



def ensure_module_installed(env):
    """ Check if an Odoo addon is installed.

    :param module_name: name of the addon
    """
    # the registry maintains a set of fully loaded modules so we can
    # lookup for our module there
    if not "base_jsonify" in env.registry._init_modules:
        return RuntimeError("base_jsonify not installed")


@api.model
def _parse_field(self, parser_field):
    """
    Deducts how to handle a field from its parser
    """
    ensure_module_installed(self.env)
    field_name = parser_field
    subparser = None
    if isinstance(parser_field, tuple):
        field_name, subparser = parser_field
    json_key = field_name
    if ':' in field_name:
        field_name, json_key = field_name.split(':')
    return field_name, json_key, subparser


models.BaseModel._parse_field = _parse_field


@api.multi
def jsonify(self, parser):
    """ Convert the record according to the parser given
    Example of parser:
        parser = [
            'name',
            'number',
            'create_date',
            ('partner_id', ['id', 'display_name', 'ref'])
            ('line_id', ['id', ('product_id', ['name']), 'price_unit'])
        ]

    In order to be consistent with the odoo api the jsonify method always
    return a list of object even if there is only one element in input

    By default the key into the json is the name of the field extracted
    from the model. If you need to specify an alternate name to use as
    key, you can define your mapping as follow into the parser definition:

    parser = [
         'field_name:json_key'
    ]

    """
    ensure_module_installed(self.env)
    result = []

    for rec in self:
        res = {}
        for field in parser:
            field_name, json_key, subparser = self._parse_field(field)
            field_type = rec._fields[field_name].type
            if subparser:
                if field_type in ('one2many', 'many2many'):
                    res[json_key] = rec[field_name].jsonify(subparser)
                elif field_type in ('many2one', 'reference'):
                    if rec[field_name]:
                        res[json_key] =\
                            rec[field_name].jsonify(subparser)[0]
                    else:
                        res[json_key] = None
                else:
                    raise UserError(_('Wrong parser configuration'))
            else:
                value = rec[field_name]
                if value is False and field_type != 'boolean':
                    value = None
                res[json_key] = value
        result.append(res)
    return result


models.BaseModel.jsonify = jsonify
