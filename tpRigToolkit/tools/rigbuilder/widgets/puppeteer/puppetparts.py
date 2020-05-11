#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains puppeteer parts widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc
from tpDcc.libs.qt.core import base


class PuppetPartsWidget(base.BaseWidget, object):
    def __init__(self, parent=None):

        self._puppet = None
        self._current_module = None
        self._current_module_name = None

        super(PuppetPartsWidget, self).__init__(parent=parent)

    @property
    def current_module(self):
        return self._current_module

    @property
    def current_module_name(self):
        return self._current_module_name

    @property
    def puppet(self):
        return self._puppet

    @puppet.setter
    def puppet(self, value):
        if value != self._puppet:
            self._puppet = value

    def ui(self):
        super(PuppetPartsWidget, self).ui()

        splitter = QSplitter()
        self.main_layout.addWidget(splitter)

        tree_widget = QWidget()
        tree_layout = QVBoxLayout()
        tree_layout.setContentsMargins(0, 0, 0, 0)
        tree_layout.setSpacing(0)
        tree_widget.setLayout(tree_layout)
        options_widget = QWidget()
        options_layout = QVBoxLayout()
        options_layout.setContentsMargins(0, 0, 0, 0)
        options_layout.setSpacing(0)
        options_widget.setLayout(options_layout)
        splitter.addWidget(tree_widget)
        splitter.addWidget(options_widget)

        buttons_layout = QHBoxLayout()
        buttons_layout.setContentsMargins(2, 2, 2, 2)
        buttons_layout.setSpacing(2)
        self._add_part_btn = QToolButton()
        self._add_part_btn.setPopupMode(QToolButton.InstantPopup)
        self._add_part_btn.setIcon(tpDcc.ResourcesMgr().icon('add'))
        self._add_part_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self._add_part_btn.setAutoRaise(True)
        self._add_mold_btn = QToolButton()
        self._add_mold_btn.setPopupMode(QToolButton.InstantPopup)
        self._add_mold_btn.setIcon(tpDcc.ResourcesMgr().icon('add'))
        self._add_mold_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self._add_mold_btn.setAutoRaise(True)
        self._duplicate_part_btn = QToolButton()
        self._duplicate_part_btn.setPopupMode(QToolButton.InstantPopup)
        self._duplicate_part_btn.setIcon(tpDcc.ResourcesMgr().icon('add'))
        self._duplicate_part_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self._duplicate_part_btn.setAutoRaise(True)
        self._delete_part_btn = QToolButton()
        self._delete_part_btn.setPopupMode(QToolButton.InstantPopup)
        self._delete_part_btn.setIcon(tpDcc.ResourcesMgr().icon('trash'))
        self._delete_part_btn.setToolButtonStyle(Qt.ToolButtonIconOnly)
        self._delete_part_btn.setAutoRaise(True)
        buttons_layout.addWidget(self._add_part_btn)
        buttons_layout.addWidget(self._add_mold_btn)
        buttons_layout.addWidget(self._duplicate_part_btn)
        buttons_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        buttons_layout.addWidget(self._delete_part_btn)

        self._parts_tree = PartsTree()

        tree_layout.addLayout(buttons_layout)
        tree_layout.addWidget(self._parts_tree)

        options_layout.addWidget(QPushButton('Hello World'))

    def set_ui_state(self, flag):
        """
        Enables/disables puppet parts widget UI
        :param flag: bool
        """

        self._parts_tree.setEnabled(flag)

    def refresh(self):

        if not self._puppet:
            self.set_ui_state(False)

        self.set_ui_state(self._puppet.exists)
        if not self._puppet.exists:
            return

        temp_name = self._current_module_name
        self._parts_tree.clear()
        if not self._puppet.part_names:
            return


class PartsTree(QTreeWidget, object):
    def __init__(self, parent=None):
        super(PartsTree, self).__init__(parent)

        self.setAutoScroll(True)
        self.setAutoScrollMargin(20)
        self.setIconSize(QSize(40, 20))
        self.setIndentation(10)
        self.setRootIsDecorated(True)
        self.setHeaderHidden(True)
        self.setColumnCount(2)
