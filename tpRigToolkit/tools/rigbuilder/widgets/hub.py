#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains rig widget for RigBuilder
"""

import tpQtLib
from tpQtLib.core import tool

from tpRigToolkit.tools.rigbuilder.tools import datalibrary


class HubWidget(tpQtLib.Window, object):
    def __init__(self, project=None, settings=None, console=None, progress_bar=None, parent=None):

        self._library = None
        self._project = project
        self._console = console
        self._progress_bar = progress_bar
        self._tools_classes = list()

        for tool_class in [datalibrary.DataLibrary]:
            self.register_tool_class(tool_class)

        super(HubWidget, self).__init__(
            name='HubWidgetWindow',
            title='Hub Widget',
            settings=settings,
            parent=parent,
            show_dragger=False,
            auto_load=False
        )

        self.statusBar().hide()

    @property
    def tools_classes(self):
        """
        Returns list of registered tool classes for current Hub
        :return: list(cls)
        """

        return self._tools_classes

    def ui(self):
        super(HubWidget, self).ui()

        self.setAcceptDrops(True)

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

        data_library = self.data_library()
        data_library.set_project(project)

    def get_console(self):
        """
        Returns console widget
        :return: Console
        """

        return self._console

    def set_console(self, console):
        """
        Sets the RigBuilder console linked to this widget
        :param console: Console
        """

        self._console = console

    def data_library(self):
        """
        Returns data library widget
        :return: DataLibrary
        """

        data_library = self.invoke_dock_tool_by_name('Data Library')
        data_library.setEnabled(False)
        self.set_library(data_library)

        return data_library

    def library(self):
        """
        Returns library of this widget
        :return: Library
        """

        return self._library

    def set_library(self, library):
        """
        Sets library to this widget
        :param library: Library
        """

        self._library = library
        # self._outliner.set_library(library)
        # self._rig_pipeline.set_library(library)

    def register_tool_class(self, tool_class):
        """
        Registers given tool class
        :param tool_class: cls
        """

        if not tool_class or tool_class in self._tools_classes:
            return

        self._tools_classes.append(tool_class)

    def invoke_dock_tool_by_name(self, tool_name, settings=None):
        tool_class = None
        for t in self._tools_classes:
            if t.NAME == tool_name:
                tool_class = t
                break
        if not tool_class:
            return None

        tool_instance = tool.create_tool_instance(tool_class, self._tools)
        if not tool_instance:
            return None
        if tool_class.NAME in [t.NAME for t in self._tools] and tool_class.IS_SINGLETON:
            return tool_instance

        self.register_tool_instance(tool_instance)
        if settings:
            tool_instance.restore_state(settings)
            if not self.restoreDockWidget(tool_instance):
                pass
        else:
            self.addDockWidget(tool_instance.DEFAULT_DOCK_AREA, tool_instance)

        tool_instance.app = self
        tool_instance.show_tool()

        return tool_instance
