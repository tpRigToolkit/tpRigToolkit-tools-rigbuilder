#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Naming class that manages tpRigToolkit.tools.rigbuilder controls
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os

from tpDcc.libs.python import decorators
from tpRigToolkit.libs.controlrig.core import controllib
from tpRigToolkit.tools.controlrig.widgets import controlrig

from tpRigToolkit.tools import rigbuilder


@decorators.Singleton
class RigBuilderControlLib(controllib.ControlLib, object):
    def __init__(self):
        controllib.ControlLib.__init__(self)

        project = rigbuilder.project
        if not project:
            return

        self.controls_file = os.path.join(project.full_path, 'controls.json')

        self.load_control_data()


class RigBuilderControlSelector(controlrig.ControlSelector, object):

    CONTROLS_LIB = RigBuilderControlLib

    def __init__(self, controls_path=None, parent=None):
        super(RigBuilderControlSelector, self).__init__(
            controls_path=controls_path,  parent=parent)
