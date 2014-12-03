# -*- coding: utf-8 -*-
##############################################################################
#
#    Authors: Nemry Jonathan
#    Copyright (c) 2014 Acsone SA/NV (http://www.acsone.eu)
#
#    WARNING: This program as such is intended to be used by professional
#    programmers who take the whole responsibility of assessing all potential
#    consequences resulting from its eventual inadequacies and bugs.
#    End users who are looking for a ready-to-use solution with commercial
#    guarantees and support are strongly advised to contact a Free Software
#    Service Company.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp import models, fields, api, tools, _
from openerp.exceptions import Warning


class readonly_field_group_mapper(models.Model):

    _name = 'readonly.field.group.mapper'
    _description = 'Readonly Field Group Mapper'
    _rec_name = 'model'

    model = fields.Char(string='Model', required=True)
    model_mode = fields.Char(string='Mode')
    field = fields.Char(string='Field', required=True)
    groups = fields.Char(string='Groups', required=True)

    @api.one
    @api.constrains('model', 'model_mode', 'field')
    def _check_uniq_mapper(self):
        domain = [
            ('model', '=', self.model),
            ('model_mode', '=', self.model_mode),
            ('field', '=', self.field)]
        if len(self.search(domain)) > 1:
            raise Warning(
                _('Only One "Mapper" for model/model_mode/field is Allowed'))

    @api.cr_uid_context
    @tools.ormcache_context(accepted_keys=('model_mode',))
    def get_groups(
            self, cr, uid, model, field, context=None):
        """
        Search after a mapper record that match with model/field

        :type: model: char
        :param model: model to search after
        :type: field: char
        :param model: field associated to the model
        :rtype: char/boolean
        :rparam: groups value for the found record or False if no match

        **Note**
        context could contain a key 'model_mode' that specifies the way the
        model is used. ie: res.partner is used as supplier and customer but for
        other concept too.
        """
        context = context or {}
        model_mode = context.get('model_mode', False)
        sql_order = """ SELECT groups
            FROM %s
            WHERE model = %%s AND field=%%s
            AND model_mode """
        sql_order += model_mode and "= '%s'" % model_mode or "is NULL"
        cr.execute(sql_order % self._table, (model, field))

        r = [x[0] for x in cr.fetchall()]
        return r and r[0] or r

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, vals):
        """
        Invalidate cache
        """
        res = super(readonly_field_group_mapper, self).create(vals)
        self.get_groups.clear_cache(self)
        return res

    @api.multi
    def write(self, vals):
        """
        Invalidate cache
        """
        res = super(readonly_field_group_mapper, self).write(vals)
        self.get_groups.clear_cache(self)
        return res

    @api.multi
    def unlink(self):
        """
        Invalidate cache
        """
        res = super(readonly_field_group_mapper, self).unlink()
        self.get_groups.clear_cache(self)
        return res
