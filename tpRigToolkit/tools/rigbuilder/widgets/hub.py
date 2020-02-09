#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains rig widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

import logging

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpQtLib
from tpQtLib.core import tool
from tpQtLib.widgets import tabs, breadcrumb
from tpPyUtils import osplatform, path as path_utils

from tpRigToolkit.tools.rigbuilder.widgets import builder, rigoutliner, blueprint
from tpRigToolkit.tools.rigbuilder.objects import rig
from tpRigToolkit.tools.rigbuilder.tools import datalibrary, controls, blueprintseditor, properties
from tpRigToolkit.tools.rigbuilder.tools import buildnodeslibrary, blueprintslibrary

LOGGER = logging.getLogger('tpRigToolkit')


class HubWidget(tpQtLib.Window, object):
    def __init__(self, project=None, settings=None, console=None, progress_bar=None, parent=None):

        self._library = None
        self._project = project
        self._console = console
        self._progress_bar = progress_bar
        self._tools_classes = list()

        self._current_rig = None
        self._path_filter = ''
        self._handle_selection_change = True

        # TODO: Tool registration should be automatic
        for tool_class in [
            datalibrary.DataLibrary, controls.ControlsTool, properties.PropertiesTool,
            blueprintseditor.BlueprintsEditor, buildnodeslibrary.BuldNodesLibrary, blueprintslibrary.BlueprintsLibrary]:
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

    # ================================================================================================
    # ======================== PROPERTIES
    # ================================================================================================

    @property
    def tools_classes(self):
        """
        Returns list of registered tool classes for current Hub
        :return: list(cls)
        """

        return self._tools_classes

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def ui(self):
        super(HubWidget, self).ui()

        self.setAcceptDrops(True)

        main_splitter = QSplitter(self)
        main_splitter.setOrientation(Qt.Horizontal)
        main_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(main_splitter)

        self._main_tab = tabs.TearOffTabWidget()
        self._main_tab.setTabsClosable(False)

        self._blueprint = blueprint.BlueprintWidget()
        self._outliner = rigoutliner.RigOutliner(settings=self._settings, project=self._project, console=self._console)
        self._builder = builder.RigBuilder(settings=self._settings, project=self._project, console=self._console)

        title_widget = QFrame()
        title_widget.setObjectName('TaskFrame')
        title_widget.setFrameStyle(QFrame.StyledPanel)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(2, 2, 2, 2)
        title_layout.setSpacing(2)
        title_widget.setLayout(title_layout)
        self._title = breadcrumb.BreadcrumbWidget()
        self.reset_title()

        title_layout.addItem(QSpacerItem(30, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        title_layout.addWidget(self._title)
        title_layout.addItem(QSpacerItem(30, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        tab_widget = QWidget()
        tab_layout = QVBoxLayout()
        tab_layout.setContentsMargins(0, 0, 0, 0)
        tab_layout.setSpacing(0)
        tab_widget.setLayout(tab_layout)
        tab_layout.addWidget(title_widget)
        tab_layout.addWidget(self._main_tab)

        main_splitter.addWidget(self._outliner)
        main_splitter.addWidget(tab_widget)

        self._main_tab.addTab(self._blueprint, 'Template')
        self._main_tab.addTab(self._builder, 'Builder')
        main_splitter.setSizes([1, 1])

    def setup_signals(self):
        self._outliner.tree_widget.itemSelectionChanged.connect(self._on_outliner_item_selection_changed)

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

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
        self._outliner.set_project(project)
        self._builder.set_project(project)

        properties_widget = self.properties_widget()
        properties_widget.set_project(project)

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

    def get_progress_bar(self):
        """
        Returns progress bar linked to this widget
        :return: ProgressBar
        """

        return self._progress_bar

    def set_progress_bar(self, progress_bar):
        """
        Sets the progress bar linked to this widget
        :param progress_bar: ProgressBar
        """

        self._progress_bar = progress_bar

    def properties_widget(self):
        """
        Returns properties widget
        :return: PropertiesTool
        """

        properties_widget = self.invoke_dock_tool_by_name('Properties')

        return properties_widget

    def data_library(self):
        """
        Returns data library widget
        :return: DataLibrary
        """

        data_library = self.invoke_dock_tool_by_name('Data Library')
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
        self._outliner.set_library(library)
        self._builder.set_library(library)

    def set_title(self, name):
        """
        Internal function used to update the title
        :param name: str,
        """

        rig_names = name.split('/')
        self._title.set(rig_names)

    def reset_title(self):
        """
        Resets title
        """

        self._title.set(['No Rig Selected'])

    # ================================================================================================
    # ======================== TOOLS
    # ================================================================================================

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
            LOGGER.warning('No registered tool found with name: "{}"'.format(tool_name))
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

    # ================================================================================================
    # ======================== INTERNAL
    # ================================================================================================

    def _get_project_settings(self):
        """
        Returns JSON settings object used of the project
        :return: JSONSettings
        """

        return self._project.settings

    def _get_project_setting(self, name):
        """
        Returns a setting value stored in the project settings
        :param name: str
        :return: variant
        """

        project_settings = self._get_project_settings()
        if not project_settings:
            return

        return project_settings.get(name)

    def _set_project_setting(self, name, value):
        """
        Internal function used to set a setting of the project
        :param name: str
        :param value: variant
        """

        project_settings = self._get_project_settings()
        if not project_settings:
            return

        project_settings.set(name, value)

    def _get_filtered_project_path(self, filter_value=None):
        """
        Internal function used to set the filter path
        :param filter_value: str
        :return: str
        """

        if not filter_value:
            filter_value = self._path_filter
        if filter_value:
            project_path = path_utils.join_path(self._project.full_path, filter_value)
        else:
            project_path = self._project.full_path

        return project_path

    def _get_current_rig_name(self):
        """
        Returns the current rig name
        :return: str
        """

        if not self._current_rig:
            return

        return self._current_rig.get_name()

    def _get_current_rig_path(self):
        """
        Returns the path where current rig is located
        :return: str
        """

        if not self._project:
            return

        rig_name = self._get_current_rig_name()
        if rig_name:
            filter_str = self._outliner.filter_widget.get_sub_path_filter()
            rig_directory = self._project.full_path
            if filter_str:
                rig_directory = path_utils.join_path(self._project.full_path, filter_str)

            rig_directory = path_utils.join_path(rig_directory, rig_name)

            return rig_directory
        else:
            filter_value = self._outliner.filter_widget.get_sub_path_filter()
            if filter_value:
                rig_directory = path_utils.join_path(self._project.full_path, filter_value)
            else:
                rig_directory = self._project.full_path

            return rig_directory

    def _set_current_rig(self, rig_name):
        """
        Internal function that sets the current active rig
        :param rig_name: str
        """

        if not rig_name or not self._project:
            self._current_rig = None
            return

        self._set_project_setting('rig', rig_name)
        self._current_rig = rig.RigObject(name=rig_name)
        self._current_rig.set_directory(self._project.full_path)
        self._current_rig.set_library(self.library())

        full_path = self._get_current_rig_path()
        LOGGER.debug('New Selected Rig Path: {}'.format(full_path))
        if not osplatform.get_permission(full_path):
            LOGGER.warning('Could not get permission for rig: {}'.format(rig_name))

    def _update_rig(self, rig_name):
        """
        Internal function that updates the current active rig
        :param rig_name: str
        """

        self._set_current_rig(rig_name)

        rigs = self._outliner.tree_widget.selectedItems()
        if rigs and self._current_rig:
            title = self._current_rig.get_name()

        if rig_name:
            project_path = self._get_filtered_project_path()
            self._current_rig.load(project_path)
            self.set_title(title)
        else:
            self.reset_title()

    def _refresh_selected_item(self):
        """
        Internal callback function that refresh current rig item selected in rig outliner
        """

        if not self._handle_selection_change:
            return

        data_library = self.data_library()
        properties_widget = self.properties_widget()

        rigs = self._outliner.tree_widget.selectedItems()
        if not rigs:
            self._update_rig(None)
            data_library.set_path(None)
            self._builder.set_rig(None)
            properties_widget.set_object(None)
            self._builder.refresh()
            return

        item = rigs[0]
        if item.matches(self._current_rig):
            return

        rig_name = item.get_name()
        self._update_rig(rig_name)
        self._outliner.setFocus()
        data_library.set_path(self._current_rig.get_path())
        self._builder.set_rig(self._current_rig)
        properties_widget.set_object(self._current_rig)

        self._builder.refresh()
        properties_widget.refresh()

    # ================================================================================================
    # ======================== CALLBACKS
    # ================================================================================================

    def _on_outliner_item_selection_changed(self):
        """
        Internal callback function that is called when a rig is selected in the rig outliner
        """

        self._refresh_selected_item()
