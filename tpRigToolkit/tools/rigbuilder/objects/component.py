#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains build node implementation rigbuilder Rig Components
"""

import os
from tpDcc.libs.python import path as path_utils

from tpRigToolkit.tools.rigbuilder.core import api
from tpRigToolkit.tools.rigbuilder.objects import build


class RigComponent(build.BuildObject, object):

    COLOR = [25, 165, 150]
    SHORT_NAME = 'CMP'
    DESCRIPTION = 'Core module to create rig components'
    ICON = 'box'

    def __init__(self, name=None, rig=None):
        super(RigComponent, self).__init__(name=name, rig=rig)

    def run(self, *args, **kwargs):
        return True

    def setup_options(self):
        setup_options = super(RigComponent, self).setup_options()

        setup_options['Inputs'] = {'value': True, 'group': None, 'type': 'group'}
        setup_options['Component Description'] = {'value': 'component', 'group': 'Inputs', 'type': 'string'}
        setup_options['Size'] = {'value': 1.0, 'group': 'Inputs', 'type': 'float'}
        setup_options['Joints'] = {'value': [], 'group': 'Inputs', 'type': 'list'}
        setup_options['Joints Name Rule'] = {'value': '', 'group': 'Inputs', 'type': 'string'}
        setup_options['Control Size'] = {'value': 1.0, 'group': 'Inputs', 'type': 'float'}
        setup_options['Mirror'] = {'value': False, 'group': 'Inputs', 'type': 'bool'}

        return setup_options

    def get_global_scale(self):
        """
        Returns global scale
        :return: float
        """

        project_scale = 1.0
        current_project = api.get_current_project()
        if current_project:
            if current_project.has_option('size'):
                project_scale = current_project.get_option('size')
            elif current_project.has_option('scale'):
                project_scale = current_project.get_option('scale')

        size = self.get_option('Size', group='Inputs', default=1.0)

        global_scale = float(project_scale) * float(size)

        return global_scale

    def get_controls_size(self):
        """
        Returns global control size
        :return: float
        """

        global_scale = self.get_global_scale()
        controls_size = self.get_option('Control Size', group='Inputs', default=1.0)

        controls_size = global_scale * float(controls_size)

        return controls_size

    def get_parent_component(self):
        """
        Returns parent rig component of this one
        """

        if not self._rig:
            return

        current_path = self.get_path()
        parent_path = '/'.join(current_path.split('/')[:-1])
        rig_path = self._rig.get_code_path()
        parent_component_name = path_utils.clean_path(os.path.relpath(parent_path, rig_path))
        parent_component, parent_component_package = self._rig.get_build_node_instance(parent_component_name)

        return parent_component
