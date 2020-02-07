#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Procedural Script based auto rigger
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from tpQtLib.core import base

import tpRigToolkit


class RigBuilderTool(tpRigToolkit.Tool, object):
    def __init__(self, config):
        super(RigBuilderTool, self).__init__(config=config)

    def ui(self):
        super(RigBuilderTool, self).ui()

        self._rig_builder_widget = RigBuilderWidget()
        self.main_layout.addWidget(self._rig_builder_widget)


class RigBuilderWidget(base.BaseWidget, object):
    def __init__(self, parent=None):
        super(RigBuilderWidget, self).__init__(parent=parent)

    def ui(self):
        super(RigBuilderWidget, self).ui()
