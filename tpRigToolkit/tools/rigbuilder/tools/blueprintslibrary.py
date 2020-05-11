#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains properties tool tool implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpDcc.libs.qt.widgets import stack

from tpRigToolkit.tools.rigbuilder.core import consts, tool
from tpRigToolkit.tools.rigbuilder.objects import helpers


class BlueprintsLibrary(tool.DockTool, object):

    NAME = 'Blueprints Library'
    TOOLTIP = 'Library that contains all available blueprints'
    IS_SINGLETON = True

    def __init__(self):
        super(BlueprintsLibrary, self).__init__()

        self._created = False
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

    def show_tool(self):
        super(BlueprintsLibrary, self).show_tool()

        if not self._created:
            self._create_ui()
            self._created = True

    def _create_ui(self):
        project = self._app.get_project()

        self._stack = stack.SlidingStackedWidget()
        self._content_layout.addWidget(self._stack)

        self._blueprints_list = BlueprintsList(project)

        self._stack.addWidget(self._blueprints_list)


class BlueprintsList(QListWidget, object):
    def __init__(self, project, parent=None):
        super(BlueprintsList, self).__init__(parent)


        self._project = project

        self.refresh()

    def refresh(self):
        self.clear()

        blueprints_found = helpers.BlueprintsHelpers.find_blueprints(project=self._project)
        if not blueprints_found:
            return

        for blueprint_found in blueprints_found:
            blueprint_name = blueprint_found.get_name()
            blueprint_item = QListWidgetItem()
            blueprint_item.setText(blueprint_name)
            blueprint_item.item_type = consts.DataTypes.Blueprint
            blueprint_item.setData(Qt.UserRole, blueprint_found)
            self.addItem(blueprint_item)
