# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd. (support@serpentcs.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import etree

import odoo.tools as tools
from odoo import api, models


class MassEditingWizard(models.TransientModel):
    _name = 'mass.editing.wizard'

    def __init__(self):
        super(MassEditingWizard, self).__init__()
        self._all_fields = {}

    @api.model
    def _get_action_selection(self, field):
        selection = [('set', 'Set')]
        if field.ttype == "many2many":
            selection.append(('remove_m2m', 'Remove'))
        else:
            selection.append(('remove', 'Remove'))

    @api.model
    def _build_action_field(self, field, field_info):
        """
        Build the 'Add/Remove...' selection
        :param field:
        :param field_info:
        :return:
        """
        self._all_fields["selection__" + field.name] = {
            'type': 'selection',
            'string': field_info[field.name]['string'],
            'selection': self._get_action_selection(field)
        }

    def _get_field_options(self, field, field_info):
        """
        Get field specific options
        :param field:
        :param field_info:
        :return:
        """
        options = {
            'type': field.ttype,
            'string': field.field_description,
            'views': {},
        }
        if field.ttype == "many2many":
            options = field_info[field.name]
        elif field.ttype == "char":
            options.update({'size': field.size or 256})
        elif field.ttype == "selection":
            options.update({'selection': field_info[field.name]['selection']})
        elif field.ttype in ("many2one", "one2many"):
            options.update({'relation': field.relation})
        return options

    def _build_field(self, field, field_info):
        """
        Build field itself
        :param field:
        :param field_info:
        :return:
        """
        self._all_fields[field.name] = self._get_field_options(
            field, field_info)

    def _get_values_xml_options(self, field):
        options = {
            'name': field.name,
            'colspan': '4',
            'nolabel': '1',
            'attrs': ("{'invisible':[('selection__" +
                      field.name + "', '=', 'remove')]}"),
        }
        if field.ttype == "many2many":
            options.update({
                'colspan': '6',
                'attrs': ("{'invisible': [('selection__" + field.name + "', '=', 'remove_m2m')]}"),})
        elif field.ttype in ("one2many", "text"):
            options.update({'colspan': '6'})
        return options

    def _get_action_xml_options(self, field):
        options = {
            'colspan': '2',
            'nolabel': '1',
            'name': "selection__" + field.name,
        }
        if field.ttype in ("many2many", "text"):
            options.update({'colspan': '6'})
        elif field.ttype == "one2many":
            options.update({'colspan': '4'})

    def _build_xml(self, field, xml_group):
        """
        Build the sub xml elements from parent node
        For many2many and text ones, build them inside another group
        :param field:
        :param field_info:
        :param xml_group:
        :return:
        """
        if field.ttype in ("many2many", "text"):
            xml_group = etree.SubElement(xml_group, "group", {
                'colspan': '6',
                'col': '6',
            })
            etree.SubElement(xml_group, 'separator', {
                'string': self._all_fields[field.name]['string'],
                'colspan': '6',
            })
        etree.SubElement(
            xml_group, 'field', self._get_action_xml_options(field))
        etree.SubElement(
            xml_group, 'field', self._get_values_xml_options(field))


    @api.model
    def _build_fields(self, field, field_info, xml_group):
        """
        Build the wizard form :
           * Build field itself
           * Build the action field (Set/Remove...)
           * Build the xml view
        :param field:
        :param field_info:
        :param xml_group:
        :return:
        """
        self._build_field(field, field_info)
        self._build_action_field(field, field_info)
        self._build_xml(field, xml_group)

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False,
                        submenu=False):
        result =\
            super(MassEditingWizard, self).fields_view_get(view_id=view_id,
                                                           view_type=view_type,
                                                           toolbar=toolbar,
                                                           submenu=submenu)
        context = self._context
        if context.get('mass_editing_object'):
            mass_obj = self.env['mass.object']
            editing_data = mass_obj.browse(context.get('mass_editing_object'))
            xml_form = etree.Element('form', {
                'string': tools.ustr(editing_data.name)
            })
            xml_group = etree.SubElement(xml_form, 'group', {
                'colspan': '6',
                'col': '6',
            })
            etree.SubElement(xml_group, 'label', {
                'string': '',
                'colspan': '2',
            })
            xml_group = etree.SubElement(xml_form, 'group', {
                'colspan': '6',
                'col': '6',
            })
            model_obj = self.env[context.get('active_model')]
            field_info = model_obj.fields_get()
            for field in editing_data.field_ids:
                self._build_field(field, field_info, xml_group)
            etree.SubElement(xml_form, 'separator', {
                'string': '',
                'colspan': '6',
                'col': '6',
            })
            xml_group3 = etree.SubElement(xml_form, 'footer', {})
            etree.SubElement(xml_group3, 'button', {
                'string': 'Apply',
                'class': 'btn-primary',
                'type': 'object',
                'name': 'action_apply',
            })
            etree.SubElement(xml_group3, 'button', {
                'string': 'Close',
                'class': 'btn-default',
                'special': 'cancel',
            })
            root = xml_form.getroottree()
            result['arch'] = etree.tostring(root)
            result['fields'] = self._all_fields
        return result

    @api.model
    def create(self, vals):
        active_model = self._context.get('active_model')
        active_ids = self._context.get('active_ids')
        if active_model and active_ids:
            model_obj = self.env[active_model]
            model_field_obj = self.env['ir.model.fields']
            translation_obj = self.env['ir.translation']
            values = {}
            for key, val in vals.items():
                if key.startswith('selection_'):
                    split_key = key.split('__', 1)[1]
                    if val == 'set':
                        values.update({split_key: vals.get(split_key, False)})
                    elif val == 'remove':
                        values.update({split_key: False})
                        # If field to remove is translatable,
                        # its translations have to be removed
                        model_field = model_field_obj.search([
                            ('model', '=', active_model),
                            ('name', '=', split_key)])
                        if model_field and model_field.translate:
                            translation_ids = translation_obj.search([
                                ('res_id', 'in', active_ids),
                                ('type', '=', 'model'),
                                ('name', '=', u"{0},{1}".format(
                                    active_model,
                                    split_key))])
                            translation_ids.unlink()

                    elif val == 'remove_m2m':
                        values.update({split_key: [(5, 0, [])]})
                    elif val == 'add':
                        m2m_list = []
                        for m2m_id in vals.get(split_key, False)[0][2]:
                            m2m_list.append((4, m2m_id))
                        values.update({split_key: m2m_list})
            if values:
                model_obj.browse(active_ids).write(values)
        return super(MassEditingWizard, self).create({})

    @api.multi
    def action_apply(self):
        return {'type': 'ir.actions.act_window_close'}

    def read(self, fields, load='_classic_read'):
        """ Without this call, dynamic fields build by fields_view_get()
            generate a log warning, i.e.:
            odoo.models:mass.editing.wizard.read() with unknown field 'myfield'
            odoo.models:mass.editing.wizard.read()
                with unknown field 'selection__myfield'
        """
        real_fields = fields
        if fields:
            # We remove fields which are not in _fields
            real_fields = [x for x in fields if x in self._fields]
        return super(MassEditingWizard, self).read(real_fields, load=load)
