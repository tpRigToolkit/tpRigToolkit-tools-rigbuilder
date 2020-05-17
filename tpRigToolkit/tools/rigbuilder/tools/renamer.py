#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains renamer tool implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpRigToolkit.tools.renamer.widgets import renamer

from tpRigToolkit.tools.rigbuilder.core import tool


class RenamerTool(tool.DockTool, object):

    NAME = 'Renamer'
    TOOLTIP = 'Allows to rename nodes'
    DEFAULT_DOCK_AREA = Qt.LeftDockWidgetArea

    def __init__(self):
        super(RenamerTool, self).__init__()

        self._renamer_widget = None
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

    def show_tool(self):
        super(RenamerTool, self).show_tool()

        self._renamer_widget = RenamerWidget()
        self._renamer_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._content_layout.addWidget(self._renamer_widget)


class RenamerWidget(renamer.RigToolkitRenamerWidget, object):

    def __init__(self, config=None, parent=None):
        super(RenamerWidget, self).__init__(config=config, parent=parent)
