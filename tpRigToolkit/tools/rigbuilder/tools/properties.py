#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains properties tool tool implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpQtLib.core import tool


class PropertiesTool(tool.DockTool, object):

    NAME = 'Properties'
    TOOLTIP = 'Shows properties/options depending on the context'
    DEFAULT_DOCK_AREA = Qt.RightDockWidgetArea
    IS_SINGLETON = True

    def __init__(self):
        super(PropertiesTool, self).__init__()

        self._options_widget = None
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

    def show_tool(self):
        super(PropertiesTool, self).show_tool()

    def refresh(self):
        pass

    def set_project(self, project):
        pass

    def set_object(self, object):
        pass
