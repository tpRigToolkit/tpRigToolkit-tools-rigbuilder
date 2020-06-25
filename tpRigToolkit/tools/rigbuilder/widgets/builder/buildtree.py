#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget for build tree
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtGui import *

import tpDcc as tp
from tpDcc.libs.qt.core import qtutils
from tpDcc.libs.python import osplatform, timers, path as path_utils

import tpRigToolkit
from tpRigToolkit.tools.rigbuilder.core import utils, consts
from tpRigToolkit.tools.rigbuilder.items import build
from tpRigToolkit.tools.rigbuilder.widgets.rig import scriptstree


class BuildTree(scriptstree.ScriptTree, object):

    HEADER_LABELS = ['Build']
    ITEM_WIDGET = build.BuildItem
    NEW_ITEM_NAME = 'new_item'

    buildSignalsConnected = False

    createNode = Signal()
    renameNode = Signal()
    itemSelected = Signal(object)
    runFinished = Signal()

    def __init__(self, settings=None, parent=None):
        super(BuildTree, self).__init__(settings=settings, parent=parent)

        self.setItemDelegate(build.BuildItemsDelegate(self))

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def mouseReleaseEvent(self, event):
        item = self.itemAt(event.pos())
        if item and event.button() == Qt.LeftButton:
            self.itemSelected.emit(item)
        else:
            self.itemSelected.emit(None)

        super(BuildTree, self).mouseReleaseEvent(event)

    def refresh(self, sync=False, scripts_and_states=[]):
        super(BuildTree, self).refresh(sync=sync, scripts_and_states=scripts_and_states)

        for item in self._get_all_items():
            item.update_node()

    def _create_actions(self, context_menu):
        """
        Overrides base BuildTree _create_new_actions function
        Internal function that creates actions for the creation of new items
        :param context_menu: QMenu
        :return: list(QAction)
        """

        add_icon = tp.ResourcesMgr().icon('add')
        refresh_icon = tp.ResourcesMgr().icon('refresh')

        add_action = self._context_menu.addAction(add_icon, 'Add Builder Node')
        self._context_menu.addSeparator()
        refresh_action = self._context_menu.addAction(refresh_icon, 'Refresh')

        add_action.triggered.connect(self._on_add_builder_node)
        refresh_action.triggered.connect(self._on_refresh)

    def _setup_item(self, item, state):
        """
        Overrides base BuildTree _setup_item function
        Internal function that is called before adding an item into the tree
        It is used to set item before adding it
        :param item: ScriptManifestItem
        :param state: bool
        :return:
        """

        super(BuildTree, self)._setup_item(item=item, state=state)

        if not self.buildSignalsConnected and hasattr(item, 'buildSignals'):
            item.buildSignals.runNode.connect(self._on_run_current_item)
            item.buildSignals.runBlock.connect(self._on_run_current_group)
            item.buildSignals.addNode.connect(self._on_add_builder_node)
            item.buildSignals.renameNode.connect(self._on_rename_current_item)
            item.buildSignals.duplicateNode.connect(self._on_duplicate_current_item)
            item.buildSignals.deleteNode.connect(self._on_delete_current_item)
            item.buildSignals.setStartPoint.connect(self._on_set_start_point)
            item.buildSignals.cancelStartPoint.connect(self._on_cancel_start_point)
            item.buildSignals.setBreakPoint.connect(self._on_set_break_point)
            item.buildSignals.cancelBreakPoint.connect(self._on_cancel_break_point)
            item.buildSignals.browseNode.connect(self._on_browse_code)
            item.buildSignals.statusChanged.connect(self.repaint)

        self.buildSignalsConnected = True

    def _update_item(self, item):
        super(BuildTree, self)._update_item(item)

        item.update_node()

    def _rename_item(self, item, new_name):
        item.rename_node(new_name)
        super(BuildTree, self)._rename_item(item=item, new_name=new_name)
        item.update_node()
        self.renameNode.emit()

    def _run_item(self, item, run_level, object=None, run_children=False):
        """
        Internal function that launches main run function
        :param item: ScriptItem
        :param object: object
        :param run_children: bool
        """

        if object is None:
            object = self.builder_node()
        if not object:
            tpRigToolkit.logger.warning('Impossible to run script/s because builder node is not defined!')
            return

        self.scrollToItem(item)
        item.set_state(4)
        item.setExpanded(True)

        item.is_running = True

        background = item.background(0)
        orig_background = background
        color = QColor(1, 0, 0)
        background.setColor(color)
        item.setBackground(0, background)

        status = False

        try:
            if not item.node.rig:
                item.node.rig = object

            if run_level == consts.BuildLevel.PRE:
                status = item.node.pre_run()
            elif run_level == consts.BuildLevel.MAIN:
                status = item.node.run()
            elif run_level == consts.BuildLevel.POST:
                status = item.node.post_run()

            log = osplatform.get_env_var('RIGBUILDER_LAST_TEMP_LOG')
            item.set_log(log)

            if log.find('Warning') > -1 or log.find('WARNING') > -1 or log.find('warning') > -1:
                item.set_state(2)

        except Exception as exc:
            tpRigToolkit.logger.exception(exc)
        finally:
            valid_status = True

            if isinstance(status, list):
                status = status[0][-1]

            attr_status = bool(status == 'Success' or status is True)

            setattr(item, run_level, attr_status)
            if valid_status:
                valid_status = attr_status
            self.repaint()

        if valid_status:
            item.set_state(1)
        else:
            item.set_state(0)

        item.node.rig._run_nodes[item.node.get_name()] = item.node

        if not valid_status:
            return

        item.setBackground(0, orig_background)

        if run_children:
            self._run_children(item, run_level, object, recursive=True)

    def _run_children(self, item, level, object, recursive=True):
        """
        Internal function that executes children scripts of a given item. It can be recursively or not
        :param item: ScriptItem
        :param object: object
        :param recursive: bool
        """

        child_count = item.childCount()
        if not child_count:
            return

        item.setExpanded(True)

        if child_count:
            for i in range(child_count):
                child_item = item.child(i)
                child_item.set_state(-1)
            for i in range(child_count):
                child_item = item.child(i)
                self._run_item(child_item, level, child_item.node, run_children=recursive)

    def _reset_items(self):
        def _reset_item(item):
            if hasattr(item, 'set_state'):
                item.set_state(-1)
                for build_level in [consts.BuildLevel.PRE, consts.BuildLevel.MAIN, consts.BuildLevel.POST]:
                    setattr(item, build_level, None)
            for i in range(item.childCount()):
                _reset_item(item.child(i))

        _reset_item(self.invisibleRootItem())

    def run_current_item(self, external_code_library=None, group_only=False):
        """
        Internal function that executes current item
        :param external_code_library:
        :param group_only: bool
        """

        current_object = self.object()
        if not current_object:
            tpRigToolkit.logger.warning('Impossible to run script because object is not defined!')
            return

        osplatform.set_env_var('RIGBUILDER_RUN', True)
        osplatform.set_env_var('RIGBULIDER_STOP', False)

        scripts, states = current_object.get_scripts_manifest()
        items = self.selectedItems()
        if len(items) > 1:
            value = qtutils.get_permission('Start a new scene', parent=self)
            if value:
                tp.Dcc.new_scene(force=True, do_save=False)
            else:
                return

        watch = timers.StopWatch()
        watch.start(feedback=False)

        self._reset_items()
        self.repaint()

        if external_code_library:
            current_object.set_external_code_library(external_code_library)

        last_name = items[-1].text(0)
        last_path = self.get_item_path(items[-1])
        if last_path:
            last_name = path_utils.join_path(last_path, last_name)

        set_end_states = False
        for build_level in [consts.BuildLevel.PRE, consts.BuildLevel.MAIN, consts.BuildLevel.POST]:
            for i in range(len(scripts)):
                if osplatform.get_env_var('RIGBUILDER_RUN') == 'True':
                    if osplatform.get_env_var('RIGBULIDER_STOP') == 'True':
                        break
                    if set_end_states:
                        item = self._get_item_by_name(scripts[i])
                        if item:
                            item.set_state(-1)
                    for item in items:
                        script_name = item.text(0)
                        script_path = self.get_item_path(item)
                        if script_path:
                            script_name = path_utils.join_path(script_path, script_name)
                        if script_name == scripts[i]:
                            run_children = False
                            if group_only:
                                run_children = True
                            self._run_item(item, build_level, item.node, run_children)
                            if group_only:
                                break
                            if script_name == last_name:
                                set_end_states = True

        osplatform.set_env_var('RIGBUILDER_RUN', False)
        osplatform.set_env_var('RIGBULIDER_STOP', False)

        minutes, seconds = watch.stop()
        if minutes:
            tpRigToolkit.logger.info('Builder Nodes run in {} minutes and {} seconds'.format(minutes, seconds))
        else:
            tpRigToolkit.logger.info('Builder Nodes run in {} seconds'.format(seconds))

    def _on_run_current_item(self, external_code_library=None, group_only=False):
        self.run_current_item(external_code_library=external_code_library, group_only=group_only)

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def get_all_builder_nodes(self):
        """
        Returns all available build nodes
        :return: list
        """

        def _get_subtree_nodes(tree_widget_item):
            nodes = list()
            nodes.append(tree_widget_item)
            for i in range(tree_widget_item.childCount()):
                nodes.extend(_get_subtree_nodes(tree_widget_item.child(i)))

            return nodes

        all_items = []
        for i in range(self.topLevelItemCount()):
            top_item = self.topLevelItem(i)
            all_items.extend(_get_subtree_nodes(top_item))
        return all_items

    def builder_node(self):
        """
        Returns current selected builder node
        :return:
        """

        current_nodes = self.selectedItems()
        if not current_nodes:
            return None

        return current_nodes[0]

    def create_builder_node(self, builder_node, name=None):
        """
        Function that creates a new builder node of the current selected node
        :param builder_node:
        :param name:
        :param description:
        """

        if not builder_node:
            tpRigToolkit.logger.warning('No builder node to create!')
            return

        current_rig = self.object()
        if not current_rig:
            tpRigToolkit.logger.warning('Impossible to create new builder node because rig is not defined!')
            return

        node_name = name
        if not node_name:
            node_name = self._get_node_name()
        if not node_name:
            return

        node_path = current_rig.create_build_node(builder_node=builder_node, name=node_name, unique_name=True)
        if not node_path:
            tpRigToolkit.logger.error('Impossible to create new node!')
            return

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
                'Node name "{}" is reserved. Default "node" name will be used'.format(node_name), parent=self)
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
