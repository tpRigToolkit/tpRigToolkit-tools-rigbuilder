#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains properties tool tool implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpDcc.libs.python import decorators
from tpDcc.libs.qt.widgets import label, stack, loading

from tpRigToolkit.tools.rigbuilder.core import tool
from tpRigToolkit.tools.rigbuilder.widgets.base import options


class PropertiesTool(tool.DockTool, object):

    NAME = 'Properties'
    TOOLTIP = 'Shows properties/options depending on the context'
    DEFAULT_DOCK_AREA = Qt.RightDockWidgetArea
    IS_SINGLETON = True

    def __init__(self):
        super(PropertiesTool, self).__init__()

        self._fill_delegate = None
        self._object = None
        self.setWindowTitle(self.unique_name())
        self._created = False
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

    def show_tool(self):
        super(PropertiesTool, self).show_tool()

        if not self._created:
            self._create_ui()
            self._created = True

    def _create_ui(self):
        self._stack = stack.SlidingStackedWidget()

        loading_widget = QWidget()
        loading_lyt = QVBoxLayout()
        loading_widget.setLayout(loading_lyt)
        self._loading = loading.CircleLoading(size=40)
        loading_lbl_lyt = QHBoxLayout()
        loading_lbl = label.BaseLabel('Loading properties. Please wait ...')
        loading_lbl_lyt.addStretch()
        loading_lbl_lyt.addWidget(loading_lbl)
        loading_lbl_lyt.addStretch()
        loading_lyt2 = QHBoxLayout()
        loading_lyt2.addStretch()
        loading_lyt2.addWidget(self._loading)
        loading_lyt2.addStretch()
        loading_lyt.addStretch()
        loading_lyt.addLayout(loading_lyt2)
        loading_lyt.addLayout(loading_lbl_lyt)
        loading_lyt.addStretch()

        self._lbl_widget = QWidget()
        lbl_lyt = QHBoxLayout()
        self._lbl_widget.setLayout(lbl_lyt)
        no_props_lbl = label.BaseLabel('No Build Node selected').h4()
        lbl_lyt.addStretch()
        lbl_lyt.addWidget(no_props_lbl)
        lbl_lyt.addStretch()
        self._options_widget = options.RigBuilderOptionsWidget()
        self._options_widget.hide_edit_widget()

        self._stack.addWidget(self._lbl_widget)
        self._stack.addWidget(loading_widget)
        self._stack.addWidget(self._options_widget)

        self._content_layout.addWidget(self._stack)

        self._stack.animFinished.connect(self._on_refresh)

    def clear(self, update_stack=True):
        if update_stack:
            self._stack.slide_in_index(0)
        self._options_widget.clear_options()

    def refresh(self):
        if self._object:
            self._options_widget.get_option_object().load_options()
            self._options_widget.update_options()

    @decorators.timestamp
    def set_object(self, object):
        self._object = object
        if not self._object:
            self._stack.slide_in_index(0)
        else:
            self._stack.slide_in_index(1)

    def _on_refresh(self, index):
        if index == 2:
            return

        self._options_widget.set_option_object(self._object, force_update=False)
        self.refresh()
        if index == 0:
            return
        if self._object:
            self._stack.slide_in_index(2)
        else:
            self._stack.slide_in_index(0)



