#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget for build tree
"""

from __future__ import print_function, division, absolute_import

import logging

from Qt.QtCore import *

from tpQtLib.core import qtutils

from tpRigToolkit.core import resource
from tpRigToolkit.tools import rigbuilder
from tpRigToolkit.tools.rigbuilder.core import utils
from tpRigToolkit.tools.rigbuilder.items import build
from tpRigToolkit.tools.rigbuilder.widgets import scriptstree

LOGGER = logging.getLogger('tpRigToolkit')


class BuildTree(scriptstree.ScriptTree, object):

    HEADER_LABELS = ['Build']
    ITEM_WIDGET = build.BuildItem
    NEW_ITEM_NAME = 'new_item'

    createNode = Signal()

    def __init__(self, settings=None, parent=None):
        super(BuildTree, self).__init__(settings=settings, parent=parent)

        self.setItemDelegate(build.BuildItemsDelegate(self))

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def _create_actions(self, context_menu):
        """
        Overrides base BuildTree _create_new_actions function
        Internal function that creates actions for the creation of new items
        :param context_menu: QMenu
        :return: list(QAction)
        """

        add_icon = resource.ResourceManager().icon('add')
        refresh_icon = resource.ResourceManager().icon('refresh')

        add_action = self._context_menu.addAction(add_icon, 'Add Builder Node')
        self._context_menu.addSeparator()
        refresh_action = self._context_menu.addAction(refresh_icon, 'Refresh')

        add_action.triggered.connect(self._on_add_builder_node)
        refresh_action.triggered.connect(self._on_refresh)

    def _post_setup_item(self, item, state):
        item.update_node()

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def builder_node(self):
        """
        Returns current selected builder node
        :return:
        """

        current_nodes = self.selectedItems()
        if not current_nodes:
            return None

        return current_nodes[0]

    def create_builder_node(self, builder_node, name=None, description=None):
        """
        Function that creates a new builder node of the current selected node
        :param builder_node:
        :param name:
        :param description:
        """

        if not builder_node:
            LOGGER.warning('No builder node to create!')
            return

        current_rig = self.object()
        if not current_rig:
            LOGGER.warning('Impossible to create new builder node because rig is not defined!')
            return

        node_name = name
        if not node_name:
            node_name = self._get_node_name()
        if not node_name:
            return

        node_path = current_rig.create_build_node(
            builder_node=builder_node, name=node_name, description=description, unique_name=True)
        if not node_path:
            LOGGER.error('Impossible to create new node!')
            return

        # NOTE: We must update data classes. Otherwise we have problems when
        # instancing custom data classes in data library
        rigbuilder.DataMgr().update_data_classes()

        self.refresh(sync=True)

    # ================================================================================================
    # ======================== INTERNAL
    # ================================================================================================

    def _get_node_name(self):
        """
        Internal function that returns the name of a valid node name
        :return: str
        """

        node_name = utils.show_rename_dialog('Node Name', 'Type name of new node:', 'new_node')
        if not node_name:
            return

        invalid_node_names = list()
        if invalid_node_names and node_name in invalid_node_names:
            qtutils.warning_message(
                'Node name "{}" is reserved. Default "node" name will be used'.format(code_name), parent=self)
            node_name = 'new_node'

        return node_name

    # ================================================================================================
    # ======================== CALLBACKS
    # ================================================================================================

    def _on_add_builder_node(self):
        self.createNode.emit()

    def _on_refresh(self):
        """
        Internal callback function that is triggered when the user selects Refresh action
        """

        self.refresh(sync=True)
