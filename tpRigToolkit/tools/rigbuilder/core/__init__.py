#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for tpRigToolkit.tools.rigbuilder-core
"""

from __future__ import print_function, division, absolute_import

import os

order = [
    'tpRigToolkit.tools.rigbuilder.core.consts',
    'tpRigToolkit.tools.rigbuilder.core.utils'
]

os.environ['RIGBUILDER_PATH'] = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
os.environ['RIGBUILDER_RUN'] = 'False'
os.environ['RIGBULIDER_STOP'] = 'False'
os.environ['RIGBUILDER_SETTINGS'] = ''
os.environ['RIGBUILDER_TEMP_LOG'] = ''
os.environ['RIGBUILDER_KEEP_TEMP_LOG'] = 'False'
os.environ['RIGBUILDER_LAST_TEMP_LOG'] = ''
os.environ['RIGBUILDER_CURRENT_SCRIPT'] = ''
os.environ['RIGBUILDER_COPIED_SCRIPT'] = ''
os.environ['RIGBUILDER_SAVE_COMMENT'] = ''
