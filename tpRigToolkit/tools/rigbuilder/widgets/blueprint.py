#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains templates widget
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpQtLib.core import base
from tpQtLib.widgets import splitters


class BlueprintWidget(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(BlueprintWidget, self).__init__(parent=parent)

    def ui(self):
        super(BlueprintWidget, self).ui()

        main_splitter = QSplitter(Qt.Vertical)
        self.main_layout.addWidget(main_splitter)

        self._presets_list = PresetsList()
        self._outliner = BlueprintsOutliner()
        main_splitter.addWidget(self._presets_list)
        main_splitter.addWidget(self._outliner)


class PresetsList(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(PresetsList, self).__init__(parent=parent)

    def ui(self):
        super(PresetsList, self).ui()

        self._presets_list = QListWidget()

        self.main_layout.addWidget(splitters.Splitter('Presets'))
        self.main_layout.addWidget(self._presets_list)


class BlueprintsOutliner(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(BlueprintsOutliner, self).__init__(parent=parent)

    def ui(self):
        super(BlueprintsOutliner, self).ui()

        self._blueprints_list = QListWidget()

        self.main_layout.addWidget(splitters.Splitter('Current Blueprints'))
        self.main_layout.addWidget(self._blueprints_list)
