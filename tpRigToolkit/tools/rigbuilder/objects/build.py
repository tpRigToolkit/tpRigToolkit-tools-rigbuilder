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

from Qt.QtWidgets import *

import logging

from tpRigToolkit.core import resource
from tpRigToolkit.tools.rigbuilder.objects import script
from tpRigToolkit.tools.rigbuilder.widgets import properties

LOGGER = logging.getLogger('tpRigToolkit')


class BuildObject(script.ScriptObject, object):

    SCRIPT_EXTENSION = 'yml'
    SHORT_NAME = 'BUILD'
    COLOR = [255, 0, 0]
    ICON = resource.ResourceManager().icon('ok')

    def __init__(self, name=None):
        super(BuildObject, self).__init__(name=name)

    def create_properties_widget(self, properties_widget):
        base_category = properties.CollapsibleFormWidget(head_name='Base')
        line_name = QLineEdit(self.get_name())
        line_name.setReadOnly(True)
        line_description = QLineEdit(str(self.DESCRIPTION))
        base_category.add_widget(label='Name', widget=line_name)
        base_category.add_widget(label='Description', widget=line_description)
        properties_widget.add_widget(base_category)




class PackObject(BuildObject, object):
    def __init__(self, name=None):
        super(PackObject, self).__init__(name=name)
