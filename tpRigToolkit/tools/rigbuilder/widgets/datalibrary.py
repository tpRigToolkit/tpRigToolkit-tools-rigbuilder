#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains data library widget for tpRigToolkit.tools.rignode
"""

from __future__ import print_function, division, absolute_import

from tpQtLib.widgets.library import window

from tpRigToolkit.tools import rigbuilder
from tpRigToolkit.tools.rigbuilder.core import datalibrary


class DataLibraryWindow(window.LibraryWindow):

    LIBRARY_CLASS = datalibrary.DataLibrary

    def __init__(self, project=None, console=None, parent=None):

        self._project = project
        self._console = console

        # Settings used by the library
        library_settings = rigbuilder.get_library_settings()

        super(DataLibraryWindow, self).__init__(
            name='DataLibraryWindow',
            title='Data Library',
            settings=library_settings,
            allow_non_path=True,
            parent=parent
        )
        self.statusBar().hide()

    def manager(self):
        """
        Overrides base window.library manger function
        :return: DataManager
        """

        data_manager = rigbuilder.DataMgr()
        data_manager.set_library_window(self)

        return data_manager

    def set_create_widget(self, create_widget):
        """
        Overrides base window.LibraryWindow set_create_widget function
        Data path is automatically filled
        :return:
        """

        if not create_widget:
            return

        rig_path = self.path()
        is_rig = helpers.is_rig(rig_path)
        if not is_rig:
            return

        current_rig = helpers.get_rig(rig_path)
        current_rig.set_library(self.library())
        rig_data_path = current_rig.get_data_path()

        create_widget.set_folder_path(rig_data_path)
        create_widget._folder_widget.folder_line.setReadOnly(True)
        create_widget._folder_widget.folder_btn.setVisible(False)

        super(DataLibraryWindow, self).set_create_widget(create_widget)

    def _on_show_new_menu(self):
        """
        Overrides base window.LibraryWindow _on_show_new_menu function
        :return:
        """

        if not self.path():
            return

        return super(DataLibraryWindow, self)._on_show_new_menu()

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
