#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains rig widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc
from tpDcc.libs.qt.core import window
from tpDcc.libs.qt.widgets import tabs, breadcrumb, stack
from tpDcc.libs.python import osplatform, path as path_utils

import tpRigToolkit
from tpRigToolkit.tools.rigbuilder.core import tool
from tpRigToolkit.tools.rigbuilder.widgets.base import options
from tpRigToolkit.tools.rigbuilder.widgets.builder import builder
from tpRigToolkit.tools.rigbuilder.widgets.rig import rigoutliner
# from tpRigToolkit.tools.rigbuilder.widgets.blueprint import blueprintseditor, blueprint
# from tpRigToolkit.tools.rigbuilder.widgets.puppeteer import puppeteer
from tpRigToolkit.tools.rigbuilder.objects import rig
from tpRigToolkit.tools.rigbuilder.tools import datalibrary, controls, properties, puppeteer as puppet_tools
from tpRigToolkit.tools.rigbuilder.tools import buildnodeslibrary, blueprintslibrary, renamer, connection


class HubWidget(window.BaseWindow, object):

    WindowId = 'RigBuilderHub'

    def __init__(self, project=None, settings=None, console=None, progress_bar=None, parent=None):

        self._library = None
        self._project = project
        self._settings = settings
        self._console = console
        self._progress_bar = progress_bar
        self._tools_classes = list()
        self._tools = set()

        self._current_rig = None
        self._current_builder_item = None
        self._path_filter = ''
        self._handle_selection_change = True

        # TODO: Tool registration should be automatic
        for tool_class in [datalibrary.DataLibrary, controls.ControlsTool, properties.PropertiesTool,
                           buildnodeslibrary.BuldNodesLibrary, blueprintslibrary.BlueprintsLibrary,
                           puppet_tools.PuppetPartsBuilderTool, renamer.RenamerTool, connection.ConnectionEditorTool]:
            self.register_tool_class(tool_class)

        super(HubWidget, self).__init__(parent=parent,)

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

        self._stack = stack.SlidingOpacityStackedWidget()
        self.main_layout.addWidget(self._stack)

        main_splitter = QSplitter(self)
        main_splitter.setOrientation(Qt.Horizontal)
        main_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._main_tab = tabs.BaseTabWidget()
        self._second_tab = tabs.TearOffTabWidget()
        self._second_tab.setTabsClosable(False)
    #
    #     self._blueprint_editor = blueprintseditor.BlueprintsEditor(settings=self._settings, project=self._project)
    #     self._blueprint = blueprint.BlueprintWidget()
    #     # self._puppeteer = puppeteer.PuppeteerWidget()

        rig_outliner_splitter = QSplitter(self)
        rig_outliner_splitter.setOrientation(Qt.Vertical)
        rig_outliner_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        # self._outliner = rigoutliner.RigOutliner(settings=self._settings, project=self._project, console=self._console)
        self._outliner = rigoutliner.RigOutliner(settings=self._settings, project=self._project)
        self._outliner_options = options.RigBuilderOptionsWidget()
        rig_outliner_splitter.addWidget(self._outliner)
        rig_outliner_splitter.addWidget(self._outliner_options)
    #
        # self._builder = builder.RigBuilder(settings=self._settings, project=self._project, console=self._console)
        self._builder = builder.RigBuilder(settings=self._settings, project=self._project)

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
        tab_layout.setContentsMargins(2, 2, 2, 2)
        tab_layout.setSpacing(2)
        tab_widget.setLayout(tab_layout)
        tab_layout.addWidget(title_widget)
        tab_layout.addWidget(self._second_tab)

        main_splitter.addWidget(rig_outliner_splitter)
        main_splitter.addWidget(tab_widget)

        self._second_tab.addTab(self._builder, 'Builder')
    #     # self._second_tab.addTab(self._blueprint, 'Template')
    #     main_splitter.setSizes([1, 1])

        self._main_tab.addTab(main_splitter, 'Rig')
    #     self._main_tab.addTab(self._blueprint_editor, 'Blueprint')
    #     # self._main_tab.addTab(self._puppeteer, 'Puppeteer')

        self._builder_creator = builder.NodeBuilderCreator()

        self._stack.addWidget(self._main_tab)
        self._stack.addWidget(self._builder_creator)

    def setup_signals(self):
        self._outliner.tree_widget.itemSelectionChanged.connect(self._on_outliner_item_selection_changed)
        self._builder.builder_tree().itemSelected.connect(self._on_build_tree_selection_changed)
        # self._builder.builder_tree().itemSelectionChanged.connect(self._on_build_tree_selection_changed)
        self._builder.createNode.connect(self._on_create_builder_node)
        self._builder_creator.creationCanceled.connect(self._on_cancel_builder_node_creation)
        self._builder_creator.nodeCreated.connect(self._on_builder_node_created)
    #     # self._puppeteer.puppetRemoved.connect(self._on_puppet_removed)

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
        # self._blueprint_editor.set_project(project)
        # data_library = self.data_library()
        # data_library.set_project(project)

    # def get_console(self):
    #     """
    #     Returns console widget
    #     :return: Console
    #     """
    #
    #     return self._console
    #
    # def set_console(self, console):
    #     """
    #     Sets the RigBuilder console linked to this widget
    #     :param console: Console
    #     """
    #
    #     self._console = console
    #
    # def get_progress_bar(self):
    #     """
    #     Returns progress bar linked to this widget
    #     :return: ProgressBar
    #     """
    #
    #     return self._progress_bar
    #
    # def set_progress_bar(self, progress_bar):
    #     """
    #     Sets the progress bar linked to this widget
    #     :param progress_bar: ProgressBar
    #     """
    #
    #     self._progress_bar = progress_bar

    def properties_widget(self):
        """
        Returns properties widget
        :return: PropertiesTool
        """

        properties_widget = self.invoke_dock_tool_by_name('Properties')
        # if properties_widget:
        #     properties_widget.set_project(self._project)

        return properties_widget

    # def data_library(self):
    #     """
    #     Returns data library widget
    #     :return: DataLibrary
    #     """
    #
    #     data_library = self.invoke_dock_tool_by_name('Data Library')
    #     self.set_library(data_library)
    #
    #     return data_library
    #
    # def library(self):
    #     """
    #     Returns library of this widget
    #     :return: Library
    #     """
    #
    #     return self._library
    #
    # def set_library(self, library):
    #     """
    #     Sets library to this widget
    #     :param library: Library
    #     """
    #
    #     self._library = library
    #     self._outliner.set_library(library)
    #     self._builder.set_library(library)
    #     self._blueprint_editor.set_library(library)

    def set_title(self, name):
        """
        Internal function used to update the title
        :param name: str,
        """

        rig_names = [{'text': rig_name} for rig_name in name.split('/')]
        self._title.set_items(rig_names)

    def reset_title(self):
        """
        Resets title
        """

        self._title.set_items([{'text': 'No Rig Selected'}])

    # ================================================================================================
    # ======================== TOOLS
    # ================================================================================================

    def register_tool_instance(self, instance):
        """
        Registers given tool instance
        Used to prevent tool classes being garbage collected and to save tool widgets states
        :param instance: Tool
        """

        self._tools.add(instance)

    def unregister_tool_instance(self, instance):
        """
        Unregister tool instance
        :param instance: Tool
        """

        if instance not in self._tools:
            return False
        self._tools.remove(instance)

        return True

    def get_registered_tools(self, class_name_filters=None):
        if class_name_filters is None:
            class_name_filters = list()

        if len(class_name_filters) == 0:
            return self._tools
        else:
            result = list()
            for tool in self._tools:
                if tool.__class__.__name__ in class_name_filters:
                    result.append(tool)

            return result

    def is_tool_opened(self, tool_name):
        """
        Returns whether or not a tool with given name is already opened
        :param tool_name: str
        :return: bool
        """

        return tool_name in [t.NAME for t in self._tools]

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
            tpRigToolkit.logger.warning('No registered tool found with name: "{}"'.format(tool_name))
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

    # def _get_filtered_project_path(self, filter_value=None):
    #     """
    #     Internal function used to set the filter path
    #     :param filter_value: str
    #     :return: str
    #     """
    #
    #     if not filter_value:
    #         filter_value = self._path_filter
    #     if filter_value:
    #         project_path = path_utils.join_path(self._project.full_path, filter_value)
    #     else:
    #         project_path = self._project.full_path
    #
    #     return project_path
    #
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
    #     self._current_rig.set_library(self.library())

        full_path = self._get_current_rig_path()
        tpRigToolkit.logger.debug('New Selected Rig Path: {}'.format(full_path))
        if not osplatform.get_permission(full_path):
            tpRigToolkit.logger.warning('Could not get permission for rig: {}'.format(rig_name))

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
            self._current_rig.load(rig_name)
            self.set_title(title)
        else:
            self.reset_title()

    def _refresh_selected_rig(self):
        """
        Internal callback function that refresh current rig item selected in rig outliner
        """

        if not self._handle_selection_change:
            return

    #     data_library = self.data_library()
    #     properties_widget = self.properties_widget()

        rigs = self._outliner.tree_widget.selectedItems()
        if not rigs:
            self._update_rig(None)
    #         if self._project:
    #             data_library.set_path(self._project.full_path)
    #         else:
    #             data_library.set_path(None)
            self._builder.set_rig(None)
            # self._builder_creator.set_rig(None)
            self._builder.refresh()
            # self._build_graph.clear()
            self._outliner_options.clear_options()
            return

        item = rigs[0]
        if item.matches(self._current_rig):
            return

    #     properties_widget.clear()

        rig_name = item.get_name()
        self._update_rig(rig_name)
        self._outliner.setFocus()
    #     data_library.set_path(self._current_rig.get_path())
        self._builder.set_rig(self._current_rig)
    #     self._builder_creator.set_rig(self._current_rig)
        self._outliner_options.set_option_object(self._current_rig)
        self._outliner_options.update_options()

        self._builder.refresh()

        # self._build_graph.add_nodes(self._builder.tree_widget.get_all_builder_nodes())

    def _refresh_selected_builder_node(self):
        """
        Internal callback function that is called when a builder node is selected in the builder node tree
        """

        if not self._handle_selection_change:
            return

        if not self.is_tool_opened('Properties'):
            return

        properties_widget = self.properties_widget()
        builder_nodes = self._builder.builder_tree().selectedItems()
        if not builder_nodes:
            properties_widget.clear()
            properties_widget.set_object(None)
            self._current_builder_item = None
            return

        item = builder_nodes[0]
        if item.matches(self._current_builder_item):
            return
        item_node = item.node
        self._current_builder_item = item

        properties_widget.clear(update_stack=False)
        properties_widget.set_object(item_node)

    # ================================================================================================
    # ======================== CALLBACKS
    # ================================================================================================

    def _on_outliner_item_selection_changed(self):
        """
        Internal callback function that is called when a rig is selected in the rig outliner
        """

        self._refresh_selected_rig()

    def _on_build_tree_selection_changed(self, item):
        """
        Internal callback function that is called when a builder node is selected in the builder node tree
        """

        self._refresh_selected_builder_node()

    def _on_create_builder_node(self):
        """
        Internal callback function that is called when the user wants to add a new builder node
        :return:
        """

        self._builder_creator.reset()
        self._builder_creator.set_build_node(self._builder.current_builder_node())
        self._stack.setCurrentIndex(1)

    def _on_cancel_builder_node_creation(self):
        """
        Internal callback function that is called when the user cancels the creation of a builder node
        :return:
        """

        self._stack.setCurrentIndex(0)

    def _on_builder_node_created(self, builder_node, name, parent_node):
        """
        Internal callback function that is called when a new builder node is created by the user
        :param builder_node:
        :param name:
        :param description:
        :param parent_node:
        :return:
        """

        if builder_node:
            if parent_node:
                parent_name = parent_node.get_name()
                parent_path = parent_node.get_path()
                if parent_path:
                    if parent_name.startswith(parent_path):
                        name = '{}/{}'.format(parent_name, name)
                    else:
                        name = '{}/{}/{}'.format(parent_path, parent_name, name)
                else:
                    name = '{}/{}'.format(parent_name, name)
            self._builder.create_builder_node(builder_node, name=name)
        self._stack.setCurrentIndex(0)

    def _on_puppet_removed(self):
        if self._project:
            project_name = self._project.name
            tpDcc.ToolsMgr().launch_tool_by_id(
                'tpRigToolkit-tools-rigbuilder', do_reload=False, debug=False, project_name=project_name)
        else:
            tpDcc.ToolsMgr().launch_tool_by_id('tpRigToolkit-tools-rigbuilder', do_reload=False, debug=False)
