#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains constants definitions for tpRigToolkit.tools.rigbuilder
"""

from __future__ import print_function, division, absolute_import

from tpDcc.core import scripts

FOLDERS_PREFIX = '__'
FOLDERS_SUFFIX = '__'
BLUEPRINTS_FOLDER = '__blueprints__'
CODE_FOLDER = '__code__'
DATA_FOLDER = '__data__'
SUB_DATA_FOLDER = '__sub__'
NODE_FOLDER = '__node__'
BACKUP_FOLDER = '__backup__'
VERSIONS_FOLDER = '__versions__'
MANIFEST_FOLDER = 'manifest'
DATA_FILE = 'data'
VERSION_NAME = 'version'
MANIFEST_FILE = 'manifest'
ENABLE_FILE = 'enable'
SETTINGS_FILE_NAME = 'settings'
SETTINGS_FILE_EXTENSION = 'json'
OPTIONS_FILE_NAME = 'options'
OPTIONS_FILE_EXTENSION = 'json'
PROPERTIES_FILE_NAME = 'properties'
PROPERTIES_FILE_EXTENSION = 'json'

DEFAULT_SIDES = ['center', 'left', 'right']
DEFAULT_SIDE = 'center'
DEFAULT_MIRROR_SIDE = 'right'

PUPPET_TYPE = 'puppet'
PUPPET_MAIN_GROUP = 'main'
PUPPET_RIG_GROUP = 'rig'
PUPPET_GEO_GROUP = 'geo'
PUPPET_PART_GROUP = 'part'
PUPPET_PARTS_GROUP = 'parts'
PUPPET_SKELETON_GROUP = 'skeleton'
PUPPET_TWISTS_GROUP = 'twists'
PUPPET_PARTS_FOLDER = 'parts'
PUPPET_GUIDES_GROUP = 'guides'
PUPPET_INPUT_GROUP = 'input'
PUPPET_SYSTEM_GROUP = 'system'
PUPPET_CONTROLS_GROUP = 'controls'
PUPPET_OUTPUT_GROUP = 'output'
PUPPET_OUTPUT_JOINTS_GROUP = 'outputJoints'
PUPPET_NAME_ATTR = 'name'
PUPPET_PART_NAME_ATTR = 'partName'
PUPPET_VERSION_ATTR = 'version'
PUPPET_NODE_TYPE_ATTR = 'nodeType'
PUPPET_RIG_TYPE_ATTR = 'rig'
PUPPET_RIG_GUIDES_SIZE_ATTR = 'guidesSize'
PUPPET_RIG_JOINTS_SIZE_ATTR = 'jointsSize'
PUPPET_MAIN_SET = 'sets'
PUPPET_CONTROL_SET = 'controlSet'
PUPPET_PART_CONTROL_SET = 'partControlSet'
PUPPET_SKIN_JOINTS_SETS = 'skinJointsSet'
PUPPET_MODULES_SET = 'modules'
PUPPET_GUIDE_SIZE_ATTR = 'size'
PUPPET_GUIDE_AXISES_ATTR = 'axises'
PUPPET_GUIDE = 'guide'
PUPPET_MAIN_GUIDE_NAME = 'main'
PUPPET_ROOT_GUIDE_NAME = 'root'
PUPPET_MAIN_GUIDE = '{}_{}'.format(PUPPET_MAIN_GUIDE_NAME, PUPPET_GUIDE)
PUPPET_ROOT_GUIDE = '{}_{}'.format(PUPPET_ROOT_GUIDE_NAME, PUPPET_GUIDE)
PUPPET_MAIN_GUIDE_CLUSTER = '{}_cluster'.format(PUPPET_MAIN_GUIDE)
PUPPET_METADATA_FILE = 'metadata.yml'

class BuildLevel(object):
    """
    Class that defines all available build levels for build nodes
    """

    PRE = 'pre_build'
    MAIN = 'main_build'
    POST = 'post_build'


class DataTypes(object):
    """
    Class that defines all data types found in tpRigToolkit.tools.rigbuilder
    """

    Unknown = scripts.ScriptTypes.Unknown
    Python = scripts.ScriptTypes.Python
    Manifest = scripts.ScriptTypes.Manifest
    Node = 'script.node'
    Blueprint = 'Blueprint'
