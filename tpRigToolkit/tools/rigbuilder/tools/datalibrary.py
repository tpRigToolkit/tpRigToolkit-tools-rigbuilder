#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains data library tool tool implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpRigToolkit.tools.rigbuilder.core import tool
from tpRigToolkit.tools.rigbuilder.widgets.base import datalibrary


class DataLibrary(tool.DockTool, object):

    NAME = 'Data Library'
    TOOLTIP = 'Manages the data for the project'
    DEFAULT_DOCK_AREA = Qt.LeftDockWidgetArea
    IS_SINGLETON = True

    def __init__(self):
        super(DataLibrary, self).__init__()

        self._data_library = None
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

    def show_tool(self):
        super(DataLibrary, self).show_tool()

        project = self._app.get_project()
        settings = self._app.settings()
        # theme = self._app.theme()

        if not self._data_library:
            console = self._app.get_console()
            self._data_library = datalibrary.DataLibraryWindow(project=project, console=console)
            self._data_library.setMinimumWidth(400)
            self._content_layout.addWidget(self._data_library)
            self._data_library.set_settings(settings)
            # self._data_library.set_theme(theme)
            self._data_library.set_path(project.get_full_path())

    def set_project(self, project):
        self._data_library.set_project(project)

    def set_path(self, path):
        self._data_library.set_path(path)

    def manager(self):
        return self._data_library.manager()

    def library(self):
        return self._data_library.library()

    def sync(self, force_start=False):
        return self._data_library.sync(force_start=force_start)
