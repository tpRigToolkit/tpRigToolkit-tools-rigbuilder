#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains build node implementation for data import
"""

from __future__ import print_function, division, absolute_import

import tpDcc as tp

from tpRigToolkit.tools.rigbuilder.objects import build


class DataImport(build.BuildObject, object):

    COLOR = [255, 0, 0]
    SHORT_NAME = 'DATA'
    DESCRIPTION = 'Imports data into current DCC scene'
    ICON = 'import'

    def __init__(self, name=None):
        super(DataImport, self).__init__(name=name)

    def run(self, **kwargs):
        file_path = self.get_option('File', 'Inputs')[0]
        force = self.get_option('Force', 'Inputs')
        fit_view = self.get_option('Fit View', 'Inputs')
        tp.Dcc.import_file(file_path, force=force)
        if fit_view:
            tp.Dcc.fit_view()

        return True

    def setup_options(self):
        setup_options = super(DataImport, self).setup_options()

        setup_options['Inputs'] = {'value': True, 'group': None, 'type': 'group'}
        setup_options['File'] = {'value': '', 'group': 'Inputs', 'type': 'file'}
        setup_options['Force'] = {'value': True, 'group': 'Inputs', 'type': 'bool'}
        setup_options['Fit View'] = {'value': True, 'group': 'Inputs', 'type': 'bool'}

        return setup_options
