# -*- coding: utf-8 -*-
# © 2016-2017 Akretion (http://www.akretion.com)
# © 2016-2017 Camptocamp (http://www.camptocamp.com/)
# © 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from collections import defaultdict
from odoo import api, models, fields


class Base(models.AbstractModel):
    _inherit = "base"

    @api.multi
    def _compute_onchange_dirty(self, original_record):
        """
        Return the list of dirty fields. (designed to be called by
        play_onchanges)
        The list of dirty fields is computed from the list marked as dirty
        on the record. Form this list, we remove the fields for which the value
        into the original record is the same as the one into the current record
        :param original_record:
        :return: changed values
        """
        self.ensure_one()
        dirties = []
        for field_name in self._get_dirty():
            original_value = original_record[field_name]
            new_value = self[field_name]
            if original_value == new_value:
                # False dirty. The field has been loaded into the
                # onchange process -> skip
                continue
            dirties.append(field_name)
        return dirties

    def play_onchanges(self, values, onchange_fields=None):
        """
        Play the onchange methods defined on the current record and return the
        changed values.
        The record is not modified by the onchange

        :param values: dict of input value that
        :param onchange_fields: fields for which onchange methods will be
        played. If not provided, the list of field is based on the values keys.
        Order in onchange_fields is very important as onchanges methods will
        be played in that order.
        :return: changed values

        This method reimplement the onchange method to be able to work on the
        current recordset if provided.
        """
        env = self.env
        if self:
            self.ensure_one()

        if not onchange_fields:
            onchange_fields = values.keys()
        names = onchange_fields

        # _onchange_spec() will return onchange fields from the default view
        # we need all fields in the dict even the empty ones
        # otherwise 'onchange()' will not apply changes to them
        field_onchange = {field_name: "1" for field_name in self._fields}

        if not all(name in self._fields for name in onchange_fields):
            return {}

        # determine subfields for field.convert_to_onchange() below
        secondary = []
        subfields = defaultdict(set)
        for dotname in field_onchange:
            if "." in dotname:
                secondary.append(dotname)
                name, subname = dotname.split(".")
                subfields[name].add(subname)

        # create a new record with values, and attach ``self`` to it
        with env.do_in_onchange():
            # keep a copy of the original record.
            # attach ``self`` with a different context (for cache consistency)
            origin = self.with_context(__onchange=True)
            origin_dirty = set(self._get_dirty())
            fields.copy_cache(self, origin.env)
            if self:
                record = self
                record.update(values)
            else:
                # initialize with default values, they may be used in onchange
                new_values = self.default_get(self._fields.keys())
                new_values.update(values)
                record = self.new(new_values)
            values = {name: record[name] for name in record._cache}
            record._origin = origin

        # load fields on secondary records, to avoid false changes
        with env.do_in_onchange():
            for field_seq in secondary:
                record.mapped(field_seq)

        # determine which field(s) should be triggered an onchange
        todo = list(names) or list(values)
        done = set()

        # dummy assignment: trigger invalidations on the record
        with env.do_in_onchange():
            for name in todo:
                if name == "id":
                    continue
                value = record[name]
                field = self._fields[name]
                if field.type == "many2one" and field.delegate and not value:
                    # do not nullify all fields of parent record for new
                    # records
                    continue
                record[name] = value

        dirty = set()

        # process names in order (or the keys of values if no name given)
        while todo:
            name = todo.pop(0)
            if name in done:
                continue
            done.add(name)

            with env.do_in_onchange():
                # apply field-specific onchange methods
                if field_onchange.get(name):
                    record._onchange_eval(name, field_onchange[name], {})

                # force re-evaluation of function fields on secondary records
                for field_seq in secondary:
                    record.mapped(field_seq)

                # determine which fields have been modified
                dirties = record._compute_onchange_dirty(origin)
                dirty |= set(dirties)
                todo.extend(dirties)

        # prepare the result to return a dictionary with the new values for
        # the dirty fields
        result = {}
        for name in dirty:
            field = self._fields[name]
            value = record[name]
            if field.type == "many2one":
                # for many2one, we keep the id and don't call the
                # convert_on_change to avoid the call to name_get by the
                # convert_to_onchange
                value = value.id
            else:
                value = field.convert_to_onchange(
                    value, record, subfields[name]
                )
            result[name] = value

        # reset dirty values into the current record
        if self:
            to_reset = dirty | set(values.keys())
            with env.do_in_onchange():
                for name in to_reset:
                    original = origin[name]
                    new = self[name]
                    if original == new:
                        continue
                    self[name] = origin[name]
                    env.dirty[record].discard(name)
            env.dirty[record].update(origin_dirty)
        return result
