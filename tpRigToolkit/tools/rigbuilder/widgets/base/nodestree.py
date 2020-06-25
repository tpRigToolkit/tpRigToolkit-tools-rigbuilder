#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains builder widget for Bulder Nodes Tree
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import search

from tpRigToolkit.tools import rigbuilder


class BuilderNodesTree(base.BaseWidget, object):

    nodeSelected = Signal()

    def __init__(self, parent=None):
        super(BuilderNodesTree, self).__init__(parent=parent)

        self.refresh()

    def ui(self):
        super(BuilderNodesTree, self).ui()

        splitter = QSplitter()
        splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        main_widget = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_widget.setLayout(main_layout)

        self._nodes_searcher = search.SearchFindWidget()
        self._nodes_tree = QTreeWidget()
        self._nodes_tree.setHeaderHidden(True)
        self._nodes_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(self._nodes_searcher)
        main_layout.addWidget(self._nodes_tree)

        extra_widget = QWidget()
        extra_layout = QVBoxLayout()
        extra_layout.setContentsMargins(0, 0, 0, 0)
        extra_layout.setSpacing(0)
        extra_widget.setLayout(extra_layout)
        self._node_description = QTextEdit()
        self._node_description.setPlaceholderText('Node description ...')
        self._node_description.setReadOnly(True)
        extra_layout.addWidget(self._node_description)

        splitter.addWidget(main_widget)
        splitter.addWidget(extra_widget)

        self.main_layout.addWidget(splitter)

    def setup_signals(self):
        self._nodes_tree.itemSelectionChanged.connect(self._on_node_selected)

    def selected_builder_node(self):
        selected_items = self._nodes_tree.selectedItems()
        if not selected_items:
            return None

        selected_item = selected_items[0]
        selected_node = selected_item.data(0, Qt.UserRole)

        return selected_node

    def refresh(self):
        self._fill_nodes()
        self._nodes_tree.expandAll()
        self._node_description.setText('')

    def _fill_nodes(self):
        self._nodes_tree.clear()

        all_packages = rigbuilder.PkgsMgr().registered_packages
        for pkg_name, pkg_inst in all_packages.items():
            pkg_item = QTreeWidgetItem()
            pkg_item.setText(0, pkg_name)
            self._nodes_tree.addTopLevelItem(pkg_item)
            for node_name, node_class in pkg_inst.builder_node_classes.items():
                node_item = QTreeWidgetItem()
                node_item.setText(0, node_name)
                node_item.setData(0, Qt.UserRole, node_class)
                pkg_item.addChild(node_item)

    def _on_node_selected(self):
        self._node_description.setText('')
        selected_node = self.selected_builder_node()
        if not selected_node:
            return

        self._node_description.setPlainText(selected_node.DESCRIPTION)
