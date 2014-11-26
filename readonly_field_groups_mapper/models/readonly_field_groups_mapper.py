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
from openerp import models, fields, api, tools


class readonly_field_group_mapper(models.Model):

    _name = 'readonly.field.group.mapper'
    _description = 'Readonly Field Group Mapper'
    _rec_name = 'model'

    model = fields.Char(string='Model', required=True)
    field = fields.Char(string='Field', required=True)
    groups = fields.Char(string='Groups', required=True)

    _sql_constraints = [
        ('mapper_uniq', 'unique(model, field)',
         'Only one Mapper by model/field')]

    @api.model
    @tools.ormcache()
    def get_groups(self, model, field):
        """
        Search after a mapper record that match with model/field

        :type: model: char
        :param model: model to search after
        :type: field: char
        :param model: field associated to the model
        :rtype: char/boolean
        :rparam: groups value for the found record or False if no match
        """
        mapper_id = self.search([('model', '=', model), ('field', '=', field)])
        if mapper_id:
            return mapper_id[0].groups
        return False

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
    def write(self, ids, vals):
        """
        Invalidate cache
        """
        res = super(readonly_field_group_mapper, self).write(ids, vals)
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
