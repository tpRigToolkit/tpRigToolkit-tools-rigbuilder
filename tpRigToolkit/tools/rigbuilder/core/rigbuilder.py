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

import logging
from functools import partial

from tpQtLib.core import tool, qtutils
from tpQtLib.widgets import stack

import tpRigToolkit
from tpRigToolkit.tools import rigbuilder
from tpRigToolkit.tools.rigbuilder.widgets import project, hub, console

LOGGER = logging.getLogger('tpRigToolkit')


class RigBuilderTool(tpRigToolkit.Tool, object):
    def __init__(self, config, project_path=None, project_name=None):

        self._project = None

        self._projects_widget = project.ProjectWidget()
        self._console = console.Console()
        self._hub_widget = hub.HubWidget(console=self._console)

        super(RigBuilderTool, self).__init__(config=config)

    def post_attacher_set(self):
        """
        Implements base tpRigToolkit.Tool post_attacher_set
        Function that is called once an attacher has been set
        """

        self._projects_widget.set_settings(self.settings())
        self._hub_widget.set_settings(self.settings())

        self._register_tools()

    def ui(self):
        super(RigBuilderTool, self).ui()

        self._stack = stack.SlidingStackedWidget()
        self.main_layout.addWidget(self._stack)

        self._stack.addWidget(self._projects_widget)
        self._stack.addWidget(self._hub_widget)

    def setup_signals(self):
        self._projects_widget.projectOpened.connect(self._on_open_project)

    def get_project(self):
        """
        Returns current project opened in rigbuilder
        :return: project.Project
        """

        return self._project

    def set_project(self, project):
        """
        Sets project opened in rigbuilder
        :param project: project.Project
        """

        self._project = project
        self._hub_widget.set_project(project)
        rigbuilder.project = project

    def get_console(self):
        """
        Returns console widget
        :return: Console
        """

        return self._console

    def _open_project(self):
        """
        Internal function that opens current set project
        """

        if not self._project:
            LOGGER.warning('Impossible to open project. Project is not defined.')
            return False

        self._stack.slide_in_index(1)

    def _register_tools(self):
        """
        Internal function that registers all available tools for tpRigToolkit.tools.rignode
        """

        if not self._hub_widget.tools_classes:
            LOGGER.info('No tools available!')
            return

        settings = self.settings()
        for tool_class in self._hub_widget.tools_classes:
            if issubclass(tool_class, tool.DockTool):
                tools_menu = qtutils.get_or_create_menu(self.menu_bar(), 'Tools')
                self.menu_bar().addMenu(tools_menu)
                show_tool_action = tools_menu.addAction(tool_class.NAME)
                icon = tool_class.icon()
                if icon:
                    show_tool_action.setIcon(icon)
                show_tool_action.triggered.connect(partial(self._hub_widget.invoke_dock_tool_by_name, tool_class.NAME))
                # show_tool_action.triggered.connect(
                #     lambda tool_name=tool_class.NAME: self._hub_widget.invoke_dock_tool_by_name(tool_name))
                settings.beginGroup('DockTools')
                child_groups = settings.childGroups()
                for dock_tool_group_name in child_groups:
                    settings.beginGroup(dock_tool_group_name)
                    if dock_tool_group_name in [t.unique_name() for t in self._tools]:
                        continue
                    tool_name = dock_tool_group_name.split('::')[0]
                    self._hub_widget.invoke_dock_tool_by_name(tool_name, settings)
                    settings.endGroup()
                settings.endGroup()

    def _on_open_project(self, project=None):
        """
        Internal callback function that is called when a project is selected on
        the ProjectsWidget UI
        :param project: project.Project
        """

        if project:
            self.set_project(project)
        else:
            if not self._project:
                LOGGER.warning('Impossible to retrieve already opened project! Restart the tool please')
                return False

        self._open_project()

        return True
