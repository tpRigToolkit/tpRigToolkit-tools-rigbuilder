#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains properties tool tool implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpDcc.libs.qt.widgets import options

from tpRigToolkit.tools.rigbuilder.core import tool


class PropertiesTool(tool.DockTool, object):

    NAME = 'Properties'
    TOOLTIP = 'Shows properties/options depending on the context'
    DEFAULT_DOCK_AREA = Qt.RightDockWidgetArea
    IS_SINGLETON = True

    def __init__(self):
        super(PropertiesTool, self).__init__()

        self._fill_delegate = None
        self.setWindowTitle(self.unique_name())
        self._created = False
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

    def show_tool(self):
        super(PropertiesTool, self).show_tool()

        if not self._created:
            self._create_ui()
            self._created = True

    def _create_ui(self):

        self._options_widget = options.OptionsWidget()
        self._options_widget.hide_edit_widget()
        self._content_layout.addWidget(self._options_widget)

    def clear(self):
        self._options_widget.clear_options()

    def refresh(self):
        self._options_widget.get_option_object().load_options()
        self._options_widget.update_options()

    def set_project(self, project):
        pass

    def set_object(self, object):
        self._options_widget.set_option_object(object)
        self.refresh()
