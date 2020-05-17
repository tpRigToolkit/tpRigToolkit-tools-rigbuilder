#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains build object implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

from collections import OrderedDict

import tpDcc

from tpRigToolkit.tools.rigbuilder.core import consts
from tpRigToolkit.tools.rigbuilder.objects import script


class BuildObject(script.ScriptObject, object):

    SCRIPT_EXTENSION = 'yml'
    SHORT_NAME = 'BUILD'
    COLOR = [255, 0, 0]
    ICON = 'ok'

    PROPERTIES_FILE_NAME = consts.PROPERTIES_FILE_NAME
    PROPERTIES_FILE_EXTENSION = consts.PROPERTIES_FILE_EXTENSION

    def __init__(self, name=None, rig=None):

        self._item_icon = None
        self._rig = rig

        super(BuildObject, self).__init__(name=name)

    @property
    def rig(self):
        return self._rig

    @rig.setter
    def rig(self, value):
        self._rig = value

    def get_icon(self):
        """
        Returns QIcon attached to this object
        :return: QIcon
        """

        if self._item_icon:
            return self._item_icon

        return tpDcc.ResourcesMgr().icon(self.ICON)

    def run(self, rig_object, project, *args, **kwargs):
        """
        Function that executes build function
        :return: bool
        """

        return False

    def _get_value_from_option_type(self, value, option_type):
        if option_type == 'rigcontrol':
            value = [value, 'rigcontrol']
        else:
            value = super(BuildObject, self)._get_value_from_option_type(value=value, option_type=option_type)

        return value

    def setup_options(self):

        options = OrderedDict([
            ('Base', {'value': True, 'group': None, 'type': 'group'}),
            ('Name', {'value': self.get_name(), 'group': 'Base', 'type': 'nonedittext'}),
            ('Description', {'value': self.DESCRIPTION, 'group': 'Base', 'type': 'nonedittext'})
        ])

        return options

    def load_options(self):
        setup_options = self.setup_options() or dict()
        for option_name, option_info in setup_options.items():
            option_value = option_info.get('value', None)
            option_group = option_info.get('group', None)
            option_type = option_info.get('type', None)
            if option_type == 'group' and not option_name.endswith('.'):
                option_name = '{}.'.format(option_name)
            if self.has_option(option_name, option_group):
                continue
            else:
                self.add_option(option_name, option_value, option_group, option_type)


class PackObject(BuildObject, object):
    def __init__(self, name=None, rig=None):
        super(PackObject, self).__init__(name=name, rig=rig)
