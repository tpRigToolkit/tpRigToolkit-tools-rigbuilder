#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains build node implementation for new scenes
"""

from __future__ import print_function, division, absolute_import

import tpDcc as tp

from tpRigToolkit.tools.rigbuilder.objects import build


class NewScene(build.BuildObject, object):

    COLOR = [255, 255, 0]
    SHORT_NAME = 'NEW'
    DESCRIPTION = 'Creates a new DCC scene'
    ICON = 'new'

    def __init__(self, name=None):
        super(NewScene, self).__init__(name=name)

    def run(self, **kwargs):
        force = self.get_option('Force', group='Inputs')
        tp.Dcc.new_file(force=force)

        return True

    def setup_options(self):
        setup_options = super(NewScene, self).setup_options()

        setup_options['Inputs'] = {'value': True, 'group': None, 'type': 'group'}
        setup_options['Force'] = {'value': True, 'group': 'Inputs', 'type': 'bool'}

        return setup_options
