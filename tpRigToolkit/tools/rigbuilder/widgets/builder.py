#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains builder widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

from tpQtLib.core import base

from tpRigToolkit.tools.rigbuilder.widgets import buildtree


class RigBuilder(base.DirectoryWidget, object):
    def __init__(self, project=None, settings=None, console=None, parent=None):

        self._library = None
        self._project = project
        self._settings = settings
        self._console = console

        super(RigBuilder, self).__init__(parent=parent)

    def ui(self):
        super(RigBuilder, self).ui()

        self._builder_tree = buildtree.BuildTree(settings=self._settings)

        self.main_layout.addWidget(self._builder_tree)

        self.disable()

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

    def rig(self):
        """
        Returns rig object linked to rig builder tree
        :return: RigObject
        """

        return self._builder_tree.object()

    def set_rig(self, rig):
        """
        Sets the object linked to builder tree
        :param rig: RigObject
        """

        self._builder_tree.set_object(rig)

        self.enable() if rig else self.disable()

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

    def refresh(self):
        """
        Refresh current item
        """

        self._builder_tree.refresh(True)
