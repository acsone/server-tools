# -*- coding: utf-8 -*-
# © 2016 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging
from openerp import api, fields, models
from collections import OrderedDict

_logger = logging.getLogger(__name__)


class ModulePrototyper(models.Model):
    _inherit = "module_prototyper"
    _description = "Module Prototyper"

    activity_action_ids = fields.Many2many(
        'workflow.activity.action', 'prototype_wf_activity_action_rel',
        'module_prototyper_id', 'activity_action_id', 'Activity actions',
        help=('Enter the list of workflow activities action that you have '
              'created and want to export in this module')
    )

    activity_rule_ids = fields.Many2many(
        'activity.record.rule', 'prototype_activity_rule_rel',
        'module_prototyper_id', 'activity_rule_id', 'Activity Record Rules',
        help=('Enter the list of activity record rules that you have created '
              'and want to export in this module')
    )

    ir_actions_server_ids = fields.Many2many(
        'ir.actions.server', 'prototype_action_server_rel',
        'module_prototyper_id', 'ir_actions_server_id',
        'Activity Action Server',
        help=('Enter the list of action server used by activity that you have '
              'created and want to export in this module')
    )

    @api.onchange('activity_ids')
    def on_acitvity_ids_change(self):
        super(ModulePrototyper, self).on_acitvity_ids_change()
        activity_action_ids = set(self.activity_action_ids._ids)
        activity_rule_ids = set(self.activity_rule_ids._ids)
        for act in self.activity_ids:
            activity_action_ids.update(set(act.action_ids._ids))
            activity_rule_ids.update(set(act.activity_rule_ids._ids))
        self.activity_action_ids = [(6, None, list(activity_action_ids))]
        self.activity_rule_ids = [(6, None, list(activity_rule_ids))]

    @api.onchange('activity_action_ids')
    def on_activity_action_ids_change(self):
        ir_actions_server_ids = set(self.ir_actions_server_ids._ids)
        new_actions = self.activity_action_ids.mapped('action')
        ir_actions_server_ids.update(new_actions._ids)
        self.ir_actions_server_ids = [(6, None, list(ir_actions_server_ids))]

    @api.multi
    def get_workflows_datas(self):
        ret = super(ModulePrototyper, self).get_workflows_datas()
        self.ensure_one()
        workflows = {}
        datas = self.get_import_compat_values(
            self.ir_actions_server_ids)
        # compute the list of action server by workflow
        act_servers_by_wkf = {}
        for act_action in self.activity_action_ids:
            act_servers = act_servers_by_wkf.setdefault(
                act_action.activity_id.wkf_id,
                set())
            act_servers.add(act_action.action)
        for act_server, values in datas.iteritems():
            # get the workflow from the computed list of action server by 
            # workflow since the link don't exists on act_server
            wkf_id = None
            for wkfid, act_servers in act_servers_by_wkf.iteritems():
                if act_server in act_servers:
                    wkf_id = wkfid
            wk_def = workflows.setdefault(
                wkf_id or act_server.wkf_transition_id.wkf_id,
                {'activity_actions': [],
                 'activity_rules': [],
                 'actions_server': []})
            wk_def['actions_server'].append((act_server, values))

        datas = self.get_import_compat_values(self.activity_action_ids)
        for act_action, values in datas.iteritems():
            wk_def = workflows.setdefault(
                act_action.activity_id.wkf_id,
                {'activity_actions': [],
                 'activity_rules': [],
                 'actions_server': []})
            wk_def['activity_actions'].append((act_action, values))

        datas = self.get_import_compat_values(self.activity_rule_ids)
        for act_rule, values in datas.iteritems():
            wk_def = workflows.setdefault(
                act_rule.activity_id.wkf_id,
                {'activity_actions': [],
                 'activity_rules': [],
                 'actions_server': []})
            wk_def['activity_rules'].append((act_rule, values))

        for item in ret:
            workflow = item['workflow']
            val = workflows.get(workflow)
            if not val:
                continue
            # information already present for the workflow -> enrich
            data_models = item['data_models']
            data_models['ir.actions.server'] = val['actions_server']
            data_models['workflow.activity.action'] = val['activity_actions']
            data_models['activity.record.rule'] = val['activity_rules']
            del workflows[workflow]
        for workflow, val in workflows.iteritems():
            data_models = OrderedDict()
            data_models['ir.actions.server'] = val['actions_server']
            data_models['workflow.activity.action'] = val['activity_actions']
            data_models['activity.record.rule'] = val['activity_rules']
            ret.append({
                'workflow': workflow,
                'xml_id': self.get_model_xml_id(workflow),
                'data_models':  data_models
            })
        return ret
