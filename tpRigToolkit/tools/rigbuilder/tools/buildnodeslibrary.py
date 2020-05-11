#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains properties tool tool implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtWidgets import *

from tpRigToolkit.tools.rigbuilder.core import tool
from tpRigToolkit.tools.rigbuilder.widgets.base import nodestree


class BuldNodesLibrary(tool.DockTool, object):

    NAME = 'Build Nodes Library'
    TOOLTIP = 'Library that contains all available build nodes'
    IS_SINGLETON = True

    def __init__(self):
        super(BuldNodesLibrary, self).__init__()

        self._options_widget = None
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

    def show_tool(self):
        super(BuldNodesLibrary, self).show_tool()

        self._nodes_tree = nodestree.BuilderNodesTree()
        self._nodes_tree.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._content_layout.addWidget(self._nodes_tree)
