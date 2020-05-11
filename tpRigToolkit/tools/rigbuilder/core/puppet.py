#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains core puppet implementation for RigBuilder
"""

from __future__ import print_function, division, absolute_import

import os

import tpDcc as tp
from tpDcc.libs.python import yamlio, path as path_utils
from tpDcc.libs.qt.core import qtutils

from tpRigToolkit.tools.rigbuilder import __version__
from tpRigToolkit.tools.rigbuilder import puppeteer
from tpRigToolkit.tools.rigbuilder.core import consts
from tpRigToolkit.libs.controlrig.core import controllib


class Puppet(object):
    def __init__(self, name='puppet'):
        self._name = name
        self._part_names = list()
        self._parts = dict()
        self._exists = False

        self.load()

    @property
    def name(self):
        return self._name

    @property
    def part_names(self):
        return self._part_names

    @property
    def parts(self):
        return self._parts

    @property
    def exists(self):
        return self._exists

    def load(self):
        """
        Loads puppet
        """

        if not tp.Dcc.object_exists(consts.PUPPET_PARTS_GROUP) or not tp.Dcc.object_exists(consts.PUPPET_MAIN_GROUP):
            return

        self._exists = True

        all_scene_nodes = tp.Dcc.all_scene_objects()
        for node in all_scene_nodes:
            if tp.Dcc.attribute_exists(node, consts.PUPPET_NODE_TYPE_ATTR):
                if tp.Dcc.get_attribute_value(node, consts.PUPPET_NODE_TYPE_ATTR) == consts.PUPPET_TYPE:
                    self._name = tp.Dcc.get_attribute_value(node, consts.PUPPET_NAME_ATTR)
                    break

        parts_folder = tp.Dcc.list_relatives(consts.PUPPET_PARTS_GROUP, all_hierarchy=True) or list()
        for module_folder in parts_folder:
            print(module_folder)

    def create(self):
        """
        Creates current puppet in DCC scene
        """

        root_grp = tp.Dcc.create_empty_group(name=consts.PUPPET_MAIN_GROUP)
        tp.Dcc.add_string_attribute(root_grp, consts.PUPPET_NODE_TYPE_ATTR, consts.PUPPET_RIG_TYPE_ATTR)
        tp.Dcc.add_string_attribute(root_grp, consts.PUPPET_NAME_ATTR, self._name)
        tp.Dcc.add_string_attribute(root_grp, consts.PUPPET_VERSION_ATTR, str(__version__.__version__), lock=True)
        tp.Dcc.add_float_attribute(root_grp, consts.PUPPET_RIG_GUIDES_SIZE_ATTR, lock=True)
        tp.Dcc.add_float_attribute(root_grp, consts.PUPPET_RIG_JOINTS_SIZE_ATTR, lock=True)

        rig_grp = tp.Dcc.create_empty_group(name=consts.PUPPET_RIG_GROUP, parent=root_grp)
        geo_grp = tp.Dcc.create_empty_group(name=consts.PUPPET_GEO_GROUP, parent=rig_grp)
        parts_grp = tp.Dcc.create_empty_group(name=consts.PUPPET_PARTS_GROUP, parent=rig_grp)
        skeleton_grp = tp.Dcc.create_empty_group(name=consts.PUPPET_SKELETON_GROUP, parent=rig_grp)
        tp.Dcc.set_attribute_value(skeleton_grp, 'overrideEnabled', True)
        tp.Dcc.set_attribute_value(skeleton_grp, 'overrideColor', 29)
        tp.Dcc.set_attribute_value(skeleton_grp, 'template', True)
        twists_grp = tp.Dcc.create_empty_group(name=consts.PUPPET_TWISTS_GROUP, parent=rig_grp)

        tp.Dcc.clear_selection()

        tp.Dcc.create_selection_group(consts.PUPPET_CONTROL_SET)
        tp.Dcc.create_selection_group(consts.PUPPET_MAIN_SET)
        tp.Dcc.create_selection_group(consts.PUPPET_SKIN_JOINTS_SETS)
        tp.Dcc.create_selection_group(consts.PUPPET_MODULES_SET)
        tp.Dcc.add_node_to_selection_group(consts.PUPPET_SKIN_JOINTS_SETS, consts.PUPPET_MAIN_SET)
        tp.Dcc.add_node_to_selection_group(consts.PUPPET_MODULES_SET, consts.PUPPET_MAIN_SET)

        self._exists = True

    def delete(self):
        """
        Remove current puppet from scene
        """

        for part_name in self._parts:
            part = self._parts[part_name]
            part.delete()

        tp.Dcc.delete_object(consts.PUPPET_MAIN_GROUP)
        all_scene_nodes = tp.Dcc.all_scene_objects()
        for node in all_scene_nodes:
            if tp.Dcc.attribute_exists(node, consts.PUPPET_PART_NAME_ATTR):
                tp.Dcc.delete_object(node)

        if tp.Dcc.object_exists(consts.PUPPET_MAIN_SET):
            tp.Dcc.delete_object(consts.PUPPET_MAIN_SET)

        self._exists = False
        self._part_names = list()
        self._parts = dict()


class PuppetPart(object):
    def __init__(self):
        self._name = ''
        self._type = ''
        self._root = ''
        self._path = ''
        self._parent = None
        self._symmetrical = False
        self._opposite = list()
        self._node = None
        self._additional_controls = list()

    @property
    def name(self):
        return self._name

    @property
    def type(self):
        return self._type

    @property
    def root(self):
        return self._root

    @property
    def path(self):
        return self._path

    @property
    def parent(self):
        return self._parent

    def create(self, options=None):
        if options is None:
            options = dict()


def get_parts_path():
    """
    Returns path where parts are located
    :return: str
    """

    return path_utils.clean_path(
        os.path.join(os.path.dirname(os.path.abspath(puppeteer.__file__)), consts.PUPPET_PARTS_FOLDER))


def get_part_path(part_name):
    """
    Returns path where given part should be located
    :param part_name: str
    :return: str
    """

    return path_utils.clean_path(os.path.join(get_parts_path(), part_name))


def get_part_files():
    """
    Returns all part files available in tpRigBuilder
    :return: list(str)
    """

    list_of_part_files = os.listdir(get_parts_path())
    part_files = list()
    for part in list_of_part_files:
        if part in ['incrementalSave']:
            continue
        if '.' not in part and part[0] != '_':
            part_name = part.split('.')[0]
            part_files.append(part_name)

    return part_files


def get_part_groups():
    """
    Returns all groups available in tpRigBuilder
    :return: list(str)
    """

    groups = dict()

    for part_file in get_part_files():
        part_dir = get_part_path(part_name=part_file)
        metadata = yamlio.read_file(os.path.join(part_dir, consts.PUPPET_METADATA_FILE))
        group = metadata.get('group', 'Custom')
        try:
            group_list = groups[group]
        except Exception:
            group_list = list()
        group_list.append(part_file)
        groups[group] = group_list

    return groups


def get_part_dcc_file(part_name, extension=None):
    """
    Returns DCC path file of the given part
    :param part_name: str
    :param extension: str
    :return: str
    """

    if not extension:
        extension = tp.Dcc.get_extensions()[0]
    if not extension:
        return False
    if not extension.startswith('.'):
        extension = '.{}'.format(extension)

    part_path = get_part_path(part_name)
    if not os.path.isdir(part_path):
        return False

    part_dcc_file = os.path.join(part_path, '{}{}'.format(part_name, extension))

    return part_dcc_file


def part_has_file(part_name, extension=None):
    """
    Returns whether or not given part has DCC file created or not
    :param part_name: str
    :param extension: str
    :return: bool
    """

    part_dcc_file = get_part_dcc_file(part_name=part_name, extension=extension)
    if not os.path.isfile(part_dcc_file):
        return False

    return True


def format_name(input_str):
    """
    Formats name to be used in puppeteer (removes uppercase letters, digits
    and underscores and capitalizes first letter)
    :param input_str: str
    :return: str
    """

    new_name = ''
    for n in input_str:
        if n.isupper() or n.isdigit():
            n = ' ' + n
        if n == '_':
            n = ' '
        new_name += n
    new_name = new_name[0].upper() + new_name[1:]

    return new_name


def create_main_guide_control(control_name=consts.PUPPET_MAIN_GUIDE, parent=None):
    """
    Function that creates main control for guides
    """

    main_guide = controllib.ControlLib().create_control_by_name(
        'cube', name=control_name, size=0.15, parent=parent)[0][0]
    main_guide_shape = tp.Dcc.list_shapes(main_guide)[0]
    tp.Dcc.set_attribute_value(main_guide_shape, 'overrideEnabled', True)
    tp.Dcc.set_attribute_value(main_guide_shape, 'overrideColor', 10)
    main_cluster, main_handle = tp.Dcc.create_cluster(
        main_guide, cluster_name=consts.PUPPET_MAIN_GUIDE_CLUSTER, relative=True)
    tp.Dcc.add_float_attribute(main_guide, consts.PUPPET_GUIDE_SIZE_ATTR, default_value=1.0, min_value=0.0)
    for axis in 'XYZ':
        tp.Dcc.connect_attribute(main_guide, 'size', main_handle, 'scale{}'.format(axis))
    tp.Dcc.hide_node(main_handle)
    tp.Dcc.set_parent(main_handle, main_guide)
    for axis in 'YZ':
        scale_axis_attr = 'scale{}'.format(axis)
        tp.Dcc.connect_attribute(main_guide, 'scaleX', main_guide, scale_axis_attr)
        tp.Dcc.unkeyable_attribute(main_guide, scale_axis_attr)
        tp.Dcc.hide_attribute(main_guide, scale_axis_attr)
        tp.Dcc.lock_attribute(main_guide, scale_axis_attr)

    return main_guide


def create_puppet_shaders():
    """
    Internal function that creates all necessary materials used by puppet parts
    :return: dict
    """

    # Create materials
    color_names = ('black', 'blue', 'green', 'red', 'darkRed', 'yellow')
    color_values = ((0.0, 0.0, 0.0), (0.045, 0.045, 0.7), (0.055, 0.312, 0.055),
                    (0.578, 0.057, 0.057), (0.52, 0.010, 0.010), (1.0, 1.0, 0.1))

    shaders = dict()
    for color_name, color_value in zip(color_names, color_values):
        shader_name = '{}_guide_mat'.format(color_name)
        if tp.Dcc.object_exists(shader_name):
            shaders[color_name] = shader_name
        else:
            shader = tp.Dcc.create_surface_shader(shader_name)
            tp.Dcc.set_attribute_value(shader, 'outColor', color_value)
            shaders[color_name] = shader

    return shaders


def create_main_guide(guide_name=''):
    """
    Creates a new main guide into current opened DCC puppet part
    :param guide_name: str
    :return: str
    """

    if not guide_name:
        guide_name = qtutils.get_string_input(
            'Please enter new main guide name', 'Create Main Guide', old_name=consts.PUPPET_MAIN_GUIDE)
        if not guide_name:
            return False

    if tp.Dcc.object_exists(guide_name):
        qtutils.warning_message('Guide "{}" already exists!'.format(guide_name))
        return False

    guide_suffix = '_{}'.format(consts.PUPPET_GUIDE)
    if not guide_name.endswith(guide_suffix):
        guide_name = '{}{}'.format(guide_name, guide_suffix)

    if ' ' in guide_name or '-' in guide_name or guide_name[0].isdigit():
        qtutils.warning_message('Guide "{}" cannot contains spaces, - or start with a digit'.format(guide_name))
        return False

    if guide_name == consts.PUPPET_MAIN_GUIDE and tp.Dcc.object_exists(guide_name):
        main_guide = guide_name
        tp.Dcc.select_object(main_guide)
    else:
        main_guide = create_main_guide_control(control_name=guide_name)
        if tp.Dcc.object_exists(consts.PUPPET_MAIN_GUIDE) and main_guide != consts.PUPPET_MAIN_GUIDE:
            tp.Dcc.set_parent(main_guide, consts.PUPPET_MAIN_GUIDE)
        tp.Dcc.select_object(main_guide)

    return main_guide


def create_guide(guide_name=consts.PUPPET_ROOT_GUIDE, guide_parent=None, gizmo_shader=None):
    """
    Creates a new guide into current opened DCC puppet part
    :param guide_name: str
    :param guide_parent: str
    :param gizmo_shader: str
    :return: str
    """

    shaders = create_puppet_shaders()

    tp.Dcc.clear_selection()

    # Create main sphere gizmo
    new_guide = tp.Dcc.create_nurbs_sphere(name=guide_name, radius=0.115, construction_history=False)
    root_guide_shape = tp.Dcc.list_shapes(new_guide)[0]
    gizmo_shader = gizmo_shader if gizmo_shader and gizmo_shader in shaders else 'yellow'
    tp.Dcc.apply_shader(shaders[gizmo_shader], new_guide)
    tp.Dcc.add_float_attribute(new_guide, consts.PUPPET_GUIDE_SIZE_ATTR, default_value=1.0, min_value=0.0)
    tp.Dcc.add_bool_attribute(new_guide, consts.PUPPET_GUIDE_AXISES_ATTR, default_value=True, keyable=False)
    for axis in 'XYZ':
        scale_axis_attr = 'scale{}'.format(axis)
        tp.Dcc.unkeyable_attribute(new_guide, scale_axis_attr)
        tp.Dcc.hide_attribute(new_guide, scale_axis_attr)
        tp.Dcc.lock_attribute(new_guide, scale_axis_attr)
    tp.Dcc.unkeyable_attribute(new_guide, 'visibility')
    tp.Dcc.hide_attribute(new_guide,  'visibility')
    tp.Dcc.lock_attribute(new_guide,  'visibility')

    # Create axis
    axises = list()
    axises_shapes = list()
    for axis, color_name in zip(('x', 'y', 'z'), ('red', 'green', 'blue')):
        guide_axis_name = '{}_{}'.format(guide_name, axis)
        main_axis = tp.Dcc.create_nurbs_sphere(name=guide_axis_name, radius=0.2, construction_history=False)
        tp.Dcc.connect_attribute(new_guide, 'axises', main_axis, 'visibility')
        for sec_axis in 'XZ':
            tp.Dcc.set_attribute_value(main_axis, 'scale{}'.format(sec_axis), 0.23)
        tp.Dcc.set_attribute_value(main_axis, 'scaleY', 0.9)
        tp.Dcc.translate_node_in_object_space('{}.cv[4][0:7]'.format(guide_axis_name), (0, 0.02, 0.0), relative=True)
        tp.Dcc.translate_node_in_object_space('{}.cv[2][0:7]'.format(guide_axis_name), (0, -0.02, 0.0), relative=True)
        tp.Dcc.scale_node_in_object_space('{}.cv[4][0:7]'.format(guide_axis_name), (1.07, 1.07, 1.07), relative=True)
        tp.Dcc.scale_node_in_object_space('{}.cv[2][0:7]'.format(guide_axis_name), (1.07, 1.07, 1.07), relative=True)
        tp.Dcc.scale_node_in_object_space('{}.cv[3][0:7]'.format(guide_axis_name), (0.85, 0.85, 0.85), relative=True)
        tp.Dcc.scale_node_in_object_space('{}.cv[4:6][0:7]'.format(guide_axis_name), (0.5, 0.5, 0.5), relative=True)
        if axis == 'x':
            tp.Dcc.rotate_node_in_world_space(main_axis, (0, 0, -90), relative=True)
            tp.Dcc.translate_node_in_world_space(guide_axis_name, (0.32, 0, 0), relative=True)
        elif axis == 'y':
            tp.Dcc.translate_node_in_world_space(guide_axis_name, (0, 0.32, 0), relative=True)
        elif axis == 'z':
            tp.Dcc.rotate_node_in_world_space(main_axis, (90, 0, 0), relative=True)
            tp.Dcc.translate_node_in_world_space(guide_axis_name, (0, 0, 0.32), relative=True)
        tp.Dcc.apply_shader('{}_guide_matSG'.format(color_name), main_axis)
        tp.Dcc.move_pivot_to_zero(main_axis)
        tp.Dcc.set_attribute_value(main_axis, 'overrideEnabled', True)
        tp.Dcc.set_attribute_value(main_axis, 'overrideDisplayType', 2)
        axises.append(main_axis)
        axises_shapes.append(tp.Dcc.list_shapes(main_axis)[0])

    # Create orient locator
    root_orient_loc = tp.Dcc.create_locator(name='{}_orient'.format(guide_name))
    root_orient_shape = tp.Dcc.list_shapes(root_orient_loc)[0]
    for axis in 'XYZ':
        tp.Dcc.set_attribute_value(root_orient_loc, 'localScale{}'.format(axis), 0.1)
    tp.Dcc.set_attribute_value(root_orient_shape, 'visibility', False)
    tp.Dcc.set_parent(root_orient_loc, new_guide)

    # Create init locator
    root_init_loc = tp.Dcc.create_locator(name='{}_initLoc'.format(guide_name))
    for axis in 'XYZ':
        tp.Dcc.set_attribute_value(root_init_loc, 'localScale{}'.format(axis), 0.1)
    tp.Dcc.hide_node(root_init_loc)
    tp.Dcc.set_parent(root_init_loc, root_orient_loc)

    # Create catcher mesh
    # Create empty geometry
    catcher_xform = tp.Dcc.create_empty_mesh(mesh_name='{}_catcher'.format(guide_name))
    catcher_mesh = tp.Dcc.list_shapes(catcher_xform)[0]
    root_cluster, root_handle = tp.Dcc.create_cluster(
        [root_guide_shape, catcher_mesh] + axises_shapes,
        cluster_name='{}_cluster'.format(guide_name), relative=True)
    tp.Dcc.hide_node(catcher_xform)
    tp.Dcc.set_parent(catcher_xform, new_guide)
    tp.Dcc.set_attribute_value(root_cluster, 'relative', True)
    tp.Dcc.hide_node(root_handle)
    tp.Dcc.move_pivot_to_zero(root_handle)
    for axis in 'XYZ':
        shape = tp.Dcc.list_shapes(root_handle)[0]
        tp.Dcc.set_attribute_value(shape, 'origin{}'.format(axis), 0)
        tp.Dcc.connect_attribute(new_guide, consts.PUPPET_GUIDE_SIZE_ATTR, root_handle, 'scale{}'.format(axis))
    tp.Dcc.set_parent(root_handle, new_guide)

    for axis in axises:
        tp.Dcc.set_parent(axis, root_orient_loc)

    tp.Dcc.select_object(new_guide)

    if guide_parent and tp.Dcc.object_exists(guide_parent):
        tp.Dcc.set_parent(new_guide, guide_parent)

    return new_guide


def create_part():

    part_grp = tp.Dcc.create_empty_group(consts.PUPPET_PART_GROUP)
    guides_grp = tp.Dcc.create_empty_group(consts.PUPPET_GUIDES_GROUP, parent=part_grp)
    input_grp = tp.Dcc.create_empty_group(consts.PUPPET_INPUT_GROUP, parent=part_grp)
    tp.Dcc.hide_node(input_grp)
    system_grp = tp.Dcc.create_empty_group(consts.PUPPET_SYSTEM_GROUP, parent=part_grp)
    controls_grp = tp.Dcc.create_empty_group(consts.PUPPET_CONTROLS_GROUP, parent=part_grp)
    output_grp = tp.Dcc.create_empty_group(consts.PUPPET_OUTPUT_GROUP, parent=part_grp)
    output_joints_grp = tp.Dcc.create_empty_group(consts.PUPPET_OUTPUT_JOINTS_GROUP, parent=part_grp)
    tp.Dcc.clear_selection()

    # Create main guide
    main_guide = create_main_guide_control(parent=guides_grp)

    # Create selection groups (sets)
    tp.Dcc.create_selection_group(consts.PUPPET_MAIN_SET)
    tp.Dcc.create_selection_group(consts.PUPPET_PART_CONTROL_SET)
    tp.Dcc.add_node_to_selection_group(consts.PUPPET_PART_CONTROL_SET, consts.PUPPET_MAIN_SET)

    # Create guide
    create_guide(guide_name=consts.PUPPET_ROOT_GUIDE_NAME, guide_parent=main_guide)

    # Create root connector input
    root_cnt_input_locator = tp.Dcc.create_locator(name='root_connector')
    tp.Dcc.set_parent(root_cnt_input_locator, input_grp)
    for axis in 'XYZ':
        tp.Dcc.set_attribute_value(root_cnt_input_locator, 'localScale{}'.format(axis), 0.1)

    # Create root joint
    tp.Dcc.clear_selection()
    root_joint = tp.Dcc.create_joint(joint_name='root_outJoint')
    tp.Dcc.set_attribute_value(root_joint, 'radius', 0.5)
    tp.Dcc.set_parent(root_joint, output_joints_grp)

    tp.Dcc.select_object(main_guide)

    return main_guide


def create_connector(name='connector'):

    shaders = create_puppet_shaders()

    cylinder = tp.Dcc.create_nurbs_cylinder(name=name, radius=0.05, height_ratio=20, construction_history=False)
    tp.Dcc.apply_shader(shaders['black'], cylinder)
    tp.Dcc.translate_node_in_world_space(cylinder, (0, 0.5, 0))
    tp.Dcc.move_pivot_to_zero(cylinder)
    tp.Dcc.freeze_transforms(cylinder)
    tp.Dcc.convert_surface_to_bezier(cylinder, spans_u=1, degree_u=1, degree_v=3, construction_history=False)
    if tp.is_maya():
        import tpDcc.dccs.maya as maya
        maya.cmds.select('{}.cv[0][0:12]'.format(cylinder), replace=True)
        maya.cmds.move(-0.000750343, 0, 0, r=True, os=True, wd=True)
        maya.cmds.select('{}.cv[1][0:12]'.format(cylinder), replace=True)
        maya.cmds.move(-0.000750343, 0, 0, r=True, wd=True, os=True)
    tp.Dcc.translate_node_in_object_space('{}.cv[1][0:12]'.format(cylinder), (0, -1.0, 0.0), relative=True)
    tp.Dcc.set_attribute_value(cylinder, 'overrideEnabled', True)
    tp.Dcc.set_attribute_value(cylinder, 'overrideDisplayType', 2)
    tp.Dcc.set_attribute_value(cylinder, 'inheritsTransform', False)

    start_cluster, start_handle = tp.Dcc.create_cluster(
        '{}.cv[0][0:12]'.format(cylinder), cluster_name='connector_start_cluster', relative=False)
    tp.Dcc.hide_node(start_handle)
    end_cluster, end_handle = tp.Dcc.create_cluster(
        '{}.cv[1][0:12]'.format(cylinder), cluster_name='connector_end_cluster', relative=False)
    tp.Dcc.hide_node(end_handle)

    start_cluster_grp = tp.Dcc.group_node(start_handle, 'connector_start_cluster_group')
    end_cluster_grp = tp.Dcc.group_node(end_handle, 'connector_end_cluster_group')
    tp.Dcc.translate_node_in_world_space(end_cluster_grp, (0, 1.0, 0))

    tp.Dcc.create_aim_constraint(
        start_handle, end_cluster_grp, world_up_type=2, world_up_object=cylinder,
        aim_axis=(0.0, 1.0, 0.0), up_axis=(1.0, 0.0, 0.0), maintain_offset=False)
    tp.Dcc.create_aim_constraint(
        end_handle, start_cluster_grp, world_up_type=2, world_up_object=cylinder,
        aim_axis=(0.0, -1.0, 0.0), up_axis=(1.0, 0.0, 0.0), maintain_offset=False)

    return cylinder, start_cluster_grp, end_cluster_grp


def connect_guides(source=None, target=None, name=''):
    if not source:
        sel = tp.Dcc.selected_nodes()
        if len(sel) != 2:
            qtutils.warning_message('Select source and target nodes only!')
            return
        source, target = sel

    lines_group_name = '{}lines_group'.format(name)
    if not tp.Dcc.object_exists(lines_group_name):
        tp.Dcc.create_empty_group(lines_group_name)
        tp.Dcc.set_parent(lines_group_name, 'main_guide')

    connector_name = source.replace('guide', 'connector')
    new_connector, start_grp, end_grp = create_connector(name=connector_name)
    tp.Dcc.set_parent(new_connector, lines_group_name)
    tp.Dcc.set_parent(start_grp, source)
    tp.Dcc.set_parent(end_grp, target)
    tp.Dcc.reset_transform_attributes(start_grp)
    tp.Dcc.reset_transform_attributes(end_grp)



