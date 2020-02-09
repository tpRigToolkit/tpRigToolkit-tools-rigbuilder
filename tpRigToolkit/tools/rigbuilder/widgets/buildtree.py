#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget for build tree
"""

from __future__ import print_function, division, absolute_import

from tpRigToolkit.core import resource

from tpRigToolkit.tools.rigbuilder.widgets import basetree


class BuildItem(basetree.BaseItem, object):
    def __init__(self, parent=None):
        super(BuildItem, self).__init__(parent=parent)


class BuildTree(basetree.BaseTree, object):

    HEADER_LABELS = ['Build']
    ITEM_WIDGET = BuildItem
    NEW_ITEM_NAME = 'new_item'

    def __init__(self, settings=None, parent=None):
        super(BuildTree, self).__init__(settings=settings, parent=parent)

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def refresh(self, sync=False):
        """
        Overrides base treewidgets.FileTreeWidget refresh function
        :param sync: bool
        """

        print('refreshgin ...')

    def _create_actions(self, context_menu):
        """
        Overrides base BuildTree _create_new_actions function
        Internal function that creates actions for the creation of new items
        :param context_menu: QMenu
        :return: list(QAction)
        """

        refresh_icon = resource.ResourceManager().icon('refresh')

        refresh_action = self._context_menu.addAction(refresh_icon, 'Refresh')

        refresh_action.triggered.connect(self._on_refresh)

    # ================================================================================================
    # ======================== CALLBACKS
    # ================================================================================================

    def _on_refresh(self):
        """
        Internal callback function that is triggered when the user selects Refresh action
        """

        self.refresh(sync=True)
