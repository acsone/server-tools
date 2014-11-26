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
from openerp.addons.readonly_field_groups.models.ir_ui_view import MODIFIER


class view(orm.Model):

    _inherit = 'ir.ui.view'

    def postprocess(self, cr, user, model, node, view_id, in_tree_view,
                    model_fields, context=None):
        """
        Override `postprocess` to integrate a new behavior that allows to set
        the MODIFIER attribute of `readonly_field_groups` with a list of groups
        depending of the `readonly.field.group.mapper`
        """
        if context is None:
            context = {}
        if node.tag == 'field' and not node.get(MODIFIER):
            mapper_obj = self.pool['readonly.field.group.mapper']
            groups = mapper_obj.get_groups(
                cr, user, model, node.get('name'), context=context)
            if groups:
                node.set(MODIFIER, groups)

        return super(view, self).postprocess(
            cr, user, model, node, view_id, in_tree_view, model_fields,
            context=context)
