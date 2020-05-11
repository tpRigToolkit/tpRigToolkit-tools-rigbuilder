#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Procedural Script based auto rigger
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os

import tpDcc
from tpDcc.core import tool
from tpDcc.libs.qt.widgets import toolset

# Defines ID of the tool
TOOL_ID = 'tpRigToolkit-tools-rigbuilder'

# We skip the reloading of this module when launching the tool
no_reload = True


class RigBuilderTool(tool.DccTool, object):
    def __init__(self, *args, **kwargs):
        super(RigBuilderTool, self).__init__(*args, **kwargs)

    @classmethod
    def config_dict(cls, file_name=None):
        base_tool_config = tool.DccTool.config_dict(file_name=file_name)
        tool_config = {
            'name': 'Rig Builder',
            'id': 'tpRigToolkit-tools-rigbuilder',
            'logo': 'rigbuilder',
            'icon': 'rigbuilder',
            'tooltip': ' Procedural Script based auto rigger',
            'tags': ['tpRigToolkit', 'autorig', 'rig', 'procedural', 'script'],
            'logger_dir': os.path.join(os.path.expanduser('~'), 'tpRigToolkit', 'logs', 'tools'),
            'logger_level': 'INFO',
            'is_checkable': False,
            'is_checked': False,
            'import_order': ['core', 'data', 'scripts', 'items', 'objects', 'widgets', 'tool'],
            'tools_to_reload': ['tpRigToolkit-tools-controlrig'],
            'skip_modules': ['dccs'],
            'menu_ui': {'label': 'Control Rig', 'load_on_startup': False, 'color': '', 'background_color': ''},
            'menu': [
                {'label': 'Rig Builder',
                 'type': 'menu', 'children': [{'id': 'tpRigToolkit-tools-rigbuilder', 'type': 'tool'}]}],
            'shelf': [
                {'name': 'Rig Builder',
                 'children': [{'id': 'tpRigToolkit-tools-rigbuilder', 'display_label': False, 'type': 'tool'}]}
            ]
        }
        base_tool_config.update(tool_config)

        return base_tool_config

    def launch(self, *args, **kwargs):
        return self.launch_frameless(*args, **kwargs)


class RigBuilderToolset(toolset.ToolsetWidget, object):

    ID = TOOL_ID

    def __init__(self, *args, **kwargs):

        self._settings = kwargs.pop('settings', None)
        self._project_name = kwargs.pop('project_name', None)

        super(RigBuilderToolset, self).__init__(*args, **kwargs)

    def contents(self):

        from tpRigToolkit.tools.rigbuilder.tool import rigbuilder
        rig_builder = rigbuilder.RigBuilder(settings=self._settings, project_name=self._project_name, parent=self)

        return [rig_builder]
