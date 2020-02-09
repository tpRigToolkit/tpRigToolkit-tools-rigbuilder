#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains rig outliner widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

import string

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpQtLib.core import qtutils
from tpPyUtils import osplatform, fileio, path as path_utils, name as name_utils

from tpRigToolkit.core import resource

from tpRigToolkit.tools.rigbuilder.objects import helpers, rig
from tpRigToolkit.tools.rigbuilder.widgets import basetree


class RigItem(basetree.BaseItem, object):
    def __init__(self, directory, name, library, parent_item=None):

        self._directory = directory
        self._library = library
        self._name = name

        self._rig = None
        self._detail = False
        self._folder = False

        super(RigItem, self).__init__(parent=parent_item)

        split_name = name.split('/')
        self.setText(0, split_name[-1])
        self.setSizeHint(0, QSize(50, 20))

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def text(self, column):
        """
        Overrides base QTreeWidgetItem text function
        Used to cleanup text spaces
        :param column: int
        :return: str
        """

        text = super(RigItem, self).text(column)
        text = text.strip()
        return text

    def setText(self, column, text):
        """
        Overrides base QTreeWidgetItem setText function
        We add custom space text
        :param column: int
        :param text: str
        """

        text = '   ' + text
        super(RigItem, self).setText(column, text)

    def setData(self, column, role, value):
        """
        Overrides base QTreeWidgetItem setData function
        :param column: int
        :param role: QRole
        :param value: variant
        """

        super(RigItem, self).setData(column, role, value)

        rig = self._get_rig()
        if not rig:
            return

    def create(self):
        """
        Implements BaseItem create function
        Creates the rig of this item
        """

        if self.is_folder():
            return

        rig_inst = self._get_rig()
        if rig_inst.is_rig():
            return

        rig_inst.create()

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def get_name(self):
        """
        Returns the name of the rig
        :return: str
        """

        rig_inst = self._get_rig()
        return rig_inst.get_name()

    def set_name(self, name):
        """
        Set the name of the rig item
        :param name: str
        """

        self._name = name

    def get_path(self):
        """
        Returns the full path to the rig folder
        If the rig has not been create d yet, the rig directory will be return
        :return: str
        """

        rig_inst = self._get_rig()
        return rig_inst.get_path()

    def library(self):
        """
        Returns library linked to this item
        :return: Library
        """

        return self._library

    def set_library(self, library):
        """
        Sets library linked to this item
        :param library: Library
        """

        self._library = library

    def is_folder(self):
        """
        Returns whether the task is a folder or not
        :return: bool
        """

        return self._folder

    def get_directory(self):
        """
        Returns the directory of the task item
        :return: str
        """

        return self._directory

    def set_directory(self, directory):
        """
        Sets the directory of the task item
        :param directory: str
        """

        self._directory = directory

    def set_folder(self, flag):
        """
        Sets whether the rig is a folder or not
        :param flag: bool
        """

        self._folder = flag
        self.setDisabled(flag)

    def get_rig(self):
        """
        Returns the rig of the item
        :return: Rig
        """

        return self._get_rig()

    def get_parent_rig(self):
        """
        Returns the parent rig of the item
        :return: variant, Rig or None
        """

        return self._get_parent_rig()

    def rename(self, name):
        """
        Renames the rig item
        :param name: str, new name of the rig
        :return: bool, Whether the operation was successful or not
        """

        rig_inst = self._get_rig()
        state = rig_inst.rename(name)
        if state:
            self._name = name

        return state

    def has_parts(self):
        """
        Returns whether the current item has sub rigs or not
        :return: bool
        """

        rig_path = path_utils.join_path(self._directory, self._name)
        rigs, folders = helpers.RigHelpers.find_rigs(rig_path, return_also_non_objects_list=True)
        if rigs or folders:
            return True

        return False

    def matches(self, item):
        """
        Returns whether the given item is similar to the current one
        :param item: RigItem
        """

        if not item:
            return False
        if not hasattr(item, 'name'):
            return False
        if not hasattr(item, 'directory'):
            return False
        if item.name == self._name and item.get_directory() == self._directory:
            return True

        return False

    # ================================================================================================
    # ======================== INTERNAL
    # ================================================================================================

    def _add_rig(self, directory, name, library):
        """
        Internal function that links a new Rig to this item
        :param directory: str, directory of the rig
        :param name: str, name of the rig
        """

        self._rig = rig.RigObject(name=name)
        self._rig.set_directory(directory)
        self._rig.set_library(library)

        self._rig.create()

    def _get_rig(self):
        """
        Internal function that returns the rig of the item
        :return: Rig
        """

        rig_inst = rig.RigObject(name=self._name)
        rig_inst.set_directory(self._directory)
        rig_inst.set_library(self.library())

        return rig_inst

    def _get_parent_rig(self):
        """
        Internal function that returns, if exists, the parent rig of the current rig
        :return: variant, Rig or None
        """

        rig_inst = rig.RigObject(name=self._name)
        parent_rig = rig_inst.get_parent_rig()

        return parent_rig


class RigOutlinerTree(basetree.BaseTree, object):

    HEADER_LABELS = ['name']

    ICON_ON = resource.ResourceManager().icon('box_plus')
    ICON_OFF = resource.ResourceManager().icon('box_minus_alt')
    ICON_FOLDER = resource.ResourceManager().icon('folder')
    ICON_FOLDER_OPEN = resource.ResourceManager().icon('open_folder')

    newRig = Signal(object)
    newTopRig = Signal(object)
    copyRig = Signal()
    pasteRig = Signal(object)
    copySpecialRig = Signal(object)
    rigDeleted = Signal()
    rigRenamed = Signal(object)
    rigDuplicated = Signal(object, object)

    def __init__(self, checkable=True, settings=None, parent=None):
        self._settings = settings
        self._console = None
        self._checkable = checkable
        self._disable_modifiers = True
        self._shift_activate = False
        self._disable_right_click = False
        self._handle_selection_change = True
        self._paste_item = None
        self._dragged_item = None
        self._drag_parent = None
        self._current_folder = None
        self._text_edit = False
        self._context_menu = None

        super(RigOutlinerTree, self).__init__(parent=parent)

        self.setVerticalScrollMode(self.ScrollPerPixel)
        self.setDragDropMode(self.InternalMove)
        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDropIndicatorShown(True)
        self.setTabKeyNavigation(True)
        self.setHeaderHidden(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.setSelectionBehavior(self.SelectItems)
        self.setSelectionMode(self.SingleSelection)
        self.setAlternatingRowColors(True)

        self._create_context_menu()
        self._update_style()

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def drawBranches(self, painter, rect, index):
        """
        Overrides base treewidgets.FileTreeWidget dra
        wBranches function
        Draw custom icons for tree items
        :param painter: QPainter
        :param rect: QRect
        :param index: QModelIndex
        """

        item = self.itemFromIndex(index)
        if item.childCount() <= 0:
            self.ICON_FOLDER.paint(painter, rect)
        else:
            if item.isExpanded():
                self.ICON_FOLDER_OPEN.paint(painter, rect)
            else:
                self.ICON_FOLDER.paint(painter, rect)

    def keyPressEvent(self, event):
        """
        Overrides base treewidgets.FileTreeWidget keyPressEvent function
        :param event: QKeyEvent
        """

        if event.key() == Qt.Key_Shift:
            self._shift_activate = True

    def keyReleaseEvent(self, event):
        """
        Overrides base treewidgets.FileTreeWidget keyReleaseEvent function
        :param event: QKeyEvent
        """

        if event.key() == Qt.Key_Shift:
            self._shift_activate = False

    def mouseMoveEvent(self, event):
        """
        Overrides base treewidgets.FileTreeWidget mouseMoveEvent function
        :param event: QMouseEvent
        """

        model_index = self.indexAt(event.pos())
        item = self.itemAt(event.pos())
        if not item or model_index.column() == 1:
            self.clearSelection()
            self.setCurrentItem(self.invisibleRootItem())

        if event.button() == Qt.RightButton:
            return

        if model_index.column() == 0 and item:
            super(RigOutlinerTree, self).mouseMoveEvent(event)

    def mousePressEvent(self, event):
        """
        Overrides base treewidgets.FileTreeWidget mousePressEvent function
        :param event: QMouseEvent
        """

        item = self.itemAt(event.pos())
        if self._disable_modifiers:
            modifiers = QApplication.keyboardModifiers()
            if modifiers == Qt.ControlModifier:
                return
            if modifiers == (Qt.ControlModifier | Qt.ShiftModifier):
                return

        parent = self.invisibleRootItem()
        if item:
            if item.is_folder():
                self.setCurrentItem(self.invisibleRootItem())
                return
            if item.parent():
                parent = item.parent()
        else:
            self.setCurrentItem(self.invisibleRootItem())
            return

        self._drag_parent = parent
        self._dragged_item = item

        super(RigOutlinerTree, self).mousePressEvent(event)

    def dropEvent(self, event):
        """
        Overrides base treewidgets.FileTreeWidget dropEvent function
        :param event: QMouseEvent
        """

        directory = self._directory
        position = event.pos()
        index = self.indexAt(position)

        entered_item = self.itemAt(position)
        entered_name = None
        if entered_item:
            directory = entered_item._directory
            entered_name = entered_item.get_name()
        else:
            entered_item = self.invisibleRootItem()
            entered_name = None

        is_dropped = self._is_item_dropped(event)

        super(RigOutlinerTree, self).dropEvent(event)

        if not is_dropped:
            if entered_item:
                if entered_item.parent():
                    parent_item = entered_item.parent()
                else:
                    parent_item = self.invisibleRootItem()
                if not self._drag_parent is parent_item:
                    index = entered_item.indexOfChild(self._dragged_item)
                    child = entered_item.takeChild(index)
                    parent_item.addChild(child)
                    entered_item = parent_item
                    if parent_item in self.invisibleRootItem():
                        entered_name = None
                    else:
                        entered_name = entered_item.get_name()

        if entered_item:
            entered_item.setExpanded(True)
            entered_item.addChild(self._dragged_item)

        self._dragged_item.setDisabled(True)
        if entered_item is self._drag_parent:
            self._dragged_item.setDisabled(False)
            return

        old_directory = self._dragged_item._directory
        old_name_full = self._dragged_item.get_name()
        old_name = path_utils.get_basename(old_name_full)
        test_name = self._unique_name(self._dragged_item, old_name)
        self._dragged_item.setText(0, test_name)

        if self._checkable:
            flags = Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled | Qt.ItemIsUserCheckable
        else:
            flags = self._dragged_item.setFlags(Qt.ItemIsDragEnabled | Qt.ItemIsSelectable | Qt.ItemIsDropEnabled)

        if entered_name:
            self._dragged_item.setFlags(flags)
            if self._checkable:
                self._dragged_item.setCheckState(0, Qt.Unchecked)
            msg = 'Parent {} under {}?'.format(old_name, entered_name)
        else:
            if self._checkable:
                self._dragged_item.setData(0, Qt.CheckStateRole, None)
            self._dragged_item.setFlags(flags)
            self._dragged_item.setDisabled(True)
            msg = 'Unparent {}?'.format(old_name)

        move_result = qtutils.get_permission(message=msg, parent=self)
        if not move_result:
            entered_item.removeChild(self._dragged_item)
            if self._drag_parent:
                self._drag_parent.addChild(self._dragged_item)
            self._dragged_item.setDisabled(False)
            self._dragged_item.setText(0, old_name)
            self._dragged_item.setSelected(True)
            return

        self._dragged_item.setDisabled(False)
        old_path = self._dragged_item.get_path()
        self._dragged_item.set_directory(directory)
        new_name = self._dragged_item.text(0)
        self._dragged_item.setText(0, new_name)
        if entered_name:
            new_name = path_utils.join_path(entered_name, new_name)
        self._dragged_item.set_name(new_name)

        new_path = path_utils.join_path(directory, new_name)
        move_worked = fileio.move(old_path, new_path)
        if move_worked:
            self._dragged_item.setSelected(True)
        else:
            self._dragged_item.set_name(old_name_full)
            old_name = path_utils.get_basename(old_name_full)
            self._dragged_item.setText(0, old_name)
            self._dragged_item.set_directory(old_directory)

    def refresh(self):
        """
        Overrides base treewidgets.FileTreeWidget refresh function
        Look for rigs on the current project directory
        """

        rigs, folders = helpers.RigHelpers().find_rigs(directory=self._directory, return_also_non_objects_list=True)
        self._load_rigs(rigs, folders)

        self._current_item = None
        self._last_item = None

    def _create_context_menu(self):
        """
        Overrides base BaseTree _create_context_menu function
        Internal function that is used to initialize the contextual menu used by all tree items
        """

        self._context_menu = QMenu()

        add_icon = resource.ResourceManager().icon('add')
        rename_icon = resource.ResourceManager().icon('rename')
        duplicate_icon = resource.ResourceManager().icon('clone')
        copy_icon = resource.ResourceManager().icon('copy')
        paste_icon = resource.ResourceManager().icon('paste')
        merge_icon = resource.ResourceManager().icon('merge')
        delete_icon = resource.ResourceManager().icon('delete')
        browse_icon = resource.ResourceManager().icon('open')
        refresh_icon = resource.ResourceManager().icon('refresh')

        self._new_rig_action = self._context_menu.addAction(add_icon, 'New Rig')
        self._new_top_level_rig_action = self._context_menu.addAction(add_icon, 'New Top Level Rig')
        self._context_menu.addSeparator()
        self._convert_folder_action = self._context_menu.addAction('Convert Folder to Rig')
        self._context_menu.addSeparator()
        self._rename_action = self._context_menu.addAction(rename_icon, 'Rename')
        self._duplicate_action = self._context_menu.addAction(duplicate_icon, 'Duplicate')
        self._copy_action = self._context_menu.addAction(copy_icon, 'Copy')
        self._paste_action = self._context_menu.addAction(paste_icon, 'Paste')
        self._merge_action = self._context_menu.addAction(merge_icon, 'Merge')
        self._merge_with_sub_action = self._context_menu.addAction(merge_icon, 'Merge with Sub Folders')
        self._copy_special_action = self._context_menu.addAction(copy_icon, 'Copy Match')
        self._delete_action = self._context_menu.addAction(delete_icon, 'Delete')
        self._context_menu.addSeparator()
        self._context_menu.addSeparator()
        self._show_in_explorer_action = self._context_menu.addAction(browse_icon, 'Show in Explorer')
        self._refresh_action = self._context_menu.addAction(refresh_icon, 'Refresh')

        self._convert_folder_action.setVisible(False)
        self._paste_action.setVisible(False)
        self._merge_action.setVisible(False)
        self._merge_with_sub_action.setVisible(False)

        self._new_rig_action.triggered.connect(self._on_new_rig)
        self._new_top_level_rig_action.triggered.connect(self._on_new_top_rig)
        self._rename_action.triggered.connect(self._on_rename_rig)
        self._duplicate_action.triggered.connect(self._on_duplicate_rig)
        self._copy_action.triggered.connect(self._on_copy_rig)
        self._paste_action.triggered.connect(self._on_paste_rig)
        self._merge_action.triggered.connect(self._on_merge_rig)
        self._delete_action.triggered.connect(self._on_delete_rig)
        self._show_in_explorer_action.triggered.connect(self._on_show_in_explorer)

    def _add_sub_items(self, tree_item):
        """
        Overrides base treewidgets.FileTreeWidget _add_sub_items function
        :param tree_item: QTreeWidgetItem
        """

        self.delete_tree_item_children(tree_item)
        rig_path = ''
        if hasattr(tree_item, 'get_name'):
            rig_name = tree_item.get_name()
            rig_path = path.join_path(self._directory, rig_name)

        self._add_rig_items(tree_item, rig_path)

    def _item_rename_valid(self, old_name, item):
        """
        Overrides base treewidgets.FileTreeWidget _item_rename_valid function
        Internal function used to check if the rename operation is valid or not
        :param old_name: str, old name of the item
        :param item: QTreeWidgetItem
        :return: bool, Whether the rename operation was successful or not
        """

        state = super(RigOutlinerTree, self)._item_rename_valid(old_name, item)
        if not state:
            return False

        parent_name = self._get_parent_path(item)
        parent_path = path_utils.join_path(self._directory, parent_name)
        if path_utils.is_dir(parent_path):
            return False

        return True

    def _item_renamed(self, item):
        """
        Overrides base treewidgets.FileTreeWidget _item_renamed function
        Internal function that is called after a rig is renamed
        :param item: QTreeWidgetItem
        :return: bool, Whether the rename operation is right or not
        """

        item_path = self.get_tree_item_path_string(item)
        state = item.rename(item_path)
        if state:
            item.setExpanded(False)

        return state

    def _on_item_expanded(self, item):
        """
        Overrides base treewidgets.FileTreeWidget _on_item_expanded function
        If the user expands an item with SHIFT pressed all hierarchy will expand
        :param item: QTreeWidgetItem
        """

        if self._shift_activate:
            child_count = item.childCount()
            for i in range(child_count):
                children = self._get_ancestors(item.child(i))
                item.child(i).setExpanded(True)
                for child in children:
                    child.setExpanded(True)

    def _on_item_collapsed(self, item):
        """
        Overrides base treewidgets.FileTreeWidget _on_item_collapsed function
        :param item: QTreeWidgetItem
        """

        items = self.selectedItems()
        current_item = None
        if items:
            current_item = items[0]
        if self._has_item_parent(current_item, item):
            self.setCurrentItem(item)
            self.setItemSelected(item, True)

    def _on_item_menu(self, pos):
        """
        Overrides base BaseTree _on_item_menu function
        Internal callback function that shows the context menu of the selected item
        :param pos: QPoint
        """

        if self._disable_right_click:
            return

        self._current_folder = None
        self._set_item_menu_vis(pos)

        self._context_menu.exec_(self.viewport().mapToGlobal(pos))

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def set_directory(self, directory, refresh=True, sub_path=''):
        """
        Overrides base treewidgets.FileTreeWidget set_directory function
        :param directory: str
        :param refresh: bool
        :param sub_path: str
        """

        if sub_path:
            directory = path_utils.join_path(directory, sub_path)
        super(RigOutlinerTree, self).set_directory(directory, refresh=refresh)

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

    # ================================================================================================
    # ======================== RIG
    # ================================================================================================

    def add_rig(self, name):
        """
        Adds a new rig with the given name into the tree
        :param name: str, name of the new rig
        :return:
        """

        if not self._directory:
            self.get_console().write_warning(
                'RigTree >> add_rig >> Current directory is not valid: "{}"'.format(self._directory))
            return

        items = self.selectedItems()
        current_item = None
        if items:
            current_item = items[0]

        parent_item = None
        if not osplatform.get_permission(self._directory):
            self.get_console().write_warning(
                'RigTree > >> add rig >> Could not get permission in directory: "{}"'.format(self._directory))
            return

        if name == '':
            rig_path = self._directory
            if current_item:
                rig_path = self.get_tree_item_path_string(current_item)
                if rig_path:
                    rig_path = path_utils.join_path(self._directory, rig_path)
            if not osplatform.get_permission(rig_path):
                self.get_console().write_warning(
                    'RigTree >> add_rig >> Could not get permission in directory: "{}"'.format(rig_path))
                return
            name = helpers.RigHelpers.get_unused_rig_name(directory=rig_path)

        if name is None:
            name = helpers.RigHelpers.get_unused_rig_name(directory=self._directory)
            parent_item = self.invisibleRootItem()

        item = self._add_rig_item(name=name, parent_item=parent_item, create=True)

        self.setCurrentItem(item)
        self.setItemSelected(item, True)

        if not path_utils.is_dir(item.get_path()):
            self.remove_rig(item)
            self.get_console().write_warning(
                'RigTree >> add_rig >> Could not create rig: {}'.format(name))
            return
        else:
            self._on_rename_rig(item)

        self.newRig.emit(item)

        self.get_console().write_ok('RigTree >> add_rig >> New Rig created!')

    def rename_rig(self, item=None, new_name=None):
        """
        Renames new with new name. If not given name a UI to write new name pop ups
        :param item: variant, str or QTreeWidgetItem
        :param new_name: variant, str or None
        """

        if not item:
            items = self.selectedItems()
            if not items:
                return
            item = items[0]

        old_name = item.get_name()
        old_name = old_name.split('/')[-1]
        if not new_name:
            new_name = qtutils.get_string_input('', title='New Rig Name', old_name=old_name)
        if not new_name:
            return
        if new_name == old_name:
            self.get_console().write_warning(
                'RigTree >> rename_rig >> Rename process aborted because '
                'old and new names are the same!: "{}"'.format(new_name))
            return

        new_name = self._unique_name(item=item, new_name=new_name)
        item.setText(0, new_name)

        if not self._item_rename_valid(old_name=old_name, item=item):
            self.get_console().write_warning(
                'RigTree >> rename_rig >> Renaming process reverted because new name: {} is not valid!'.format(
                    new_name))
            item.setText(0, old_name)
            return

        valid_rename = self._item_renamed(item=item)
        if valid_rename:
            self.rigRenamed.emit(item)
            self.get_console().write_ok('RigTree >> rename_rig >> Rig {} renamed to {}'.format(old_name, new_name))
        else:
            self.get_console().write_warning(
                'RigTree >> rename_rig >> Renaming rig reverted because new name: {} is not valid!'.format(new_name))
            item.setText(0, old_name)

    def duplicate_rig(self, item=None):
        """
        Duplicates rig from the tree
        :param item: variant, str or QTreeWidgetItem
        """

        if not item:
            items = self.selectedItems()
            if not items:
                return
            item = items[0]

        source_rig = item.get_rig()
        target_rig = item.get_parent_rig()
        target_item = item.parent()
        if not target_rig:
            target_rig = rig.RigObject()
            target_rig.set_directory(self._directory)
            target_rig.set_library(self.library())
            target_item = self.invisibleRootItem()
        new_rig = helpers.RigHelpers().copy_rig(source_rig, target_rig)
        if not new_rig:
            return

        new_item = self._add_rig_item(name=new_rig.get_name(), parent_item=target_item)
        self.setCurrentItem(new_item)
        new_item.setSelected(True)
        self.scrollToItem(new_item)

        self.rigDuplicated.emit(item, new_item)
        self.get_console().write_ok(
            'RigTree >> duplicate_rig >> Rig {} duplicated! >>>>>> {}'.format(
                source_rig.get_path(), new_rig.get_path()))

    def copy_rig(self, item=None):
        """
        Copies rig from the tree
        :param item: variant, str or QTreeWidgetItem
        """

        if not item:
            items = self.selectedItems()
            if not items:
                return
            item = items[0]

        self._paste_item = item
        name = item.get_name()
        osplatform.set_env_var('RIGBUILDER_COPIED_RIG', item.get_path())
        self._paste_action.setText('Paste: {}'.format(name))
        self._merge_action.setText('Merge in: {}'.format(name))
        self._merge_with_sub_action.setText('Merge With Sub Folders: {}'.format(name))
        self._paste_action.setVisible(True)
        self._merge_action.setVisible(True)
        self._merge_with_sub_action.setVisible(True)

        self.copyRig.emit()
        self.get_console().write_ok('RigTree >> copy_rig >> Rig {} copied to clipboard!'.format(name))

    def paste_rig(self, source_item=None):
        """
        Paste rig
        :param item: variant, str or QTreeWidgetItem
        """

        if not source_item:
            copied = osplatform.get_env_var('RIGBUILDER_COPIED_RIG')
            if copied:
                source_rig = rig.RigObject()
                source_rig.set_directory(copied)
                source_rig.set_library(self.library())
            else:
                return

        target_rig = None
        items = self.selectedItems()
        if items:
            target_item = items[0]
            target_rig = target_item.get_rig()
        else:
            target_item = None
        if not target_rig:
            target_rig = rig.RigObject()
            target_rig.set_directory(self._directory)
            target_rig.set_library(self.library())
            target_item = None

        new_rig = helpers.RigHelpers.copy_rig(source_rig, target_rig)
        if not new_rig:
            return

        new_item = self._add_rig_item(new_rig.get_name(), target_item)

        self.clearSelection()
        self.setCurrentItem(self.invisibleRootItem())
        new_item.setSelected(True)
        self.scrollToItem(new_item)

        self.pasteRig.emit(new_item)
        self.get_console().write_ok('RigTree >> paste_rig >> Rig {} pasted from clipboard!'.format(new_item.get_name()))

    def merge_rig(self, source_rig=None, sub_rig_merge=False):
        """
        Merges source rig contents
        :param source_rig:
        :param sub_rig_merge: bool
        """

        self._paste_action.setVisible(False)
        if not source_rig:
            if not self._paste_item:
                return
            source_rig = self._paste_item.get_rig()

        source_rig_name = source_rig.get_name()
        merge_permission = qtutils.get_permission('Are you sure you want to merge in {}?'.format(source_rig_name))
        if not merge_permission:
            return

        target_rig = None
        target_item = None
        items = self.selectedItems()
        if items:
            target_item = items[0]
            target_rig = target_item.get_rig()

        if not target_rig:
            return

        helpers.RigHelpers.copy_rig_into(source_rig, target_rig, merge_sub_folders=sub_rig_merge)

        if target_item:
            target_item.setExpanded(False)
            if target_rig.get_sub_rigs():
                temp_item = QTreeWidgetItem()
                target_item.addChild(temp_item)

        self.copyRig.emit()

    def remove_rig(self, item=None):
        """
        Removes rig from the tree
        :param item: variant, str or QTreeWidgetItem
        """

        if not item:
            items = self.selectedItems()
            if not items:
                return
            item = items[0]

        parent_path = self._get_parent_path(item)
        delete_permission = qtutils.get_permission('Are you sure you want to delete {}?'.format(parent_path),
                                                   parent=self)
        if not delete_permission:
            return

        rig_inst = rig.RigObject(name=parent_path)
        rig_inst.set_directory(self._directory)
        rig_inst.set_library(self.library())
        rig_inst.delete()

        item_name = item.get_name()
        parent_item = item.parent()
        if parent_item:
            parent_item.removeChild(item)
        else:
            index = self.indexOfTopLevelItem(item)
            self.takeTopLevelItem(index)
            self.clearSelection()
            self.setCurrentItem(self.invisibleRootItem())

        self.rigDeleted.emit()
        self.get_console().write_ok('RigTree >> delete_rig >> Rig deleted: {} !'.format(item_name))

    # ================================================================================================
    # ======================== INTERNAL
    # ================================================================================================

    def _unique_name(self, item, new_name):
        """
        Internal function used to get a unique name for an item of the tree
        :param item: QTreeWidgetItem
        :param new_name: str, new name of the item
        :return: str, unique name for the item based on the given name
        """

        parent = item.parent()
        if not parent:
            parent = self.invisibleRootItem()

        sibling_count = parent.childCount()
        name_index = 1
        found_one = False
        for i in range(sibling_count):
            child_item = parent.child(i)
            if child_item.text(0) == new_name:
                if not found_one:
                    found_one = True
                    continue
                new_name = name_utils.increment_last_number(new_name)
                name_index += 1

        return new_name

    def _update_style(self):
        """
        Internal function that updates the style of the tree item
        """

        pass

    def _set_item_menu_vis(self, pos):
        item = self.itemAt(pos)
        if not item:
            self.clearSelection()
            self.setCurrentItem(self.invisibleRootItem())

        if item:
            if item.is_folder():
                if self.edit_state:
                    self._new_rig_action.setVisible(True)
                    # self._top
            else:
                pass
        else:
            pass

    def _add_rig_item(self, name, parent_item=None, create=False, find_parent_path=True, folder=False):
        """
        Internal function used to add rig tasks into the tree
        :param name:
        :param parent_item:
        :param create:
        :param find_parent_path:
        :param folder:
        :return:
        """

        expand_to = False
        items = self.selectedItems()
        current_item = None
        if items:
            current_item = items[0]

        if not parent_item and current_item:
            parent_item = current_item
            expand_to = True

        if find_parent_path and parent_item:
            item_path = self.get_tree_item_path_string(parent_item)
            if item_path:
                name = string.join([item_path, name], '/')
                if self._child_exists(name, parent_item):
                    return
            else:
                parent_item = None

        item = RigItem(directory=self._directory, name=name, library=self.library())

        if not folder:
            rig_inst = rig.RigObject(name=name)
            rig_inst.set_directory(self._directory)
            rig_inst.set_library(self.library())
        else:
            rig_inst = None
            item.set_folder(True)

        if create:
            item.create()

        if parent_item and not folder:
            enable = rig_inst.get_setting('enable')
            if not enable and self._checkable:
                item.setCheckState(0, Qt.Unchecked)
            if enable and self._checkable:
                item.setCheckState(0, Qt.Checked)

        if parent_item:
            if expand_to:
                self._auto_add_sub_items = False
                self.expandItem(parent_item)
                self._auto_add_sub_items = True
            parent_item.addChild(item)
        else:
            self.addTopLevelItem(item)

        if item.has_parts() and not folder:
            QTreeWidgetItem(item)

        return item

    def _add_rig_items(self, item, rig_path):
        """
        Internal function that is used to add a new script item into the tree hierarchy of the given item
        :param item: QTreeWidgetItem
        :param rig_path: str
        """

        parts, folders = helpers.find_rigs(rig_path, return_also_non_rig_list=True)
        sub_path = path_utils.remove_common_path(self._directory, rig_path)
        self.setUpdatesEnabled(False)
        try:
            for part in parts:
                if sub_path:
                    part = path_utils.join_path(sub_path, part)
                    self._add_rig_item(part, item, find_parent_path=False)
                else:
                    self._add_rig_item(part, item)
            for f in folders:
                if sub_path:
                    self._add_rig_item(f, item, create=True, find_parent_path=False, folder=True)
                else:
                    self._add_rig_item(f, item, create=True, folder=True)
        finally:
            self.setUpdatesEnabled(True)

    def _get_parent_path(self, tree_item):
        """
        Internal function that returns the path of the QTreeWidget's parent
        :param tree_item: QTreeWidgetItem
        :return: str
        """

        parents = self.get_tree_item_path(tree_item)
        parent_names = self.get_tree_item_names(parents)
        if not parent_names:
            return tree_item

        names = list()
        for name in parent_names:
            names.append(name[0])

        names.reverse()

        names_path = string.join(names, '/')

        return names_path

    def _child_exists(self, child_name, tree_item):
        """
        Checks if given child name exists in the hierarchy of the given QTreeWidgetItem
        :param child_name: str
        :param tree_item: QTreeWidgetItem
        :return: bool
        """

        children = self.get_tree_item_children(tree_item)
        for child in children:
            if hasattr(child, 'get_name'):
                if child_name == child.get_name():
                    return True

        return False

    def _has_item_parent(self, child_item, parent_item):
        """
        Internal function that return if given child_item has given parent_item
        :param child_item: QTreeItemWidget
        :param parent_item: QTreeItemWidget
        :return: bool
        """

        if not child_item or not parent_item:
            return False

        parent = child_item.parent()
        if not parent:
            return False

        if parent_item.matches(parent):
            return True

        while parent:
            parent = parent.parent()
            if parent_item.matches(parent):
                return True

    def _load_rigs(self, rig_paths, folders=None):
        """
        Internal function that loads all given rigs paths and folders
        :param rig_paths: list(str)
        :param folders: variant, list(str) or None
        """

        if folders is None:
            folders = list()

        self.clear()
        for rig_path in rig_paths:
            self._add_rig_item(rig_path)
        for f in folders:
            self._add_rig_item(f, create=True, folder=True)

    # ================================================================================================
    # ======================== CALLBACKS
    # ================================================================================================

    def _on_new_rig(self):
        """
        Internal callback function that is called when the user clicks on the New Rig action
        Adds a new rig into the project and parented in the selected rig item
        """

        self.add_rig(name='')

    def _on_new_top_rig(self):
        """
        Internal callback function that is called when the user clicks on the New Top Level Rig action
        Adds a new rig into the project and parent it into the root project folder
        """

        self.add_rig(None)

    def _on_rename_rig(self, item=None):
        """
        Internal callback function that is called when the user renames a rig
        :param item: QTreeWidgetItem
        """

        self.rename_rig(item=item)

    def _on_duplicate_rig(self, item=None):
        """
        Internal callback function that is called when the user clicks on Duplicate Rig Action
        Duplicates selected rig
        :param item: QTreeWidgetItem
        """

        self.duplicate_rig(item=item)

    def _on_copy_rig(self, item=None):
        """
        Internal callback function that is called when the user clicks on Copy Rig Action
        Copy selected rig
        :param item: QTreeWidgetItem
        """

        self.copy_rig(item=item)

    def _on_paste_rig(self, source_item=None):
        """
        Internal callback function that is called when the user clicks on Paste Rig Action
        :param item: QTreeWidgetItem
        """

        self.paste_rig(source_item=source_item)

    def _on_merge_rig(self, source_item=None, sub_rig_merge=False):
        """
        Internal callback function that is called when the user clicks on Merge Rig Action
        """

        self.merge_rig(source_rig=source_item, sub_rig_merge=sub_rig_merge)

    def _on_delete_rig(self):
        """
        Internal callback function that is called when the user renames a rig
        :param item: QTreeWidgetItem
        """

        self.remove_rig()

    def _on_show_in_explorer(self):
        """
        Internal  callback function that is called when the user clicks on the Show In Explorer action
        Shows selected task contents in OS explorer
        """

        rig_path = self._directory
        if self._current_folder:
            parent_path = self._get_parent_path(self._current_folder)
            rig_path = path_utils.join_path(self._directory, parent_path)
        else:
            items = self.selectedItems()
            if items:
                rig_item = items[0].get_rig()
                rig_path = rig_item.get_path()

        if rig_path:
            fileio.open_browser(rig_path)
