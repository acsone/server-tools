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
from openerp.osv import orm
ATTRS = 'attrs'
REQUIRED = 'required'
MODIFIER = 'modifier_field_groups'


class view(orm.Model):

    _inherit = 'ir.ui.view'

    def _has_write_access_field(
            self, cr, uid, model, field, groups, context=None):
        return self.user_has_groups(cr, uid, groups, context=context)

    def check_write_access_group(self, cr, uid, model, node, context=None):
        """
        This method will check that the current user has the required groups
        to modify the field in case where node has an attribute named
        `modifier_field_groups`
        """
        model_obj = self.pool.get(model)
        is_field = node.tag == 'field'
        name = node.get('name')

        if node.get(MODIFIER):
            if is_field:
                if not self._has_write_access_field(
                        cr, uid, model, name,
                        node.get(MODIFIER), context=context):
                    node.set('readonly', '1')
                    if ATTRS in node.attrib:
                        del(node.attrib[ATTRS])
                    if REQUIRED in node.attrib:
                        del(node.attrib[REQUIRED])
                        # avoid to remove read-only later
            del(node.attrib[MODIFIER])
            return
        # if not found into view then check into the model
        if is_field and name in model_obj._fields:
            field = model_obj._fields[name]
            groups = getattr(field, MODIFIER, False)
            if groups:
                if not self._has_write_access_field(
                        cr, uid, model, name, groups,
                        context=context):
                    node.set('readonly', '1')
        return

    def postprocess(self, cr, user, model, node, view_id, in_tree_view,
                    model_fields, context=None):
        """
        Override `postprocess` to integrate a new behavior that allows to make
        `readonly access` depending of the user's attributes
        """
        if context is None:
            context = {}

        self.check_write_access_group(cr, user, model, node, context=context)

        return super(view, self).postprocess(
            cr, user, model, node, view_id, in_tree_view, model_fields,
            context=context)
