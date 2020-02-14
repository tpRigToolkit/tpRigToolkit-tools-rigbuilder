#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains properties tool tool implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpQtLib.core import tool

from tpRigToolkit.tools.rigbuilder.widgets import properties


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

        self._scroll_area = QScrollArea(self)
        self._scroll_area.setWidgetResizable(True)
        self._properties_widget = properties.PropertiesWidget()
        self._scroll_area.setWidget(self._properties_widget)
        self._properties_widget._search_layout.removeWidget(self._properties_widget._lock_btn)
        # self.add_button(self._properties_widget._lock_btn)
        self._properties_widget._search_layout.removeWidget(self._properties_widget._tear_off_btn)
        # self.add_button(self._properties_widget._tear_off_btn)
        self._content_layout.addWidget(self._scroll_area)

    def clear(self):
        self._properties_widget.clear()

    def refresh(self):
        print('refreshgigigigigigi')

    def assign_properties_widget(self, properties_fill_delegate):
        self._fill_delegate = properties_fill_delegate
        properties_fill_delegate(self._properties_widget)

    def set_project(self, project):
        pass

    def set_object(self, object):
        pass
