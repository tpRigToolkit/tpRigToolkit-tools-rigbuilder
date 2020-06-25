#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains build node implementation rigbuilder Rig Components
"""

import os
import tpDcc as tp

from tpDcc.libs.python import path as path_utils, folder as folder_utils

from tpRigToolkit.tools.rigbuilder.core import api
from tpRigToolkit.tools.rigbuilder.objects import build


class RigComponent(build.BuildObject, object):

    COLOR = [25, 165, 150]
    SHORT_NAME = 'CMP'
    DESCRIPTION = 'Core module to create rig components'
    ICON = 'box'

    def __init__(self, name=None, rig=None):
        super(RigComponent, self).__init__(name=name, rig=rig)

        self._controls_group = 'controls'
        self._setup_group = 'setup'
        self._main_group = 'master'

    @property
    def main_group(self):
        return self._main_group

    @property
    def controls_group(self):
        return self._controls_group

    @property
    def setup_group(self):
        return self._setup_group

    def run(self, *args, **kwargs):
        description = self.get_option('Component Description', group='Inputs', default='master')
        main_group = self.get_option('Main Group', group='Rig')
        controls_group = self.get_option('Controls Group', group='Rig', default='controls')
        setup_group = self.get_option('Rig Group', group='Rig', default='setup')

        main_group_name = api.solve_name(description, main_group)
        controls_group_name = api.solve_name(description, controls_group)
        setup_group_name = api.solve_name(description, setup_group)

        self._main_group = tp.Dcc.create_empty_group(main_group_name)
        self._controls_group = tp.Dcc.create_empty_group(controls_group_name, parent=self._main_group)
        self._setup_group = tp.Dcc.create_empty_group(setup_group_name, parent=self._main_group)

        return True

    def post_run(self, *args, **kwargs):

        # Clean groups that are empty
        for grp in [self._controls_group, self._setup_group]:
            if grp and tp.Dcc.object_exists(grp) and tp.Dcc.node_is_empty(grp):
                tp.Dcc.delete_object(grp)

        main_group = self.get_main_group(get_parent_component=True)
        if self.main_group != main_group:
            tp.Dcc.set_parent(self.main_group, main_group)

        return True

    def setup_options(self):
        setup_options = super(RigComponent, self).setup_options()

        setup_options['Rig'] = {'value': True, 'group': None, 'type': 'group'}
        setup_options['Main Group'] = {'value': 'master', 'group': 'Rig', 'type': 'string'}
        setup_options['Controls Group'] = {'value': 'controls', 'group': 'Rig', 'type': 'string'}
        setup_options['Setup Group'] = {'value': 'rig', 'group': 'Rig', 'type': 'string'}
        setup_options['Inputs'] = {'value': True, 'group': None, 'type': 'group'}
        setup_options['Component Description'] = {'value': 'component', 'group': 'Inputs', 'type': 'string'}
        setup_options['Size'] = {'value': 1.0, 'group': 'Inputs', 'type': 'float'}
        setup_options['Control Size'] = {'value': 1.0, 'group': 'Inputs', 'type': 'float'}
        setup_options['Mirror'] = {'value': False, 'group': 'Inputs', 'type': 'bool'}
        setup_options['Use Side Colors'] = {'value': True, 'group': 'Inputs', 'type': 'bool'}

        return setup_options

    def get_mirror(self):
        """
        Returns whether rig component should be mirrored or not
        :return: bool
        """

        return self.get_option('Mirror', group='Inputs', default=False)

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

    def get_children_components(self):
        """
        Returns all components that are part of this one
        """

        children_components = list()

        if not self._rig:
            return children_components

        rig_path = self._rig.get_code_path()
        current_path = self.get_path()
        folders = folder_utils.get_folders(current_path)
        if not folders:
            return children_components

        for folder_name in folders:
            child_path = os.path.join(current_path, folder_name)
            child_component_name = path_utils.clean_path(os.path.relpath(child_path, rig_path))
            child_component = self._rig.get_build_node_instance(child_component_name)
            if child_component:
                children_components.append(child_component)

        return children_components

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
        parent_component = self._rig.get_build_node_instance(parent_component_name)

        return parent_component

    def get_main_group(self, get_parent_component=False):
        """
        Returns master group of this component
        If the rig component is attached to a parent component, parent component controls group will be used
        :return:
        """

        main_group = self._main_group
        if get_parent_component:
            parent_component = self.get_parent_component()
            if parent_component:
                if hasattr(parent_component, 'main_group'):
                    main_group = parent_component.main_group

        return main_group

    def get_controls_group(self, get_parent_component=False):
        """
        Returns controls group this component should use
        If the rig component is attached to a parent component, parent component controls group will be used
        :return: str
        """

        controls_grp = self._controls_group
        if get_parent_component:
            parent_component = self.get_parent_component()
            if parent_component:
                if hasattr(parent_component, 'controls_group'):
                    controls_grp = parent_component.controls_group

        return controls_grp

    def get_setup_group(self, get_parent_component=False):
        """
        Returns setup group this component should use
        If the rig component is attached to a parent component, parent component setup group will be used
        :return: str
        """

        setup_grp = self._setup_group
        if get_parent_component:
            parent_component = self.get_parent_component()
            if parent_component:
                if hasattr(parent_component, 'setup_group'):
                    setup_grp = parent_component.setup_group

        return setup_grp


class ChainComponent(RigComponent, object):
    """
    Custom rig component that can be reused to create components with support switch states
    """

    def __init__(self, name=None, rig=None):
        super(RigComponent, self).__init__(name=name, rig=rig)

        self._chain_joints = dict()
        self._joints_to_attach = dict()
        self._switch_controls_group = dict()
        self._switch_attribute = 'switch'
        self._auto_switch_visibility = True
        self._attach_type = 0

    def setup_options(self):
        setup_options = super(ChainComponent, self).setup_options()

        setup_options['Chain'] = {'value': True, 'group': None, 'type': 'group'}
        setup_options['Duplicate Hierarchy'] = {'value': False, 'group': 'Chain', 'type': 'bool'}
        setup_options['Attach Chain'] = {'value': False, 'group': 'Chain', 'type': 'bool'}
        setup_options['Create Switch'] = {'value': True, 'group': 'Chain', 'type': 'bool'}

        return setup_options

    def get_duplicate_hierarchy(self):
        return self.get_option('Duplicate Hierarchy', group='Chain')

    def set_duplicate_hierarchy(self, flag):
        self.set_option('Duplicate Hierarchy', flag, group='Chain')

    def get_attach_chain(self):
        return self.get_option('Attach Chain', group='Chain')

    def set_attach_chain(self, flag):
        self.set_option('Attach Chain', flag, group='Chain')

    def get_create_switch(self):
        return self.get_option('Create Switch', group='Chain')

    def set_create_switch(self, flag):
        self.set_option('Create Switch', flag, group='Chain')

    def get_switch_attribute(self):
        return self._switch_attribute

    def set_switch_attribute(self, value):
        self._switch_attribute = value

    def get_auto_switch_visibility(self):
        return self._auto_switch_visibility

    def set_auto_switch_visibility(self, flag):
        self._auto_switch_visibility = flag

    def get_attach_type(self):
        return self._attach_type

    def set_attach_type(self, index):
        self._attach_type = index

    def get_chain_joints(self, side):
        return self._chain_joints[side] if side in self._chain_joints else list()

    def get_joints_to_attach(self, side):
        return self._joints_to_attach[side] if side in self._joints_to_attach else list()

    def get_switch_controls_group(self, side):
        return self._switch_controls_group[side] if side in self._switch_controls_group else None

    def _setup_rig(self, side, rig, joints):
        controls_grp = self.get_controls_group()
        setup_grp = self.get_setup_group()

        self._chain_joints[side] = joints
        self._joints_to_attach[side] = rig.buffer_joints
        self._switch_controls_group[side] = rig.controls_group

        rig.set_control_parent(controls_grp)
        if self.get_duplicate_hierarchy():
            rig.set_setup_parent(setup_grp)
        else:
            rig.delete_setup()
