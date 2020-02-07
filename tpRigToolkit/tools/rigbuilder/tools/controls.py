#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains controls tool implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpQtLib.core import tool

from tpRigToolkit.tools.controlrig.core import controlrig

from tpRigToolkit.tools.rigbuilder.core import controls


class ControlsTool(tool.DockTool, object):

    NAME = 'Controls'
    TOOLTIP = 'Manages and create Rig Controls'
    DEFAULT_DOCK_AREA = Qt.LeftDockWidgetArea

    def __init__(self):
        super(ControlsTool, self).__init__()

        self._controls_widget = None
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

        # self._config = config.get_config('tpRigToolkit-controls')

    def show_tool(self):
        super(ControlsTool, self).show_tool()

        self._controls_widget = ControlsWidget()
        self._controls_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._content_layout.addWidget(self._controls_widget)


class ControlsWidget(controlrig.ControlsWidget, object):

    CONTROLS_LIB = controls.RigBuilderControlLib

    def __init__(self, controls_path=None, parent=None):
        super(ControlsWidget, self).__init__(controls_path=controls_path, parent=parent)
