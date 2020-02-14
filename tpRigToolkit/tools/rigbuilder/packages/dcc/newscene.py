#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains build node implementation for new scenes
"""

from __future__ import print_function, division, absolute_import

from Qt.QtWidgets import *

from tpRigToolkit.core import resource
from tpRigToolkit.tools.rigbuilder.objects import build
from tpRigToolkit.tools.rigbuilder.widgets import properties


class NewScene(build.BuildObject, object):

    COLOR = [255, 255, 0]
    SHORT_NAME = 'NEW'
    DESCRIPTION = 'Creates a new DCC scene'
    ICON = resource.ResourceManager().icon('new_file')

    def __init__(self, name=None):
        super(NewScene, self).__init__(name=name)

    def get_option_file(self):
        super(NewScene, self).get_option_file()

        self.add_option('node_title', 'Hello World!', option_type='title')

    def create_properties_widget(self, properties_widget):
        super(NewScene, self).create_properties_widget(properties_widget=properties_widget)

        base_category = properties.CollapsibleFormWidget(head_name='Inputs')
        self._force = QCheckBox()
        base_category.add_widget(label='Force', widget=self._force)
        properties_widget.add_widget(base_category)
