#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains properties tool tool implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtWidgets import *

from tpQtLib.core import tool


class BlueprintsLibrary(tool.DockTool, object):

    NAME = 'Blueprints Library'
    TOOLTIP = 'Library that contains all available blueprints'
    IS_SINGLETON = True

    def __init__(self):
        super(BlueprintsLibrary, self).__init__()

        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

    def show_tool(self):
        super(BlueprintsLibrary, self).show_tool()
