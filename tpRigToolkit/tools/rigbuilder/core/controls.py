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

from tpPyUtils import decorators
from tpRigToolkit.tools.controlrig.core import controllib

from tpRigToolkit.tools import rigbuilder


@decorators.Singleton
class RigBuilderControlLib(controllib.ControlLib, object):
    def __init__(self):
        controllib.ControlLib.__init__(self)

        project = rigbuilder.project
        if not project:
            return

        self.controls_file = os.path.join(project.get_full_path(), 'controls.json')

        self.load_control_data()
