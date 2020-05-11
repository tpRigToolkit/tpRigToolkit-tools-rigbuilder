#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains build node implementation for scripts
"""

from __future__ import print_function, division, absolute_import

import tpDcc

from tpRigToolkit.tools.rigbuilder.objects import build


class Blueprint(build.BuildObject, object):

    COLOR = [125, 0, 125]
    SHORT_NAME = 'BP'
    DESCRIPTION = 'Creates RigBuilder Blueprint'
    ICON = 'blueprint'

    def __init__(self, name=None):
        super(Blueprint, self).__init__(name=name)

    def create_properties_widget(self, properties_widget):
        super(Blueprint, self).create_properties_widget(properties_widget=properties_widget)
