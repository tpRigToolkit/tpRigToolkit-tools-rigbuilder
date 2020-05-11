#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains puppeteer widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import stack

from tpRigToolkit.tools.rigbuilder.widgets.puppeteer import puppet, puppetparts


class PuppeteerWidget(base.BaseWidget, object):

    puppetRemoved = Signal()

    def __init__(self, parent=None):
        super(PuppeteerWidget, self).__init__(parent=parent)

        self.refresh_puppet_widget()

    def ui(self):
        super(PuppeteerWidget, self).ui()

        self._stack = stack.SlidingStackedWidget()
        self.main_layout.addWidget(self._stack)

        self._main_tab = QTabWidget()

        self._puppet_widget = puppet.PuppetWidget()
        self._puppet_parts = puppetparts.PuppetPartsWidget()

        self._main_tab.addTab(self._puppet_widget, 'Puppet')
        self._main_tab.addTab(self._puppet_parts, 'Parts')

        self._stack.addWidget(self._main_tab)

    def setup_signals(self):
        self._puppet_widget.puppetCreated.connect(self.refresh_puppet_widget)
        self._puppet_widget.puppetRemoved.connect(self.puppetRemoved.emit)

    def refresh_puppet_widget(self):
        """
        Refresh puppet widget UI
        """

        if self._puppet_widget.puppet.exists:
            self.refresh_puppet_parts_widget()
            self._main_tab.setCurrentIndex(1)
        else:
            self._main_tab.setCurrentIndex(0)

        self._puppet_widget.refresh()

    def refresh_puppet_parts_widget(self):
        """
        Refreshes puppet parts widget
        """

        self._puppet_parts.puppet = self._puppet_widget.puppet
        self._puppet_parts.refresh()
