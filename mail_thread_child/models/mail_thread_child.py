# -*- coding: utf-8 -*-
##############################################################################
#
#     This file is part of mail_thread_child,
#     an Odoo module.
#
#     Copyright (c) 2015 ACSONE SA/NV (<http://acsone.eu>)
#
#     mail_thread_child is free software:
#     you can redistribute it and/or modify it under the terms of the GNU
#     Affero General Public License as published by the Free Software
#     Foundation,either version 3 of the License, or (at your option) any
#     later version.
#
#     mail_thread_child is distributed
#     in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
#     even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR
#     PURPOSE.  See the GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with mail_thread_child.
#     If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, api, _
from openerp.osv.orm import browse_record, browse_null
import logging

_logger = logging.getLogger(__name__)

MODE = [
    ('create', 'Created'),
    ('write', 'Changed'),
    ('unlink', 'Removed'),
]

DICT_MODE = {x[0]: x[1] for x in MODE}


class mail_thread_child(models.Model):
    _name = 'mail.thread.child'
    _tracked_parent = []
    _track = {}
    _track_name = ''

    @api.model
    @api.returns('self', lambda value: value.id)
    def create(self, values):
        if self.env.context.get('tracking_disable'):
            return super(mail_thread_child, self).create(values)
        thread = super(mail_thread_child, self).create(values )
        # track values
        track_ctx = dict(self.env.context)
        if 'lang' not in track_ctx:
            track_ctx['lang'] = self.env['res.users']\
                .browse([self._uid])[0].lang
        if not self.env.context.get('mail_notrack'):
            tracked_fields = self.with_context(track_ctx)\
                ._get_tracked_fields(values.keys())
            if tracked_fields:
                initial_values = {thread.id: dict.fromkeys(tracked_fields,
                                                           False)}
                thread.with_context(track_ctx)\
                    .message_track(tracked_fields, initial_values,
                                   mode='create')
        return thread

    @api.multi
    def write(self, values):
        if self.env.context.get('tracking_disable'):
            return super(mail_thread_child, self).write(values)
        # Track initial values of tracked fields
        track_ctx = dict(self.env.context)
        if 'lang' not in track_ctx:
            track_ctx['lang'] = self.env['res.users']\
                .browse(self._uid).lang

        tracked_fields = None
        if not self.env.context.get('mail_notrack'):
            tracked_fields = self._get_tracked_fields(values.keys(),
                                                      mode='write')

        if tracked_fields:
            initial_values = dict((record.id, dict((key, getattr(record, key))
                                                   for key in tracked_fields))
                                  for record in self)

        # Perform write, update followers
        result = super(mail_thread_child, self).write(values)
        # Perform the tracking
        if tracked_fields:
            self.with_context(track_ctx)\
                .message_track(tracked_fields, initial_values, mode='write')

        return result

    @api.multi
    def unlink(self):
        self.message_post_parent(body="", mode='unlink')
        res = super(mail_thread_child, self).unlink()
        return res

    @api.model
    def _get_tracked_fields(self, updated_fields, mode="create"):
        tracked_fields = []
        for name, field in self._fields.items():
            visibility = getattr(field, 'track_visibility', False)
            if visibility == 'always':
                tracked_fields.append(name)
            elif mode == 'create' and visibility == 'oncreate':
                tracked_fields.append(name)
            elif mode == 'write' and visibility == 'onchange' and \
                    name in updated_fields:
                tracked_fields.append(name)
            elif name in self._track:
                tracked_fields.append(name)

        if tracked_fields:
            return self.fields_get(tracked_fields)
        return {}

    @api.multi
    def message_track(self, tracked_fields, initial_values, mode="create"):

        def convert_for_display(value, col_info):
            if not value and col_info['type'] == 'boolean':
                return 'False'
            if not value:
                return ''
            if col_info['type'] == 'many2one':
                return value.name_get()[0][1]
            if col_info['type'] == 'selection':
                return dict(col_info['selection'])[value]
            return value

        def format_message(message_description, tracked_values):
            message = ''
            if message_description:
                message = '<span>%s</span>' % message_description
            for name, change in tracked_values.items():
                message += '<div> &nbsp; &nbsp; &bull; <b>%s</b>: ' % \
                    change.get('col_info')
                if change.get('old_value'):
                    message += '%s &rarr; ' % change.get('old_value')
                message += '%s</div>' % change.get('new_value')
            return message

        if not tracked_fields:
            return True

        for browse_record in self:
            initial = initial_values[browse_record.id]
            changes = set()
            tracked_values = {}

            # generate tracked_values data structure:
            # {'col_name': {col_info, new_value, old_value}}
            for col_name, col_info in tracked_fields.items():
                field = self._fields[col_name]
                initial_value = initial[col_name]
                record_value = getattr(browse_record, col_name)

                if record_value == initial_value and \
                        getattr(field, 'track_visibility', None) == 'always':
                    tracked_values[col_name] = dict(
                        col_info=col_info['string'],
                        new_value=convert_for_display(record_value, col_info),
                    )
                elif record_value != initial_value and\
                        (record_value or initial_value):
                        # because browse null != False
                    if getattr(field, 'track_visibility', None) in \
                            ['always', 'onchange']:
                        tracked_values[col_name] = dict(
                            col_info=col_info['string'],
                            old_value=convert_for_display(initial_value,
                                                          col_info),
                            new_value=convert_for_display(record_value,
                                                          col_info),
                        )
                    if col_name in tracked_fields:
                        changes.add(col_name)
            if not changes:
                continue

            # find subtypes and post messages or log if no subtype found
            subtypes = []
            # By passing this key, that allows to let the subtype empty and so
            # don't sent email because partners_to_notify from mail_message.
            # notify will be empty
            if not self.env.context.get('mail_track_log_only'):
                for field, track_info in self._track.items():
                    if field not in changes:
                        continue
                    for subtype, method in track_info.items():
                        if method(self, browse_record):
                            subtypes.append(subtype)

            posted = False
            for subtype in subtypes:
                subtype_rec = self.env['ir.model.data']\
                    .xmlid_to_object(subtype)
                if not (subtype_rec and subtype_rec.exists()):
                    _logger.debug('subtype %s not found' % subtype)
                    continue
                message = format_message(subtype_rec.description if
                                         subtype_rec.description else
                                         subtype_rec.name, tracked_values)
                self.message_post_parent(browse_record, message, mode)
            if not posted:
                message = format_message('', tracked_values)
                browse_record.message_post_parent(body=message, mode=mode)
        return True

    @api.one
    def message_post_parent(self, body="", mode="create"):
        ctx = self.env.context.copy()
        for parent in self._tracked_parent:
            parent_field = getattr(self, parent)
            if isinstance(parent_field, browse_record) and \
                    not isinstance(parent_field, browse_null):
                parent_model = str(parent_field._model)
                params = {'model': parent_model,
                          'res_id': parent_field.id
                          }
                parent_message = \
                    _('<div>&bull; <b>%s</b> %s : %s</div>') % \
                    (self._description, DICT_MODE[mode],
                     getattr(self, self._track_name))
                message = parent_message + body
                ctx.update({'params': params})
                parent_field.message_post(body=message)
