#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains console widget for tpRigToolkit.tools.rigbuilder
"""

from __future__ import print_function, division, absolute_import

from tpDcc.libs.qt.widgets import console


class Console(console.Console, object):
    def __init__(self, parent=None):
        super(Console, self).__init__(parent=parent)


class ConsoleInput(console.ConsoleInput, object):
    def __init__(self, parent=None):
        super(ConsoleInput, self).__init__(parent=parent)
