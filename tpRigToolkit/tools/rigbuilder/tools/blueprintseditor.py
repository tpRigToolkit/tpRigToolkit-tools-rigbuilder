#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains rig presets tool implementation for tpRigBuilder
"""

from __future__ import print_function, division, absolute_import

import os
import logging
from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpQtLib.core import base, tool
from tpQtLib.widgets import stack, options

from tpRigToolkit.core import resource
from tpRigToolkit.tools.rigbuilder.core import consts, utils
from tpRigToolkit.tools.rigbuilder.objects import helpers, blueprint
from tpRigToolkit.tools.rigbuilder.widgets import scriptstree


LOGGER = logging.getLogger('tpRigToolkit')


class BlueprintsEditor(tool.DockTool, object):

    NAME = 'Blueprints Editor'
    TOOLTIP = 'Manages current available blueprints'
    DEFAULT_DOCK_AREA = Qt.RightDockWidgetArea
    IS_SINGLETON = True

    def __init__(self):
        super(BlueprintsEditor, self).__init__()

        self._created = False
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

    def show_tool(self):
        super(BlueprintsEditor, self).show_tool()

        data_library = self._app.data_library()

        if not self._created:
            self._create_ui()
            self._created = True

        if data_library:
            self._blueprints_viewer.set_library(data_library)

    def _create_ui(self):
        settings = self._app.settings()
        project = self._app.get_project()
        console = self._app.get_console()

        self._toolbar = QToolBar()
        self._content_layout.addWidget(self._toolbar)

        self._build_btn = QToolButton()
        self._build_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self._build_btn.setIcon(resource.ResourceManager().icon('play'))
        self._build_btn.setText('Build')
        self._toolbar.addWidget(self._build_btn)

        self._stack = stack.SlidingStackedWidget()
        self._content_layout.addWidget(self._stack)

        self._blueprints_viewer = BlueprintsViewer(project, settings)

        self._stack.addWidget(self._blueprints_viewer)

        self._blueprints_viewer.blueprintCreated.connect(self._on_blueprint_created)

    def _on_blueprint_created(self):
        self._blueprints_viewer.refresh()


class BlueprintsViewer(base.BaseWidget, object):

    blueprintCreated = Signal(str)

    def __init__(self, project, settings, parent=None):

        self._library = None
        self._project = project
        self._settings = settings

        super(BlueprintsViewer, self).__init__(parent=parent)

    def ui(self):
        super(BlueprintsViewer, self).ui()

        main_splitter = QSplitter()
        main_splitter.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.main_layout.addWidget(main_splitter)

        self._blueprints_tree = BlueprintsTree(project=self._project)

        right_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(self._blueprints_tree)
        main_splitter.addWidget(right_splitter)

        self._blueprints_scripts = BlueprintScripts(settings=self._settings)
        self._blueprints_scripts_options = BlueprintScriptsOptions()
        right_splitter.addWidget(self._blueprints_scripts)
        right_splitter.addWidget(self._blueprints_scripts_options)

    def setup_signals(self):
        self._blueprints_tree.currentItemChanged.connect(self._on_blueprint_selected)
        self._blueprints_tree.blueprintCreated.connect(self.blueprintCreated.emit)

    def library(self):
        """
        Returns library attached to this widget
        :return:
        """

        return self._library

    def set_library(self, library):
        """
        Sets library attached to this widget
        :param library:
        """

        self._library = library

    def refresh(self):
        """
        Refreshes widgets
        """

        self._blueprints_tree.refresh()

    def _on_blueprint_selected(self, current, previous):
        """
        Internal callback function that is called when a blueprint is selected
        :param current:
        :param previous:
        :return:
        """

        if not hasattr(current, 'item_type') or not current.item_type == consts.DataTypes.Blueprint:
            self._blueprints_scripts.set_object(None)
            self._blueprints_scripts.set_directory('')
            self._blueprints_scripts_options.set_option_object(None)
            self._blueprints_scripts_options.clear_options()
            if self._library:
                self._library.set_path(None)
            return

        blueprint_selected = current.data(0, Qt.UserRole)
        if not blueprint_selected:
            return

        self._blueprints_scripts.set_object(blueprint_selected)
        self._blueprints_scripts.set_directory(blueprint_selected.get_path())
        self._blueprints_scripts_options.set_option_object(blueprint_selected)
        self._blueprints_scripts_options.update_options()

        if self._library:
            self._library.set_path(blueprint_selected.get_path())
            blueprint_selected.set_library(self._library)


class BlueprintsTree(QTreeWidget, object):

    blueprintCreated = Signal(str)

    def __init__(self, project, parent=None):
        super(BlueprintsTree, self).__init__(parent)

        self._project = project

        self.setAlternatingRowColors(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.refresh()

        self.customContextMenuRequested.connect(self._on_custom_context_menu)

    def refresh(self):
        self.clear()

        project_path = self._project.get_full_path()

        builder_item = QTreeWidgetItem()
        builder_item.setText(0, 'RigBuilder')
        builder_item.setData(0, Qt.UserRole, helpers.BlueprintsHelpers.get_rigbuilder_blueprints_path())
        builder_item.item_type = 'root'
        project_item = QTreeWidgetItem()
        project_item.setText(0, 'Project: {}'.format(self._project.get_name()))
        project_item.setData(0, Qt.UserRole, project_path)
        project_item.item_type = 'root'

        self.addTopLevelItem(builder_item)
        self.addTopLevelItem(project_item)

        blueprints_found = helpers.BlueprintsHelpers.find_blueprints(project=self._project)
        if not blueprints_found:
            return

        for blueprint_found in blueprints_found:
            blueprint_name = blueprint_found.get_name()
            blueprint_item = QTreeWidgetItem()
            blueprint_item.setText(0, blueprint_name)
            blueprint_item.item_type = consts.DataTypes.Blueprint
            blueprint_item.setData(0, Qt.UserRole, blueprint_found)
            blueprint_path = blueprint_found.get_path()
            if blueprint_path.startswith(helpers.BlueprintsHelpers.get_rigbuilder_blueprints_path()):
                builder_item.addChild(blueprint_item)
            elif blueprint_path.startswith(project_path):
                project_item.addChild(blueprint_item)

        self.expandAll()

    def _on_custom_context_menu(self, pos):
        item = self.itemAt(pos)
        if not item or not hasattr(item, 'item_type'):
            return

        context_menu = QMenu(self)

        item_type = item.item_type
        if item_type == 'root':
            create_icon = resource.ResourceManager().icon('import')
            create_blueprint_action = context_menu.addAction(create_icon, 'New Blueprint')
            create_blueprint_action.triggered.connect(partial(self._on_create_blueprint, item.data(0, Qt.UserRole)))
        elif item_type == consts.DataTypes.Blueprint:
            play_icon = resource.ResourceManager().icon('play')
            build_blueprint_action = context_menu.addAction(play_icon, 'Build Blueprint')
            build_blueprint_action.triggered.connect(partial(self._on_build_blueprint, item.data(0, Qt.UserRole)))

        context_menu.exec_(self.mapToGlobal(pos))

    def _on_create_blueprint(self, root_path):
        blueprint_name = utils.show_rename_dialog('Blueprint Name', 'Type name of new blueprint:', 'blueprint')
        if not blueprint_name:
            return

        new_blueprint = blueprint.Blueprint(blueprint_name)
        new_blueprint.set_directory(root_path)
        blueprint_path = new_blueprint.create()
        if not blueprint_path or not os.path.isdir(blueprint_path):
            return

        self.blueprintCreated.emit(blueprint_path)

    def _on_build_blueprint(self, blueprint_to_build):
        if not blueprint_to_build:
            return

        blueprint_to_build.build()


class BlueprintScriptItem(scriptstree.ScriptItem, object):
    def __init__(self, parent=None):
        super(BlueprintScriptItem, self).__init__(parent=parent)


class BlueprintScripts(scriptstree.ScriptTree, object):

    HEADER_LABELS = ['Blueprint Scripts']
    ITEM_WIDGET = BlueprintScriptItem

    def __init__(self, settings, parent=None):
        super(BlueprintScripts, self).__init__(parent)


class BlueprintScriptsOptions(options.OptionsWidget, object):
    def __init_(self, settings=None, parent=None):
        super(BlueprintScriptsOptions, self).__init__(settings=settings, parent=parent)
