#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget to show scripts tree
"""

from __future__ import print_function, division, absolute_import

import logging

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDccLib as tp
from tpQtLib.core import qtutils
from tpQtLib.widgets import treewidgets

from tpRigToolkit.core import resource

LOGGER = logging.getLogger('tpRigToolkit')


class ScriptObject(object):
    def __init__(self):
        super(ScriptObject, self).__init__()

    def sync_scripts(self):
        print('Syncing scripts ...')

    def get_code_folders(self):
        print('codef olders ....')
        return list()

    def get_code_file(self):
        print('getting code file ...')
        return None

    def move_code(self):
        print('moving code ...')
        return None

    def get_scripts_manifest(self):
        print('getting scripts manifest ...')
        return None, None

    def set_scripts_manifest(self, scripts, states):
        print('set scripts manifest: ', scripts, states)
        return None


class ScriptItem(treewidgets.TreeWidgetItem, object):

    ok_icon = resource.ResourceManager().icon('ok')
    warning_icon = resource.ResourceManager().icon('warning')
    error_icon = resource.ResourceManager().icon('error')
    wait_icon = resource.ResourceManager().icon('wait')

    def __init__(self, parent=None):
        self.handle_manifest = False
        super(ScriptItem, self).__init__(parent)

        self._run_state = -1
        self._log = ''

        self.setSizeHint(0, QSize(10, 20))
        self.setCheckState(0, Qt.Unchecked)

        if tp.is_maya():
            maya_version = tp.Dcc.get_version()
            if maya_version > 2015 or maya_version == 0:
                self._circle_fill_icon(0, 0, 0)
            if maya_version < 2016 and maya_version != 0:
                self._radial_fill_icon(0, 0, 0)

    def text(self, index):
        """
        Returns item text of given index
        :param index: QModelIndex
        :return: str
        """

        return self.get_text()

    def setText(self, index, text):
        """
        Overrides QTreeWidgetItem setText function
        Sets text of given item index
        :param index: QModelIndex
        :param text: str
        """

        return self.set_text(text)

    def setData(self, column, role, value):
        """
        Overrides base QTreeWidgetItem setData function
        :param column: int
        :param role: QRole
        :param value: variant
        """

        super(ScriptItem, self).setData(column, role, value)

        if value == 0:
            check_state = Qt.Unchecked
        elif value == 2:
            check_state = Qt.Checked

        if role == Qt.CheckStateRole:
            if self.handle_manifest:
                tree = self.treeWidget()
                tree.update_scripts_manifest()
                if tree._shift_activate:
                    child_count = self.childCount()
                    for i in range(child_count):
                        child = self.child(i)
                        child.setCheckedState(column, check_state)
                        children = tree._get_ancestors(child)
                        for child in children:
                            child.setCheckedState(column, check_state)

    def set_text(self, text):
        """
        Function used to set text of the item
        :param text: str
        """

        text = '   ' + text
        super(ScriptItem, self).setText(0, text)

    def get_text(self):
        """
        Function used to get the text of the item
        :return: str
        """

        text_value = super(ScriptItem, self).text(0)
        return str(text_value).strip()

    def log(self):
        """
        Returns current item log
        :return: str
        """

        return self._log

    def set_log(self, log):
        """
        Sets log of current item
        :param log: str
        """

        self._log = log

    def set_state(self, state):
        """
        Sets state of curren item
        :param state: int
        """

        if tp.is_maya():
            maya_version = tp.Dcc.get_version()
            if maya_version < 2016 and maya_version != 0:
                if state == 0:
                    self._error_icon()
                if state == 1:
                    self._ok_icon()
                if state == -1:
                    self._radial_fill_icon(0.6, 0.6, 0.6)
                if state == 2:
                    self._warning_icon()
                if state == 3:
                    self._radial_fill_icon(.65, .7, 0.225)
                if state == 4:
                    self._wait_icon()
            if maya_version > 2015 or maya_version == 0:
                if state == 0:
                    self._error_icon()
                if state == 1:
                    self._ok_icon()
                if state == -1:
                    self._circle_fill_icon(0, 0, 0)
                if state == 2:
                    self._warning_icon()
                    # self._circle_fill_icon(1.0, 1.0, 0.0)
                if state == 3:
                    self._circle_fill_icon(.65, .7, .225)
                if state == 4:
                    self._wait_icon()
        else:
            if state == 0:
                self._error_icon()
            if state == 1:
                self._ok_icon()
            if state == -1:
                self._radial_fill_icon(0.6, 0.6, 0.6)
            if state == 2:
                self._warning_icon()
            if state == 3:
                self._radial_fill_icon(.65, .7, 0.225)
            if state == 4:
                self._wait_icon()

        self._run_state = state

    def get_state(self):
        """
        Returns current item state
        :return: int
        """

        return self.checkState(0)

    def get_run_state(self):
        """
        Returns curren item run state
        :return: int
        """

        return self._run_state

    def _square_fill_icon(self, r, g, b):
        """
        Internal function used to draw square filled icon
        :param r: float
        :param g: float
        :param b: float
        """

        alpha = 1
        if r == 0 and g == 0 and b == 0:
            alpha = 0

        pixmap = QPixmap(20, 20)
        pixmap.fill(QColor.fromRgbF(r, g, b, alpha))
        painter = QPainter(pixmap)
        painter.fillRect(0, 0, 100, 100, QColor.fromRgbF(r, g, b, alpha))
        painter.end()

        icon = QIcon(pixmap)
        self.setIcon(0, icon)

    def _circle_fill_icon(self, r, g, b):
        """
        Internal function used to draw circle filled icon
        :param r: float
        :param g: float
        :param b: float
        """

        alpha = 1
        if r == 0 and g == 0 and b == 0:
            alpha = 0

        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        # pixmap.fill(qt.QColor.fromRgbF(r, g, b, alpha))

        painter = QPainter(pixmap)
        painter.setBrush(QColor.fromRgbF(r, g, b, alpha))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(0, 0, 20, 20)
        # painter.fillRect(0, 0, 100, 100, qt.QColor.fromRgbF(r, g, b, alpha))
        painter.end()

        icon = QIcon(pixmap)
        self.setIcon(0, icon)

    def _radial_fill_icon(self, r, g, b):
        """
        Internal function used to draw radial filled icon
        :param r: float
        :param g: float
        :param b: float
        """
        alpha = 1
        if r == 0 and g == 0 and b == 0:
            alpha = 0

        pixmap = QPixmap(20, 20)
        pixmap.fill(Qt.transparent)
        gradient = QRadialGradient(10, 10, 10)
        gradient.setColorAt(0, QColor.fromRgbF(r, g, b, alpha))
        gradient.setColorAt(1, QColor.fromRgbF(0, 0, 0, 0))

        painter = QPainter(pixmap)
        painter.fillRect(0, 0, 100, 100, gradient)
        painter.end()

        icon = QIcon(pixmap)

        self.setIcon(0, icon)

    def _ok_icon(self):
        """
        Internal callback function that sets ok icon into the item
        """

        self.setIcon(0, self.ok_icon)

    def _warning_icon(self):
        """
        Internal callback function that sets warning icon into the item
        """

        self.setIcon(0, self.warning_icon)

    def _error_icon(self):
        """
        Internal callback function that sets error icon into the item
        """

        self.setIcon(0, self.error_icon)

    def _wait_icon(self):
        """
        Internal callback function that sets wait icon into the item
        """

        self.setIcon(0, self.wait_icon)


class ScriptTree(treewidgets.FileTreeWidget, object):

    HEADER_LABELS = ['Scripts']
    ITEM_WIDGET = ScriptItem
    NEW_ITEM_NAME = 'new_rig'

    itemCreated = Signal(object)
    itemRenamed = Signal(object, object)
    itemRemoved = Signal(object)
    itemDuplicated = Signal()
    scriptOpened = Signal(object, bool, bool)
    scriptOpenedInExternal = Signal()
    scriptFocused = Signal()

    python_icon = resource.ResourceManager().icon('python')
    python_expand_icon = resource.ResourceManager().icon('python_expand')
    python_no_expand_icon = resource.ResourceManager().icon('python_no_expand')

    def __init__(self, settings=None, parent=None):
        super(ScriptTree, self).__init__(parent)

        self._object = None
        self._library = None
        self._settings = settings

        self._handle_selection_change = True
        self._allow_scripts_manifest_update = True
        self._update_checkbox = True
        self._shift_activate = False
        self._hierarchy = True
        self._dragged_item = None
        self._break_index = None
        self._start_index = None
        self._break_item = None
        self._start_item = None

        self._context_menu = None
        self._new_actions = list()
        self._edit_actions = list()

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
        # header.setStyleSheet('background-color:rgba(28, 28, 28, 255);')
        header.setDefaultAlignment(Qt.AlignCenter)
        self._checkbox = QCheckBox(header)
        self._checkbox.move(4, 4)

        self._checkbox.stateChanged.connect(self._on_set_all_checked)
        self.customContextMenuRequested.connect(self._on_item_menu)

        self._create_context_menu()

    def resizeEvent(self, event):
        """
        Overrides base treewidgets.FileTreeWidget resizeEvent function
        Places update all checkbox to proper position
        :param event: QResizeEvent
        :return:
        """

        super(ScriptTree, self).resizeEvent(event)
        self._checkbox.setGeometry(QRect(3, 2, 16, 17))

    def mousePressEvent(self, event):
        self._handle_selection_change = True
        item = self.itemAt(event.pos())
        parent = self.invisibleRootItem()
        if item:
            if item.parent():
                parent = item.parent()
        self._dragged_item = item
        super(ScriptTree, self).mousePressEvent(event)
        self.scriptFocused.emit()

    def mouseDoubleClickEvent(self, event):
        item = None
        items = self.selectedItems()
        if items:
            item = items[0]
        if not item:
            return

        settings = self.settings()
        if not settings:
            self.scriptOpened.emit(item, False, False)
            return

        settings.beginGroup('Code')
        double_click_option = settings.get('script_double_click')
        if double_click_option:
            if double_click_option == 'open_tab':
                self.scriptOpened.emit(item, False, False)
            elif double_click_option == 'open_new':
                self._on_open_in_window(item)
            elif double_click_option == 'open_external':
                self._on_open_in_external(item)
        else:
            self.scriptOpened.emit(item, False, False)
        settings.endGroup()

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

    def drawBranches(self, painter, rect, index):
        """
        Overrides base treewidgets.FileTreeWidget drawBranches function
        Draws custom icons for scripts tree items
        :param painter: QPainter
        :param rect: QRect
        :param index: QModelIndex
        """

        if index:
            item = self.itemFromIndex(index)
            item_text = item.get_text()
            if item_text.endswith('.py'):
                if item.childCount() <= 0:
                    self.python_icon.paint(painter, rect)
                else:
                    if item.isExpanded():
                        self.python_expand_icon.paint(painter, rect)
                    else:
                        self.python_no_expand_icon.paint(painter, rect)
            else:
                super(ScriptTree, self).drawBranches(painter, rect, index)
        else:
            super(ScriptTree, self).drawBranches(painter, rect, index)

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

        return self._settings

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
        Returns library linked to this widget
        :return: Library
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

    def get_current_scripts_manifest(self):
        """
        Returns the current script manifest of the script
        :return:
        """

        scripts = list()
        states = list()

        items = self._get_all_items()
        for item in items:
            item_name = item.get_text()
            item_path = self.get_item_path(item)
            if item_path:
                item_name = path.join_path(item_path, item_name)

            state = item.checkState(0)
            if state == 0:
                state = False
            elif state == 2:
                state = True

            scripts.append(item_name)
            states.append(state)

        return scripts, states

    def reset_script_state(self):
        """
        Resets the states of all current scripts
        """

        items = self._get_all_items()
        for item in items:
            item.set_state(-1)

    def set_script_state(self, directory, state):
        """
        Sets the state of script
        :param directory: str
        :param state: int
        """

        script_name = directory
        item = self._get_item_by_name(script_name)
        if not item:
            return
        if state > -1:
            self.scrollToItem(item)
        item.set_state(state)

    def set_script_log(self, directory, log):
        """
        Sets the script log of the script
        :param directory: str
        :param log: str
        """

        script_name = directory
        item = self._get_item_by_name(script_name)
        if not item:
            return
        item.set_log(log)

    def get_item_path(self, item):
        """
        Returns the path to an item from the top tree level to down
        :param item: QTreeWidgetItem
        :return: str
        """

        parent = item.parent()
        parent_path = ''

        while parent:
            parent_name = parent.text(0)
            parent_name = parent_name.split('.')[0]
            if parent_path:
                parent_path = path.join_path(parent_name, parent_path)
            else:
                parent_path = parent_name

            parent = parent.parent()

        return parent_path

    def update_scripts_manifest(self):
        """
        Forces the update (if allowed) of the scripts manifest
        """

        if not self._allow_scripts_manifest_update:
            return

        current_object = self.object()
        if not current_object:
            tpRigBuilder.logger.debug('Impossible to get object files because object is not defined!')
            return

        scripts, states = self.get_current_scripts_manifest()
        current_object.set_scripts_manifest(scripts, states)

    def has_start_point(self):
        """
        Returns whether start point is defined or not
        :return: bool
        """

        if self._start_index is not None:
            return True

        return False

    def is_script_break_point(self, directory):
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

    def is_script_start_point(self, directory):
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

    def _create_context_menu(self):
        """
        Internal function that creates context menu for script tree
        """

        self._context_menu = QMenu()
        
        python_icon = resource.ResourceManager().icon('python')
        import_icon = resource.ResourceManager().icon('import')
        play_icon = resource.ResourceManager().icon('play')
        rename_icon = resource.ResourceManager().icon('rename')
        duplicate_icon = resource.ResourceManager().icon('clone')
        delete_icon = resource.ResourceManager().icon('delete')
        refresh_icon = resource.ResourceManager().icon('refresh')
        log_icon = resource.ResourceManager().icon('document')
        new_window_icon = resource.ResourceManager().icon('new_window')
        external_icon = resource.ResourceManager().icon('external')
        browse_icon = resource.ResourceManager().icon('open')
        start_point_icon = resource.ResourceManager().icon('finish_flag')
        break_point_icon = resource.ResourceManager().icon('record')
        cancel_start_point_icon = resource.ResourceManager().icon('cancel_start_point')
        cancel_break_point_icon = resource.ResourceManager().icon('cancel_break_point')
        cancel_start_break_points_icon = resource.ResourceManager().icon('cancel_start_break_points')

        new_python_action = self._context_menu.addAction(python_icon, 'New Python Code')
        new_data_import_action = self._context_menu.addAction(import_icon, 'New Data Import')
        self._new_actions = [new_python_action, new_data_import_action]
        self._context_menu.addSeparator()
        self._run_action = self._context_menu.addAction(play_icon, 'Run')
        rename_action = self._context_menu.addAction(rename_icon, 'Rename')
        duplicate_action = self._context_menu.addAction(duplicate_icon, 'Duplicate')
        self._delete_action = self._context_menu.addAction(delete_icon, 'Delete')
        self._context_menu.addSeparator()
        log_window = self._context_menu.addAction(log_icon, 'Show Last Log')
        new_window_action = self._context_menu.addAction(new_window_icon, 'Open in New Window')
        external_window_action = self._context_menu.addAction(external_icon, 'Open in External')
        browse_action = self._context_menu.addAction(browse_icon, 'Browse')
        refresh_action = self._context_menu.addAction(refresh_icon, 'Refresh')
        self._context_menu.addSeparator()
        start_action = self._context_menu.addAction(start_point_icon, 'Set Start Point')
        self._cancel_start_action = self._context_menu.addAction(cancel_start_point_icon, 'Cancel Start Point')
        self._context_menu.addSeparator()
        break_action = self._context_menu.addAction(break_point_icon, 'Set Break Point')
        self._cancel_break_point = self._context_menu.addAction(cancel_break_point_icon, 'Cancel Break Point')
        self._context_menu.addSeparator()
        self._cancel_points_action = self._context_menu.addAction(cancel_start_break_points_icon,
                                                                  'Cancel Start/Break Points')
        self._edit_actions = [self._run_action, rename_action, duplicate_action, self._delete_action]

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
                Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsDragEnabled
                | Qt.ItemIsUserCheckable)

        # Used to avoid script manifest update when check states of ScriptManifestItem is changed programatically
        if hasattr(item, 'handle_manifest'):
            item.handle_manifest = True

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
            item_name = path.join_path(item_path, item_name)

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
            item_path = path.join_path(item_path, folder_name)
        else:
            item_path = folder_name
        item_name = path.join_path(item_path, item_name)

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
            LOGGER.debug('Impossible to sync scripts because rig is not defined!')
            return

        current_object.sync_scripts()

    def _edit_actions_visible(self, flag):
        """
        Internal function used to show/hide actions that are related with script edition
        :param flag: bool
        """

        for action in self._edit_actions:
            action.setVisible(flag)

    def _get_files(self, scripts=None, states=None):
        """
        Internal function that returns all scripts and its states located in the current scripts tree directory
        :param scripts: list(str)
        :param states: list(str)
        :return: list(list, list)
        """

        if scripts is None:
            scripts = list()
        if states is None:
            states = list()

        current_object = self.object()
        if not current_object:
            LOGGER.debug('Impossible to get script files because scripts object is not defined!')
            return

        if not scripts:
            scripts, states = current_object.get_scripts_manifest()
        if not scripts:
            LOGGER.debug('Current object has no scripts!')
            return

        code_folders = current_object.get_code_folders()
        found_scripts = list()
        found_states = list()
        parents = dict()

        for i in range(len(scripts)):
            script_name = fileio.remove_extension(scripts[i])
            if not script_name in code_folders:
                continue
            script_path = current_object.get_code_file(script_name)
            if not script_path or not path.is_file(script_path):
                continue

            if script_name.count('/') > 0:
                dir_name = path.get_dirname(script_name)
                parents[dir_name] = scripts[i]

            found_scripts.append(scripts[i])
            found_states.append(states[i])

        return [found_scripts, found_states, parents]

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

    def _add_item(self, file_name, state, parent=None, update_manifest=True):
        """
        Internal function that adds a new item to the script tree
        :param file_name: str
        :param state: int
        :param parent: ScriptItem
        :param update_manifest: bool
        :return: ScriptItem
        """

        if file_name.count('/') > 0:
            basename = path.get_basename(file_name)
            item = super(ScriptTree, self)._add_item(basename, parent=False)
        elif file_name.count('/') == 0:
            item = super(ScriptTree, self)._add_item(file_name, parent=parent)

        self._setup_item(item, state)

        if update_manifest:
            self.update_scripts_manifest()

        return item

    def _add_items(self, files, item=None):
        """
        Internal function used to add new scripts file to the given script item
        :param files: list(str)
        :param item: ScriptItem
        """

        scripts, states, parents = files
        script_count = len(scripts)
        found_false = False
        built_parents = dict()

        for i in range(script_count):
            script_name = scripts[i].split('.')[0]
            basename = path.get_basename(scripts[i])
            dir_name = path.get_dirname(scripts[i])
            current_parent = None
            if dir_name in parents and dir_name in built_parents:
                current_parent = built_parents[dir_name]
            item = self._add_item('...temp...', states[i], parent=current_parent, update_manifest=False)
            if script_name in parents:
                built_parents[script_name] = item
            if dir_name in parents and dir_name in built_parents:
                item.set_text(basename)
            if not dir_name:
                self.addTopLevelItem(item)
                item.set_text(basename)

            if not states[i]:
                found_false = True

        orig_update_checkbox = self._update_checkbox
        self._update_checkbox = False
        if found_false:
            self._checkbox.setChecked(False)
        else:
            self._checkbox.setChecked(True)
        self._update_checkbox = orig_update_checkbox

    def _handle_item_reparent(self, old_name, new_name):
        """
        Internal function that handles the parenting of script tree script items
        :param old_name: str
        :param new_name: str
        :return: str
        """

        if old_name == new_name:
            return old_name

        current_object = self.object()
        if not current_object:
            tpRigBuilder.logger.warning('Impossible to handle item reparent because object is not defined!')
            return

        new_name = current_object.move_code(old_name, new_name)

        return new_name

    def _activate_rename(self):
        """
        Function that allows the user to type a new name script name
        """

        current_library = self.library()
        if not current_library:
            tpRigBuilder.logger.warning('Impossible to rename current item because data library is not defined!')
            return

        items = self.selectedItems()
        if not items:
            return
        item = items[0]

        self._old_name = str(item.get_text())
        new_name = tpRigBuilder.show_rename_dialog('Rename item', 'Rename the current item to:', self._old_name)
        if new_name == self._old_name:
            return True
        if not new_name:
            return

        if new_name == 'manifest' or new_name == 'manifest.py':
            qtutils.warning_message('Manifest name is reserved. Name your script something else', parent=self)
            return

        self._rename_item(item, new_name)

        return True

    def _name_clash(self, name):
        """
        Internal function that checks if a name is not already defined in current directory files and folders
        :param name: str
        :return: bool
        """

        current_object = self.object()
        if not current_object:
            tpRigBuilder.logger.warning('Impossible to check clash code folder name because object is not defined!')
            return

        code_folders = current_object.get_code_folders()
        for f in code_folders:
            other_name = f
            if name == other_name:
                return True

        return False

    def _on_item_menu(self, pos):
        """
        Internal function that is called when the user right clicks an item of the tree and shows the contextual
        menu for that item
        :param pos: QPos
        """

        items = self.selectedItems()
        item = None
        if items:
            item = items[0]
        if item:
            self._edit_actions_visible(True)
        else:
            self._edit_actions_visible(False)

        if len(items) > 1:
            self._edit_actions_visible(False)
            self._run_action.setVisible(True)
            self._delete_action.setVisible(True)

        self._context_menu.exec_(self.viewport().mapToGlobal(pos))

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

