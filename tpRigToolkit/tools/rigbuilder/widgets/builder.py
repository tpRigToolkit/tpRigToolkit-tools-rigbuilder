#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains builder widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpQtLib.core import base
from tpQtLib.widgets import splitters

from tpRigToolkit.tools.rigbuilder.widgets import buildtree, nodestree


class RigBuilder(base.DirectoryWidget, object):

    createNode = Signal()

    def __init__(self, project=None, settings=None, console=None, parent=None):

        self._library = None
        self._project = project
        self._settings = settings
        self._console = console

        super(RigBuilder, self).__init__(parent=parent)

    def ui(self):
        super(RigBuilder, self).ui()

        self._builder_tree = buildtree.BuildTree(settings=self._settings)

        self.main_layout.addWidget(self._builder_tree)

        self.disable()

    def setup_signals(self):
        self._builder_tree.createNode.connect(self.createNode.emit)

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def enable(self):
        """
        Enables user interaction on builder tree
        """

        self._builder_tree.setEnabled(True)

    def disable(self):
        """
        Disables user interaction on builder tree
        """

        self._builder_tree.setEnabled(False)

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
            self._builder_tree.set_directory(self._project.full_path)
        else:
            self._builder_tree.set_directory(None)

    def rig(self):
        """
        Returns rig object linked to rig builder tree
        :return: RigObject
        """

        return self._builder_tree.object()

    def set_rig(self, rig):
        """
        Sets the object linked to builder tree
        :param rig: RigObject
        """

        self._builder_tree.set_object(rig)

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
        self._builder_tree.set_library(library)

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

        return self._builder_tree

    def current_builder_node(self):
        """
        Returns current selected builder node
        :return:
        """

        return self._builder_tree.builder_node()

    def refresh(self):
        """
        Refresh current item
        """

        self._builder_tree.refresh(True)

    def create_builder_node(self, builder_node, name=None, description=None):
        """
        Function that creates a new builder node of the current selected node
        :param builder_node:
        :param name:
        :param description:
        """

        return self._builder_tree.create_builder_node(builder_node=builder_node, name=name, description=description)


class NodeBuilderCreator(base.BaseWidget, object):

    nodeCreated = Signal(object)
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
        description_lbl = QLabel('Description:')
        self._description_name_line = QLineEdit()
        self._description_name_line.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        grid_layout.addWidget(display_name_lbl, 0, 0, Qt.AlignRight)
        grid_layout.addWidget(self._display_name_line, 0, 1)
        grid_layout.addWidget(description_lbl, 1, 0, Qt.AlignRight)
        grid_layout.addWidget(self._description_name_line, 1, 1)
        grid_main_layout.addLayout(grid_layout)

        self.main_layout.addWidget(grid_main_widget)
        self.main_layout.addLayout(splitters.SplitterLayout())
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

    def refresh(self):
        self._nodes_tree.refresh()

    def _on_create_node(self):
        selected_node = self._nodes_tree.selected_builder_node()
        if not selected_node:
            self.nodeCreated.emit(None)
            return

        self.nodeCreated.emit(selected_node)
