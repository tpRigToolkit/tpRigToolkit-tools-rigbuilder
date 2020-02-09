#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains builder widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpQtLib.core import base
from tpQtLib.widgets import breadcrumb

from tpRigToolkit.tools.rigbuilder.widgets import buildtree


class RigBuilder(base.DirectoryWidget, object):
    def __init__(self, project=None, settings=None, console=None, parent=None):

        self._library = None
        self._object = None
        self._project = project
        self._settings = settings
        self._console = console

        super(RigBuilder, self).__init__(parent=parent)

    def ui(self):
        super(RigBuilder, self).ui()

        title_widget = QFrame()
        title_widget.setObjectName('TaskFrame')
        title_widget.setFrameStyle(QFrame.StyledPanel)
        title_layout = QHBoxLayout()
        title_layout.setContentsMargins(2, 2, 2, 2)
        title_layout.setSpacing(2)
        title_widget.setLayout(title_layout)
        self._title = breadcrumb.BreadcrumbWidget()
        self.reset_title()

        title_layout.addItem(QSpacerItem(30, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        title_layout.addWidget(self._title)
        title_layout.addItem(QSpacerItem(30, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        self._builder_tree = buildtree.BuildTree(settings=self._settings)

        self.main_layout.addWidget(title_widget)
        self.main_layout.addWidget(self._builder_tree)

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def enable(self):
        """
        Enables user interaction on builder tree
        """

        self._builder_tree.setEnabled(True)

    def disable(self):
        """
        Disables user interaction on builder tree
        """

        self._builder_tree.setEnabled(False)

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

        if project:
            self._builder_tree.set_directory(self._project.full_path)
        else:
            self._builder_tree.set_directory(None)

    def library(self):
        """
        Returns data library linked to this widget
        :return: Library
        """

        return self._library

    def set_library(self, library):
        """
        Sets data library linked to this widget
        :param library: Library
        """

        self._library = library
        self._builder_tree.set_library(library)

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

    def builder_tree(self):
        """
        Returns rig pipeline scripts tree
        :return: BuilderTree
        """

        return self._builder_tree

    def set_title(self, name):
        """
        Internal function used to update the title
        :param name: str,
        """

        rig_names = name.split('/')
        self._title.set(rig_names)

    def reset_title(self):
        """
        Resets the current title
        """

        self._title.set(['No Rig Selected'])