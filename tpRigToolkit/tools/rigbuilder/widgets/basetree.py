#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget to show rig base trees
"""

from __future__ import print_function, division, absolute_import

import os
import logging

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDccLib as tp
from tpPyUtils import fileio, path as path_utils
from tpQtLib.core import qtutils
from tpQtLib.widgets import treewidgets

from tpRigToolkit.tools.rigbuilder.core import utils
from tpRigToolkit.tools.rigbuilder.items import base

LOGGER = logging.getLogger('tpRigToolkit')


class BaseTree(treewidgets.FileTreeWidget, object):

    HEADER_LABELS = ['Build']
    ITEM_WIDGET = base.BaseItem
    NEW_ITEM_NAME = 'new_rig'

    itemCreated = Signal(object)
    itemRenamed = Signal(object, object)
    itemRemoved = Signal(object)
    itemDuplicated = Signal()
    itemFocused = Signal()

    def __init__(self, settings=None, parent=None):
        super(BaseTree, self).__init__(parent=parent)

        self._object = None
        self._library = None
        self._settings = settings

        self._handle_selection_change = True
        self._update_checkbox = True
        self._shift_activate = False
        self._dragged_item = None
        self._break_index = None
        self._start_index = None
        self._break_item = None
        self._start_item = None
        self._hierarchy = True

        self._context_menu = None

        self.setSortingEnabled(False)
        self.setSelectionMode(self.ExtendedSelection)
        self.setDragDropMode(self.DragDrop)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setAutoScroll(False)
        self.setDefaultDropAction(Qt.MoveAction)
        self.invisibleRootItem().setFlags(Qt.ItemIsDropEnabled)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        header = self.header()
        header.setDefaultAlignment(Qt.AlignCenter)
        self._checkbox = QCheckBox(header)
        self._checkbox.move(4, 4)

        self._create_context_menu()

        self._checkbox.stateChanged.connect(self._on_set_all_checked)
        self.customContextMenuRequested.connect(self._on_item_menu)

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def resizeEvent(self, event):
        """
        Overrides base treewidgets.FileTreeWidget resizeEvent function
        Places update all checkbox to proper position
        :param event: QResizeEvent
        :return:
        """

        super(BaseTree, self).resizeEvent(event)
        self._checkbox.setGeometry(QRect(3, 2, 16, 17))

    def mousePressEvent(self, event):
        self._handle_selection_change = True
        item = self.itemAt(event.pos())
        parent = self.invisibleRootItem()
        if item:
            if item.parent():
                parent = item.parent()
        self._dragged_item = item
        super(BaseTree, self).mousePressEvent(event)
        self.itemFocused.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Shift:
            self._shift_activate = True

    def keyReleaseEvent(self ,event):
        if event.key() == Qt.Key_Shift:
            self._shift_activate = False

    def dragEnterEvent(self, event):
        if event.mimeData().hasText():
            event.setDropAction(Qt.CopyAction)
            event.accept()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasText:
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasText():
            if not self.library():
                event.ignore()
            if not self.library().manager():
                event.ignore()

            item = self.library().manager().item_from_path(event.mimeData().text())
            if not item:

                event.ignore()
            if not os.path.isfile(item.path()):
                event.ignore()
            data_name, data_extension = os.path.splitext(os.path.basename(item.path()))
            self._on_create_data_import(data_name=data_name, data_extension=data_extension)
            event.accept()
        else:
            event.ignore()

    def _add_item(self, file_name, state, parent=None, **kwargs):
        """
        Internal function that adds a new item to the tree
        :param file_name: str
        :param state: int
        :param parent: ScriptItem
        :param update_manifest: bool
        :return: ScriptItem
        """

        if file_name.count('/') > 0:
            basename = path_utils.get_basename(file_name)
            item = super(BaseTree, self)._add_item(basename, parent=False)
        elif file_name.count('/') == 0:
            item = super(BaseTree, self)._add_item(file_name, parent=parent)

        self._setup_item(item, state)

        return item

    def _get_ancestors(self, item):
        """
        Internal function that returns all ancestor items of the given item
        :param item: ScripItem
        :return: list(ScriptItem)
        """

        child_count = item.childCount()
        items = list()
        for i in range(child_count):
            child = item.child(i)
            children = self._get_ancestors(child)
            items.append(child)
            if children:
                items += children

        return items

    def _on_item_collapsed(self, item):
        """
        Internal callback function triggered when an item is collapsed
        :param item: ScriptItem
        """

        super(BaseTree, self)._on_item_collapsed(item=item)
        if self._shift_activate:
            child_count = item.childCount()
            for i in range(child_count):
                children = self._get_ancestors(item.child(i))
                item.child(i).setExpanded(False)
                for child in children:
                    child.setExpanded(False)

    def _on_item_expanded(self, item):
        """
        Internal callback function triggered when an item is expanded
        :param item: ScriptItem
        """

        if self._shift_activate:
            child_count = item.childCount()
            for i in range(child_count):
                children = self._get_ancestors(item.child(i))
                item.child(i).setExpanded(True)
                for child in children:
                    child.setExpanded(True)

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def settings(self):
        """
        Returns script tree settings
        :return: QtSettings
        """

        return self._settings

    def set_settings(self, settings):
        """
        Sets script tree settings
        :param settings: QtSettings
        """

        self._settings = settings

    def object(self):
        """
        Returns current script object
        :return: object
        """

        return self._object

    def set_object(self, script_object):
        """
        Returns current script object tree
        :param script_object: object
        """

        self._object = script_object

    def library(self):
        """
        Returns data library linked to this widget
        :return: Liibrary
        """

        return self._library

    def set_library(self, library):
        """
        Sets data library linked to this widget
        :param library: Library
        """

        self._library = library

    def break_index(self):
        """
        Returns break index
        :return: int
        """

        return self._break_index

    def can_handle_selection_changes(self):
        """
        Returns whether the tree can handle events when the user changes script selection
        :return: bool
        """

        return self._handle_selection_change

    def has_start_point(self):
        """
        Returns whether start point is defined or not
        :return: bool
        """

        if self._start_index is not None:
            return True

        return False

    def is_break_point(self, directory):
        """
        Checks whether item has a break point or not
        :param directory: str
        :return: bool
        """

        item = self._get_item_by_name(directory)
        model_index = self.indexFromItem(item)
        index = model_index.internalId()
        if index == self._break_index:
            return True

        return False

    def is_start_point(self, directory):
        """
        Checks whether item has a start point or not
        :param directory: str
        :return: bool
        """

        item = self._get_item_by_name(directory)
        model_index = self.indexFromItem(item)
        index = model_index.internalId()
        if index == self._start_index:
            return True

        return False

    def set_break_point(self, item=None):
        """
        Sets break point in given item
        :param item: ScriptItem
        """

        self.cancel_break_point()
        if not item:
            items = self.selectedItems()
            if not items:
                return
            item = items[0]
        self.clearSelection()

        item_index = self.indexFromItem(item)
        if item_index.internalId() == self._start_index:
            self.cancel_start_point()

        self._break_index = item_index.internalId()
        self._break_item = item
        if tp.Dcc.get_name() == tp.Dccs.Maya:
            brush = QBrush(QColor(70, 0, 0))
        else:
            brush = QBrush(QColor(240, 230, 230))

        item.setBackground(0, brush)

    def set_start_point(self, item=None):
        """
        Sets starts point in given item
        :param item: ScriptItem
        """

        self.cancel_start_point()
        if not item:
            items = self.selectedItems()
            if not items:
                return
            item = items[0]
        self.clearSelection()

        item_index = self.indexFromItem(item)
        if item_index.internalId() == self._break_index:
            self.cancel_break_point()

        self._start_index = item_index.internalId()
        self._start_item = item
        if tp.Dcc.get_name() == tp.Dccs.Maya:
            brush = QBrush(QColor(0, 70, 20))
        else:
            brush = QBrush(QColor(230, 240, 230))

        item.setBackground(0, brush)

    def cancel_break_point(self):
        """
        Removes break point
        """

        if self._break_item:
            try:
                self._break_item.setBackground(0, QBrush())
            except Exception:
                pass
        self._break_index = None
        self._break_item = None
        self.repaint()

    def cancel_start_point(self):
        """
        Removes start point
        """

        if self._start_item:
            try:
                self._start_item.setBackground(0, QBrush())
            except Exception:
                pass
        self._start_index = None
        self._start_item = None
        self.repaint()

    def cancel_points(self):
        """
        Removes break and start points
        """

        self.cancel_start_point()
        self.cancel_break_point()

    def reset_items_state(self):
        """
        Resets the states of all objects
        """

        items = self._get_all_items()
        for item in items:
            item.set_state(-1)

    def set_item_state(self, directory, state):
        """
        Sets the state of the item
        :param directory: str
        :param state: int
        """

        item_name = directory
        item = self._get_item_by_name(item_name)
        if not item:
            return
        if state > -1:
            self.scrollToItem(item)
        item.set_state(state)

    def set_item_log(self, directory, log):
        """
        Sets the item log
        :param directory: str
        :param log: str
        """

        item_name = directory
        item = self._get_item_by_name(item_name)
        if not item:
            return
        item.set_log(log)

    # ================================================================================================
    # ======================== ITEMS
    # ================================================================================================

    def get_item_path(self, item):
        """
        Returns the path to an item from the top tree level to down
        :param item: QTreeWidgetItem
        :return: str
        """

        return item.get_path()

    # ================================================================================================
    # ======================== INTERNAL
    # ================================================================================================

    def _create_context_menu(self):
        """
        Internal function that creates context menu for script tree
        """

        self._context_menu = QMenu()

        self._create_actions(self._context_menu)

    def _create_actions(self, context_menu):
        """
        Internal function that creates actions
        :param context_menu: QMenu
        """

        return None

    def _edit_actions_visible(self, flag):
        """
        Internal function used to show/hide actions that are related with script edition
        :param flag: bool
        """

        for action in self._edit_actions:
            action.setVisible(flag)

    def _get_code_name(self):
        """
        Internal function that returns the name of a valid code name
        :return: str
        """

        code_name = utils.show_rename_dialog('Script Name', 'Type name of current script:', 'code.py')
        if not code_name:
            return
        invalid_code_names = list()
        if invalid_code_names and code_name in invalid_code_names:
            qtutils.warning_message(
                'Code name "{}" is reserved. Default "code" name will be used'.format(code_name), parent=self)
            code_name = 'code'
        code_name = fileio.remove_extension(code_name)

        return code_name

    def _setup_item(self, item, state):
        """
        Internal function that is called before adding an item into the tree
        It is used to set item before adding it
        :param item: ScriptManifestItem
        :param state: bool
        :return:
        """

        if state:
            item.setCheckState(0, Qt.Checked)
        else:
            item.setCheckState(0, Qt.Unchecked)

        if self._hierarchy:
            item.setFlags(
                Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled |
                Qt.ItemIsUserCheckable | Qt.ItemIsDropEnabled)
        else:
            item.setFlags(
                Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled |
                Qt.ItemIsDragEnabled | Qt.ItemIsUserCheckable)

        item.set_object(self.object())

    def _post_setup_item(self, item, state):
        """
       Internal function that is called after adding an item into the tree
       :param item: ScriptManifestItem
       :param state: bool
       """

        pass

    def _get_item_path_name(self, item, keep_extension=False):
        """
        Returns the script name with path
        :param item: QTreeWidgetItem
        :param keep_extension: bool, Whether to return the path to the file with the file extension or not
        :return: str
        """

        item_name = item.text(0)
        if not keep_extension:
            item_name = fileio.remove_extension(item_name)

        item_path = self.get_item_path(item)
        if item_path:
            item_name = path_utils.join_path(item_path, item_name)

        return item_name

    def _get_item_path_full_name(self, item, keep_extension=False):
        """
        Returns the script name with full path
        :param item: QTreeWidgetItem
        :param keep_extension: bool, Whether to return the path to the file with the file extension or not
        :return: str
        """

        item_name = item.text(0)
        folder_name = fileio.remove_extension(item_name)
        if not keep_extension:
            item_name = folder_name

        item_path = self.get_item_path(item)
        if item_path:
            item_path = path_utils.join_path(item_path, folder_name)
        else:
            item_path = folder_name
        item_name = path_utils.join_path(item_path, item_name)

        return item_name

    def _get_all_items(self):
        """
        Returns all items in the tree
        :return: list<QTreeWidgetItem>
        """

        item_count = self.topLevelItemCount()
        items = list()
        for i in range(item_count):
            item = self.topLevelItem(i)
            ancestors = self._get_ancestors(item)
            items.append(item)
            if ancestors:
                items += ancestors

        return items

    def _get_item_by_name(self, item_name):
        """
        Returns tree item by its name
        :param item_name: str
        :return: QTreeWidgetItem
        """

        items = self._get_all_items()
        for item in items:
            check_name = self._get_item_path_name(item, keep_extension=True)
            if check_name == item_name:
                return item

        return None

    def _get_entered_item(self, event):
        """
        Returns item that is located in the position of the given event cursor position
        If not item is detected, root tree object will be returned
        :param event: QMouseEvent
        :return: QTreeWidgetItem
        """

        entered_item = self.itemAt(event.pos())
        if not entered_item:
            entered_item = self.invisibleRootItem()

        return entered_item

    def _custom_refresh(self, scripts, states):
        """
        Internal function that updates scripts taking into account their states
        :param scripts: list<str>
        :param states: list<str>
        :return:
        """

        files = self._get_files(scripts, states)
        if not files:
            self.clear()
            return

        self._load_files(files)
        self.refreshed.emit()

    def _sync_scripts(self):
        """
        Internal function that sync all current task scripts on tree
        """

        current_object = self.object()
        if not current_object:
            LOGGER.debug('Impossible to sync scripts because object is not defined!')
            return

        current_object.sync()

    def _rename_item(self, item, new_name):
        """
        Internal function that renames with script item
        :param item: ScriptItem
        :param new_name: str
        """

        current_object = self.object()
        if not current_object:
            LOGGER.warning('Impossible to rename item because object is not defined!')
            return

        new_name = str(new_name)
        test_name = fileio.remove_extension(new_name)
        if new_name and not test_name:
            new_name = '_' + new_name[1:]
        new_name = fileio.remove_extension(new_name)
        item_path = self.get_item_path(item)
        if item_path:
            new_name = path_utils.join_path(item_path, new_name)

        old_name = self._old_name
        old_name = fileio.remove_extension(old_name)
        if item_path:
            old_name = path_utils.join_path(item_path, old_name)

        file_name = current_object.rename_code(old_name, new_name)
        new_file_name = fileio.remove_extension(file_name)
        file_path = current_object.get_code_file(new_file_name)
        basename = path_utils.get_basename(file_path)

        item.set_text(basename)

        self.itemRenamed.emit(old_name, new_name)

    def _move_item(self, old_name, new_name, item):
        """
        Internal function that handles the move of an item in the file system
        :param old_name: str
        :param new_name: str
        :param item: ScriptItem
        """
        after_name = self._handle_item_reparent(old_name, new_name)
        basename = path_utils.get_basename(after_name)
        self.itemRenamed.emit(old_name, after_name)

    def _reparent_item(self, name, item, parent_item):
        """
        Internal function that handles the parenting of an item
        :param name: str
        :param item: ScriptItem
        :param parent_item: ScriptItem
        """

        current_parent = item.parent()
        if not current_parent:
            current_parent = self.invisibleRootItem()

        if current_parent and parent_item:
            old_name = self._get_item_path_name(item)
            parent_path = self._get_item_path_name(parent_item)
            new_name = path_utils.join_path(parent_path, name)
            current_parent.removeChild(item)
            parent_item.addChild(item)
            old_name = fileio.remove_extension(old_name)
            new_name = fileio.remove_extension(new_name)

            self._move_item(old_name, new_name, item)

    # ================================================================================================
    # ======================== CALLBACKS
    # ================================================================================================

    def _on_item_menu(self, pos):
        """
        Internal function that is called when the user right clicks an item of the tree and shows the contextual
        menu for that item
        :param pos: QPos
        """

        current_object = self.object()
        if not current_object:
            return

        items = self.selectedItems()
        item = None
        if items:
            item = items[0]
        if item:
            context_menu = item.get_context_menu()
            # self._edit_actions_visible(True)
        else:
            context_menu = self._context_menu
            # self._edit_actions_visible(False)

        # if len(items) > 1:
        #     self._edit_actions_visible(False)
        #     self._run_action.setVisible(True)
        #     self._delete_action.setVisible(True)

        context_menu.exec_(self.viewport().mapToGlobal(pos))

    def _on_set_all_checked(self, check_number):
        """
        Internal callback function that checks/unchecks all scripts in script tree
        :param check_number: int, check value (2 = Check , 1 = Uncheck)
        """

        if not self._update_checkbox:
            return

        if check_number == 2:
            state = Qt.Checked
        else:
            state = Qt.Unchecked

        value = qtutils.get_permission(
            'This will activate/deactivate all code. Perhaps consider saving your manifest before continuing.\n\n\n Continue?',
            parent=self, title='Warning: Activate/Deactivate all code')
        if not value:
            self._update_checkbox = False
            if check_number == 0:
                self._checkbox.setCheckState(Qt.Checked)
            elif check_number == 2:
                self._checkbox.setCheckState(Qt.Unchecked)
            self._update_checkbox = True
            return

        for it in QTreeWidgetItemIterator(self):
            item = it.value()
            if item:
                item.setCheckState(0, state)
