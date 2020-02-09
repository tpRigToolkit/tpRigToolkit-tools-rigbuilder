#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains rig outliner widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *

from tpPyUtils import path as path_utils
from tpQtLib.widgets import treewidgets

from tpRigToolkit.tools.rigbuilder.widgets import rigtree


class RigOutliner(treewidgets.EditFileTreeWidget, object):

    description = 'Rig'
    TREE_WIDGET = rigtree.RigOutlinerTree
    FILTER_WIDGET = treewidgets.FilterTreeDirectoryWidget

    copyDone = Signal()

    def __init__(self, project=None, settings=None, console=None, parent=None):

        self._library = None
        self._settings = settings
        self._project = project
        self._console = console
        self._copy_widget = None

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

        self.tree_widget.copySpecialRig.connect(self._on_copy_match)
        self.tree_widget.copyRig.connect(self._on_copy_done)

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

    def _on_edit(self, flag):
        """
        Overrides base treewidgets.EditFileTreeWidget _on_edit function
        Internal function that is called anytime the user presses the Edit button on the filter widget
        If edit is ON, drag/drop operations in tree widget are disabled
        :param flag: bool
        """

        super(RigOutliner, self)._on_edit(flag)

        self.tree_widget.edit_state = flag

    def _on_item_selection_changed(self):
        """
        Overrides base treewidgets.EditFileTreeWidget _on_item_selection_changed function
        Internal function that is called anytime the user selects an item on the TreeWidget
        Emits itemClicked signal with the name of the selected item and the item itself
        """

        name, item = super(RigOutliner, self)._on_item_selection_changed()
        if not name:
            return

        name = self.tree_widget._get_parent_path(item)
        if name:
            name = self._get_filter_name(name)

        if self._copy_widget:
            self._copy_widget.set_other_rig(name, self.directory)

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
        self.tree_widget.set_console(self._console)

    def set_current_item(self, item):
        """
        Selects given item in outliner tree widget
        :param item: QTreeWidgetItem
        """

        self.tree_widget.setCurrentItem(item)

    def get_rigs(self):
        """
        Returns a list with all rigs currently loaded in outliner
        :return: list(Rig)
        """

        def _visit_tree(lst, item):
            lst.append(item)
            for i in range(item.childCount()):
                _visit_tree(lst, item.child(i))

        rigs_list = list()
        for i in range(self.tree_widget.topLevelItemCount()):
            _visit_tree(rigs_list, self.tree_widget.topLevelItem(i))

        return rigs_list

    # ================================================================================================
    # ======================== INTERNAL
    # ================================================================================================

    def _get_filter_name(self, name):
        """
        Internal function that returns filtered name from given name
        :param name: str
        :return: str
        """

        filter_value = self.filter_widget.get_sub_path_filter()
        test_name = filter_value + '/' + name
        test_path = path_utils.join_path(self.directory, test_name)
        if path_utils.is_dir(test_path):
            name = test_name

        return name

    # ================================================================================================
    # ======================== CALLBACKS
    # ================================================================================================

    def _on_copy_match(self, rig_mame=None, directory=None):
        """
        Internal callback function that is callled when an item is copied match into clipboard
        :param rig_Name: str
        :param directory: str
        """

        print('Copied match ...')

    def _on_copy_done(self):
        """
        Internal callback function that is called when a rig is copied into clipboard
        """

        self.copyDone.emit()
