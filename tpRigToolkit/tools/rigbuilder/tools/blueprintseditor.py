#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains rig presets tool implementation for tpRigBuilder
"""

from __future__ import print_function, division, absolute_import

import os
import logging

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpPyUtils import yamlio, path as path_utils
from tpQtLib.core import base, tool
from tpQtLib.widgets import stack, options, treewidgets

from tpRigToolkit.tools.rigbuilder.core import consts, blueprint
from tpRigToolkit.tools.rigbuilder.widgets import scriptstree


LOGGER = logging.getLogger('tpRigToolkit')


class BlueprintsEditor(tool.DockTool, object):

    NAME = 'Blueprints Editor'
    TOOLTIP = 'Manages current available blueprints'
    DEFAULT_DOCK_AREA = Qt.LeftDockWidgetArea
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

        if not self._created:
            self._create_ui()

    def close_tool(self):
        super(BlueprintsEditor, self).close_tool()

    def get_blueprints_path(self):
        """
        Returns default path where blueprints are located
        :return: str
        """

        from tpRigToolkit.tools.rigbuilder import blueprints

        return os.path.dirname(os.path.abspath(blueprints.__file__))

    def _create_ui(self):
        settings = self._app.settings()
        project = self._app.get_project()
        console = self._app.get_console()

        self._stack = stack.SlidingStackedWidget()
        self._content_layout.addWidget(self._stack)

        self._blueprints_viewer = BlueprintsViewer(project, settings, self.get_blueprints_path())
        self._blueprints_creator = BlueprintsCreator(project, self.get_blueprints_path())

        self._stack.addWidget(self._blueprints_viewer)
        self._stack.addWidget(self._blueprints_creator)

        self._create_blueprint_btn = QPushButton('Create')
        self._content_layout.addWidget(self._create_blueprint_btn)

        self._create_blueprint_btn.clicked.connect(self._on_create_blueprint)
        self._blueprints_creator.blueprintCreated.connect(self._on_blueprint_created)

    def _on_create_blueprint(self):
        self._stack.slide_in_index(1)
        self._create_blueprint_btn.setVisible(False)

    def _on_blueprint_created(self):
        self._stack.slide_in_index(0)
        self._create_blueprint_btn.setVisible(True)
        self._blueprints_viewer.refresh()


class BlueprintsCreator(base.BaseWidget, object):

    blueprintCreated = Signal(str)

    def __init__(self, project, blueprints_path, parent=None):

        self._project = project
        self._blueprints_path = blueprints_path

        super(BlueprintsCreator, self).__init__(parent=parent)

    def ui(self):
        super(BlueprintsCreator, self).ui()

        grid_layout = QGridLayout()
        self.main_layout.addLayout(grid_layout)

        name_lbl = QLabel('Name:')
        self._name_line = QLineEdit()
        self._name_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        path_lbl = QLabel('Path')
        self._path_combo = QComboBox()
        self._path_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self._path_line = QLineEdit()
        self._path_line.setReadOnly(True)

        grid_layout.addWidget(name_lbl, 0, 0, Qt.AlignRight)
        grid_layout.addWidget(self._name_line, 0, 1)
        grid_layout.addWidget(path_lbl, 1, 0, Qt.AlignRight)
        grid_layout.addWidget(self._path_combo, 1, 1)
        grid_layout.addWidget(self._path_line, 2, 0, 1, 2)

        self._fill_path_combo()

        self._create_btn = QPushButton('Create')
        self.main_layout.addItem(QSpacerItem(0, 10, QSizePolicy.Preferred, QSizePolicy.Expanding))
        self.main_layout.addWidget(self._create_btn)

    def setup_signals(self):
        self._create_btn.clicked.connect(self._on_create)
        self._path_combo.currentIndexChanged.connect(self._on_path_index_changed)

    def _fill_path_combo(self):
        """
        Internal function that fills combo
        """

        self._path_combo.clear()
        self._path_combo.addItem('RigBuilder', userData=self._blueprints_path)
        self._path_combo.addItem('Project: {}'.format(self._project.get_name()), userData=self._project.get_full_path())
        self._path_line.setText(self._path_combo.currentData())

    def _create_blueprint(self, name, path):
        new_blueprint = blueprint.Blueprint(name=name, directory=path)
        blueprint_path = new_blueprint.create()

        return blueprint_path

    def _on_path_index_changed(self, index):
        self._path_line.setText(self._path_combo.currentData())

    def _on_create(self):
        blueprint_name = self._name_line.text().strip().replace(' ', '_')
        blueprint_path = self._path_combo.currentData()
        if not blueprint_name:
            LOGGER.warning('Type a name for the blueprint!')
            return
        if not os.path.isdir(blueprint_path):
            LOGGER.warning('Blueprint target path does not exists: "{}!"'.format(blueprint_path))
            return

        created_path = self._create_blueprint(blueprint_name, blueprint_path)
        if not created_path or not os.path.isdir(created_path):
            return

        self.blueprintCreated.emit(created_path)

        self._name_line.setText('')
        self._path_combo.clear()


class BlueprintsViewer(base.BaseWidget, object):
    def __init__(self, project, settings, blueprints_path, parent=None):

        self._project = project
        self._settings = settings
        self._blueprints_path = blueprints_path

        super(BlueprintsViewer, self).__init__(parent=parent)

    def ui(self):
        super(BlueprintsViewer, self).ui()

        main_splitter = QSplitter()
        main_splitter.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.main_layout.addWidget(main_splitter)

        self._blueprints_tree = BlueprintsTree(blueprints_path=self._blueprints_path, project=self._project)

        right_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(self._blueprints_tree)
        main_splitter.addWidget(right_splitter)

        self._blueprints_scripts = BlueprintScripts(settings=self._settings)
        self._blueprints_scripts_options = BlueprintScriptsOptions(project=self._project)
        right_splitter.addWidget(self._blueprints_scripts)
        right_splitter.addWidget(self._blueprints_scripts_options)
        right_splitter.addWidget(self._blueprints_scripts_options)

    def setup_signals(self):
        self._blueprints_tree.currentItemChanged.connect(self._on_blueprint_selected)

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
            return

        blueprint_selected = current.data(0, Qt.UserRole)
        if not blueprint_selected:
            return

        self._blueprints_scripts.set_object(blueprint_selected)
        self._blueprints_scripts.set_directory(blueprint_selected.get_path())


class BlueprintsTree(QTreeWidget, object):
    def __init__(self, project, blueprints_path, parent=None):
        super(BlueprintsTree, self).__init__(parent)

        self._project = project
        self._blueprints_path = blueprints_path

        self.setAlternatingRowColors(True)

        self.refresh()

    def refresh(self):
        self.clear()

        project_path = self._project.get_full_path()

        builder_item = QTreeWidgetItem()
        builder_item.setText(0, 'RigBuilder')
        builder_item.setData(0, Qt.UserRole, self._blueprints_path)
        builder_item.item_type = 'root'
        project_item = QTreeWidgetItem()
        project_item.setText(0, 'Project: {}'.format(self._project.get_name()))
        builder_item.setData(0, Qt.UserRole, project_path)
        project_item.item_type = 'root'

        self.addTopLevelItem(builder_item)
        self.addTopLevelItem(project_item)

        blueprints_found = self._search_blueprints()
        if not blueprints_found:
            return

        for blueprint_found in blueprints_found:
            blueprint_name = blueprint_found.get_name()
            blueprint_item = QTreeWidgetItem()
            blueprint_item.setText(0, blueprint_name)
            blueprint_item.item_type = consts.DataTypes.Blueprint
            blueprint_item.setData(0, Qt.UserRole, blueprint_found)
            blueprint_path = blueprint_found.get_path()
            if blueprint_path.startswith(self._blueprints_path):
                builder_item.addChild(blueprint_item)
            elif blueprint_path.startswith(project_path):
                project_item.addChild(blueprint_item)

        self.expandAll()

    def _get_paths_to_find(self):
        """
        Internal function that returns all paths where blueprints will be search
        :return: list(str)
        """

        return [self._blueprints_path, self._project.get_full_path()]

    def _search_blueprints(self):
        """
        Internal function that searches blueprints in folders
        :return: list(str)
        """

        paths_to_find = self._get_paths_to_find()
        if not paths_to_find:
            return

        blueprints_found = list()
        for path_to_find in paths_to_find:
            for root, _, filenames in os.walk(path_to_find):
                if blueprint.Blueprint.BLUEPRINT_DATA_FILE_NAME in filenames:
                    for filename in filenames:
                        if filename.startswith(blueprint.Blueprint.BLUEPRINT_DATA_FILE_NAME):
                            data_file_path = path_utils.clean_path(os.path.join(root, filename))
                            try:
                                data_dict = yamlio.read_file(data_file_path)
                                if not data_dict:
                                    continue
                                data_type = data_dict.get('data_type', None)
                                if not data_type:
                                    continue
                                if data_type == consts.DataTypes.Blueprint:
                                    blueprint_name = os.path.basename(os.path.dirname(data_file_path))
                                    blueprints_found.append(blueprint.Blueprint(blueprint_name, path_to_find))
                            except Exception as exc:
                                continue

        return blueprints_found


class BlueprintScriptItem(scriptstree.ScriptItem, object):
    def __init__(self, parent=None):
        super(BlueprintScriptItem, self).__init__(parent=parent)


class BlueprintScripts(scriptstree.ScriptTree, object):

    HEADER_LABELS = ['Blueprint Scripts']
    ITEM_WIDGET = BlueprintScriptItem

    def __init__(self, settings, parent=None):
        super(BlueprintScripts, self).__init__(parent)


class BlueprintScriptsOptions(base.BaseWidget, object):
    def __init_(self, project, parent=None):

        self._project = project

        super(BlueprintScriptsOptions, self).__init__(parent)

    def ui(self):
        super(BlueprintScriptsOptions, self).ui()

        self._options = options.OptionsWidget()
        self.main_layout.addWidget(self._options)
