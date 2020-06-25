#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains builder widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import dividers, treewidgets

from tpRigToolkit.tools.rigbuilder.widgets.base import nodestree
from tpRigToolkit.tools.rigbuilder.widgets.builder import buildtree


class RigBuilder(treewidgets.EditFileTreeWidget, object):

    description = 'Build'
    TREE_WIDGET = buildtree.BuildTree
    FILTER_WIDGET = treewidgets.FilterTreeDirectoryWidget

    createNode = Signal()

    def __init__(self, project=None, settings=None, console=None, parent=None):

        self._library = None
        self._project = project
        self._settings = settings
        self._console = console

        super(RigBuilder, self).__init__(parent=parent)

        self.tree_widget.set_settings(settings)
        self.disable()

    def setup_signals(self):
        super(RigBuilder, self).setup_signals()

        self.tree_widget.createNode.connect(self.createNode.emit)
        self.tree_widget.renameNode.connect(self.refresh)

    def _on_edit(self, flag):
        """
        Overrides base treewidgets.EditFileTreeWidget _on_edit function
        Internal function that is called anytime the user presses the Edit button on the filter widget
        If edit is ON, drag/drop operations in tree widget are disabled
        :param flag: bool
        """

        super(RigBuilder, self)._on_edit(flag)

        self.tree_widget.edit_state = flag

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def enable(self):
        """
        Enables user interaction on builder tree
        """

        self.tree_widget.setEnabled(True)

    def disable(self):
        """
        Disables user interaction on builder tree
        """

        self.tree_widget.setEnabled(False)

    def get_project(self):
        """
        Returns current RigBuilder project used by this widget
        :return: Project
        """

        return self._project

    def set_project(self, project):
        """
        Sets current RigBuilder project used by this widget
        :param project: Project
        """

        self._project = project

        if project:
            self.tree_widget.set_directory(self._project.full_path)
        else:
            self.tree_widget.set_directory(None)

    def rig(self):
        """
        Returns rig object linked to rig builder tree
        :return: RigObject
        """

        return self.tree_widget.object()

    def set_rig(self, rig):
        """
        Sets the object linked to builder tree
        :param rig: RigObject
        """

        self.tree_widget.set_object(rig)

        self.enable() if rig else self.disable()

    def library(self):
        """
        Returns data library linked to this widget
        :return: Library
        """

        return self._library

    def set_library(self, library):
        """
        Sets data library linked to this widget
        :param library: Library
        """

        self._library = library
        self.tree_widget.set_library(library)

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

    def builder_tree(self):
        """
        Returns rig pipeline scripts tree
        :return: BuilderTree
        """

        return self.tree_widget

    def current_builder_node(self):
        """
        Returns current selected builder node
        :return:
        """

        return self.tree_widget.builder_node()

    def refresh(self):
        """
        Refresh current item
        """

        self.tree_widget.refresh(sync=True)
        self.tree_widget.selectionModel().clearSelection()

    def create_builder_node(self, builder_node, name=None):
        """
        Function that creates a new builder node of the current selected node
        :param builder_node:
        :param name:
        """

        return self.tree_widget.create_builder_node(builder_node=builder_node, name=name)


class NodeBuilderCreator(base.BaseWidget, object):

    nodeCreated = Signal(object, str, object)
    creationCanceled = Signal()

    def __init__(self, parent=None):
        super(NodeBuilderCreator, self).__init__(parent=parent)

        self._rig = None
        self._build_node = None

        self.refresh()

    def ui(self):
        super(NodeBuilderCreator, self).ui()

        self._nodes_tree = nodestree.BuilderNodesTree()
        self._nodes_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        grid_main_widget = QWidget()
        grid_main_layout = QVBoxLayout()
        grid_main_layout.setContentsMargins(2, 2, 2, 2)
        grid_main_layout.setSpacing(2)
        grid_main_widget.setLayout(grid_main_layout)
        grid_layout = QGridLayout()
        display_name_lbl = QLabel('Display Name:')
        self._display_name_line = QLineEdit()
        self._display_name_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        grid_layout.addWidget(display_name_lbl, 0, 0, Qt.AlignRight)
        grid_layout.addWidget(self._display_name_line, 0, 1)
        grid_main_layout.addLayout(grid_layout)

        self.main_layout.addWidget(grid_main_widget)
        self.main_layout.addLayout(dividers.DividerLayout())
        self.main_layout.addWidget(self._nodes_tree)

        buttons_layout = QHBoxLayout()
        self.main_layout.addLayout(buttons_layout)
        self._ok_btn = QPushButton('Ok')
        self._cancel_btn = QPushButton('Cancel')
        buttons_layout.addWidget(self._ok_btn)
        buttons_layout.addWidget(self._cancel_btn)

    def setup_signals(self):
        self._ok_btn.clicked.connect(self._on_create_node)
        self._cancel_btn.clicked.connect(self.creationCanceled.emit)

    def rig(self):
        """
        Returns rig object linked to rig builder tree
        :return: RigObject
        """

        return self._rig

    def set_rig(self, rig):
        """
        Sets the object linked to builder tree
        :param rig: RigObject
        """

        self._rig = rig

    def build_node(self):
        return self._build_node

    def set_build_node(self, build_node):
        self._build_node = build_node

    def reset(self):
        self._display_name_line.setText('')

    def refresh(self):
        self._nodes_tree.refresh()

    def _on_create_node(self):
        selected_node = self._nodes_tree.selected_builder_node()
        if not selected_node:
            self.nodeCreated.emit(None, '', '', None)
            return

        node_display_name = self._display_name_line.text()

        self.nodeCreated.emit(selected_node, node_display_name, self._build_node)
