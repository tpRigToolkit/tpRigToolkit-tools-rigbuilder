#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for properties editor widget
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpQtLib.core import base

from tpQtLib.widgets import search


class PropertiesWidget(base.BaseWidget, object):
    def __init__(self, search_by_headers=False, parent=None):

        self._search_by_headers = search_by_headers

        super(PropertiesWidget, self).__init__(parent=parent)

    def get_main_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        main_layout.setObjectName('propertiesMainLayout')
        main_layout.setContentsMargins(2, 2, 2, 2)

        return main_layout

    def ui(self):
        super(PropertiesWidget, self).ui()

        self._search_widget = QWidget()
        self._search_layout = QHBoxLayout()
        self._search_layout.setContentsMargins(1, 1, 1, 1)
        self._search_widget.setLayout(self._search_layout)
        self._search_line = search.SearchFindWidget()
        self._search_line.setObjectName('searchLine')
        self._search_line.set_placeholder_text('Search Property ...')

        self._search_layout.addWidget(self._search_line)
        # self._search_widget.setVisible(False)

        self._content_layout = QVBoxLayout()
        self._content_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        self.main_layout.addWidget(self._search_widget)
        self.main_layout.addLayout(self._content_layout)
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))