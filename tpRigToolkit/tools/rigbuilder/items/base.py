#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base tree item implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDcc as tp
from tpDcc.libs.python import decorators, fileio, path as path_utils
from tpDcc.libs.qt.widgets import treewidgets


class BaseItem(treewidgets.TreeWidgetItem, object):
    def __init__(self, parent=None):

        self._log = ''
        self._object = None
        self._run_state = -1
        self._context_menu = None
        self._handle_manifest = False

        self.ok_icon = tp.ResourcesMgr().icon('ok')
        self.warning_icon = tp.ResourcesMgr().icon('warning')
        self.error_icon = tp.ResourcesMgr().icon('error')
        self.wait_icon = tp.ResourcesMgr().icon('wait')

        super(BaseItem, self).__init__(parent)

        self.setSizeHint(0, QSize(10, 20))
        self.setCheckState(0, Qt.Unchecked)

        if tp.is_maya():
            maya_version = tp.Dcc.get_version()
            if maya_version > 2015 or maya_version == 0:
                self._circle_fill_icon(0, 0, 0)
            if maya_version < 2016 and maya_version != 0:
                self._radial_fill_icon(0, 0, 0)

        self._create_context_menu()

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    @property
    def handle_manifest(self):
        return self._handle_manifest

    @handle_manifest.setter
    def handle_manifest(self, flag):
        self._handle_manifest = flag

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def text(self, index):
        """
        Returns item text of given index
        :param index: QModelIndex
        :return: str
        """

        return self.get_text()

    # def setText(self, index, text):
    #     """
    #     Overrides QTreeWidgetItem setText function
    #     Sets text of given item index
    #     :param index: QModelIndex
    #     :param text: str
    #     """
    #
    #     return self.set_text(text)

    def setData(self, column, role, value):
        """
        Overrides base QTreeWidgetItem setData function
        :param column: int
        :param role: QRole
        :param value: variant
        """

        super(BaseItem, self).setData(column, role, value)

        if value == 0 or value is False:
            check_state = Qt.Unchecked
        elif value == 2 or value is True:
            check_state = Qt.Checked

        if role == Qt.CheckStateRole:
            if self._handle_manifest:
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

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    @decorators.abstractmethod
    def create(self):
        """
        Function that creates data for current item
        Implements in specific classe
        """

        raise NotImplementedError('function create not implememted for "{}"!'.format(self.__class__.__name__))

    def get_text(self):
        """
        Function used to get the text of the item
        :return: str
        """

        text_value = super(BaseItem, self).text(0)
        return str(text_value).strip()

    def set_text(self, text):
        """
        Function used to set text of the item
        :param text: str
        """

        text = '   ' + text
        super(BaseItem, self).setText(0, text)

    def get_name(self, keep_extension=False):
        """
        Returns item name
        :param keep_extension: bool, Whether to return the path to the file with the file extension or not
        :return: str
        """

        item_name = self.text(0)
        if not keep_extension:
            item_name = fileio.remove_extension(item_name)

        item_path = self.get_path()
        if item_path:
            item_name = path_utils.join_path(item_path, item_name)

        return item_name

    def get_path(self):
        """
        Returns the path to an item from the top tree level to down
        :return: str
        """

        parent = self.parent()
        parent_path = ''

        while parent:
            parent_name = parent.text(0)
            parent_name = parent_name.split('.')[0]
            if parent_path:
                parent_path = path_utils.join_path(parent_name, parent_path)
            if not parent_path:
                parent_path = parent_name

            parent = parent.parent()

        return parent_path

    def get_object(self):
        """
        Returns object this item is linked to
        :return: object
        """

        return self._object

    def set_object(self, object):
        """
        Sets the object this item is linked to
        :param object: object
        """

        self._object = object

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

    def get_state(self):
        """
        Returns current item state
        :return: int
        """

        return self.checkState(0)

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

    def get_run_state(self):
        """
        Returns curren item run state
        :return: int
        """

        return self._run_state

    def get_context_menu(self):
        """
        Returns context menu of the item
        :return: QMenu
        """

        return self._context_menu

    def matches(self, item):
        """
        Returns whether the given item is similar to the current one
        :param item: RigItem
        """

        if not item:
            return False
        if not hasattr(item, 'get_name') or not hasattr(self, 'get_path'):
            return False
        if item.get_name() == self.get_name() and item.get_path() == self.get_path():
            return True

        return False

    # ================================================================================================
    # ======================== INTERNAL
    # ================================================================================================

    def _create_context_menu(self):
        """
        Creates context menu for this item
        """

        self._context_menu = QMenu()

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
