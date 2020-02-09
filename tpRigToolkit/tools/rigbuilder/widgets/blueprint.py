#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains templates widget
"""

from __future__ import print_function, division, absolute_import

from Qt.QtWidgets import *

from tpQtLib.core import base


class BlueprintWidget(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(BlueprintWidget, self).__init__(parent=parent)

    def ui(self):
        super(BlueprintWidget, self).ui()

        self.main_layout.addWidget(QPushButton('Hello World'))
