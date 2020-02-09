#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains rig outliner widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpQtLib.core import qtutils
from tpQtLib.widgets import treewidgets


class RigOutlinerTree(treewidgets.FileTreeWidget, object):
    HEADER_LABELS = ['name']

    def __init__(self, checkable=True, settings=None, parent=None):
        self._library = None
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
        self._context_menu = QMenu()

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

        self.customContextMenuRequested.connect(self._on_item_menu)

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

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
        old_name = path.get_basename(old_name_full)
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
            new_name = path.join_path(entered_name, new_name)
        self._dragged_item.set_name(new_name)

        new_path = path.join_path(directory, new_name)
        move_worked = fileio.move(old_path, new_path)
        if move_worked:
            self._dragged_item.setSelected(True)
        else:
            self._dragged_item.set_name(old_name_full)
            old_name = path.get_basename(old_name_full)
            self._dragged_item.setText(0, old_name)
            self._dragged_item.set_directory(old_directory)

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

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

    def set_directory(self, directory, refresh=True, sub_path=''):
        """
        Overrides base treewidgets.FileTreeWidget set_directory function
        :param directory: str
        :param refresh: bool
        :param sub_path: str
        """

        if sub_path:
            directory = path.join_path(directory, sub_path)
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
    # ======================== INTERNAL
    # ================================================================================================

    def _create_context_menu(self):
        """
        Internal function that is used to initialize the contextual menu used by all tree items
        """

        pass

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

    # ================================================================================================
    # ======================== CALLBACKS
    # ================================================================================================

    def _on_item_menu(self, pos):
        """
        Internal callback function that shows the context menu of the selected item
        :param pos: QPoint
        """

        if self._disable_right_click:
            return

        self._current_folder = None

        self._set_item_menu_vis(pos)

        self._context_menu.exec_(self.viewport().mapToGlobal(pos))