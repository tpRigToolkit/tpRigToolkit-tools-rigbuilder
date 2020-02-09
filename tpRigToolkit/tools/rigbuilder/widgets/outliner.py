#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains rig outliner widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

from tpQtLib.widgets import treewidgets

from tpRigToolkit.tools.rigbuilder.widgets import outlinertree


class RigOutliner(treewidgets.EditFileTreeWidget, object):

    description = 'Rig'
    TREE_WIDGET = outlinertree.RigOutlinerTree
    FILTER_WIDGET = treewidgets.FilterTreeDirectoryWidget

    def __init__(self, project=None, settings=None, console=None, parent=None):

        self._library = None
        self._settings = settings
        self._project = project
        self._console = console

        super(RigOutliner, self).__init__(parent=parent)

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def ui(self):
        super(RigOutliner, self).ui()

        policy = self.sizePolicy()
        policy.setHorizontalPolicy(policy.Maximum)
        policy.setHorizontalStretch(0)
        self.setSizePolicy(policy)

        self.tree_widget.set_console(self._console)

    def repaint(self, *args, **kwargs):
        super(RigOutliner, self).repaint(*args, **kwargs)
        self.tree_widget.repaint()

    def set_directory(self, directory):
        """
        Overrides base treewidgets.EditFileTreeWidget set_directory function
        If no directory is given, we do not update the direct ory
        :param directory: str
        """

        if not directory:
            return

        super(RigOutliner, self).set_directory(directory)

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def library(self):
        """
        Returns library linked to this library
        :return: Library
        """

        return self._library

    def set_library(self, library):
        """
        Sets library linked to this widget
        :param library: Library
        """

        self._library = library
        self.tree_widget.set_library(library)

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

        if not project:
            return

        self._project = project
        self.set_directory(project.full_path)

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