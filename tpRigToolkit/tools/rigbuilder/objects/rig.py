#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains rig object implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import logging

from tpDcc.libs.python import folder, fileio, path as path_utils

from tpRigToolkit.tools.rigbuilder.core import consts, utils, data
from tpRigToolkit.tools.rigbuilder.scripts import node
from tpRigToolkit.tools.rigbuilder.objects import helpers, script

LOGGER = logging.getLogger('tpRigToolkit')


class RigObject(script.ScriptObject, object):

    DESCRIPTION = 'rig'
    NODE_FOLDER = consts.NODE_FOLDER
    ENABLE_FILE = consts.ENABLE_FILE
    SCRIPT_EXTENSION = 'yml'

    def __init__(self, name=None):
        super(RigObject, self).__init__(name=name)

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def sync(self):
        scripts_list, states = self.get_scripts_manifest()
        synced_scripts = list()
        synced_states = list()

        script_count = 0
        if scripts_list:
            script_count = len(scripts_list)
        code_folders = self.get_code_folders()
        if not script_count and not code_folders:
            return

        extension = self.SCRIPT_EXTENSION
        if not extension.startswith('.'):
            extension = '.{}'.format(extension)

        for i in range(script_count):
            script_name = fileio.remove_extension(scripts_list[i])
            script_path = self.get_code_file(script_name)
            if not path_utils.exists(script_path) or scripts_list[i] in synced_scripts:
                continue

            synced_scripts.append(scripts_list[i])
            synced_states.append(states[i])

            remove_index = None
            for i in range(len(code_folders)):
                if code_folders[i] == script_name:
                    remove_index = i
                    break
                if code_folders in synced_scripts:
                    if not code_folders[i].count('/'):
                        continue
                    common_path = path_utils.get_common_path(code_folders[i], script_name)
                    if common_path:
                        common_path_name = common_path + extension
                        if common_path_name in synced_scripts:
                            code_script = code_folders[i] + extension
                            synced_scripts.append(code_script)
                            synced_states.append(False)
                            remove_index = i
                            break
            if remove_index:
                code_folders.pop(remove_index)

        for code_folder in code_folders:
            code_folder += extension
            if code_folder not in synced_scripts:
                synced_scripts.append(code_folder)
                synced_states.append(False)

        self.set_scripts_manifest(scripts_to_add=synced_scripts, states=synced_states)

    def _reset(self):
        """
        Internal function resets all rig variables
        """

        super(RigObject, self)._reset()

        self._parts = list()

    def _get_invalid_code_names(self):
        invalid_folders = super(RigObject, self)._get_invalid_code_names()
        invalid_folders.append('{}.yml'.format(self.MANIFEST_FILE))

        return invalid_folders

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def is_enabled(self):
        """
        Returns whether or not this rig is enabled
        :return: bool
        """

        rig_path = self.get_path()
        enable_path = path_utils.join_path(rig_path, consts.ENABLE_FILE)
        if path_utils.exists(enable_path):
            return True

        return False

    def set_enabled(self, flag):
        """
        Sets whether or not this rig is enabled
        :param flag: bool
        """

        rig_path = self.get_path()
        if flag:
            fileio.create_file(self.ENABLE_FILE, rig_path)
        else:
            fileio.delete_file(self.ENABLE_FILE, rig_path, show_warning=False)

    def is_rig(self):
        """
        Returns whether the rig is valid or not
        :return: bool
        """

        if not path_utils.is_dir(self.get_code_path()):
            if not path_utils.is_dir(self.get_code_path()):
                return False

        return True

    def get_empty_rig(self, path=None):
        """
        Returns empty rig
        :param path: str
        :return: RigObject
        """

        rig = RigObject()
        rig.set_directory(path)

        return rig

    def get_parent_rig(self):
        """
        Returns parent rig of current one
        :return: variant, Rig or None
        """

        name, path = self._get_parent_rig_path()
        if not name:
            return

        parent_rig = RigObject()
        parent_rig.set_directory(path)

        if self._data_override:
            name, path = self._get_parent_rig_path(from_override=True)
            if name:
                override_rig = RigObject(name)
                override_rig.set_directory(path)
                override_rig.set_data_override(override_rig)

        LOGGER.info('Parent rig: {}'.format(parent_rig.get_path()))

        return parent_rig

    def get_relative_rig(self, relative_path):
        """
        Returns instance of an object in the relative path
        If a name with no backlash is given, this will return any matching rig parented directly under the current rig
        A relative path like, '../test' or '../..º/test' can be used (being .. a folder above the current rig)
        :param relative_path: str
        :return: object
        """

        rig_name, rig_directory = self._get_relative_object_path(relative_path)
        if not rig_name and rig_directory:
            rig_name = path_utils.get_basename(rig_directory)
            rig_directory = path_utils.get_dirname(rig_directory)
        if not rig_name and not rig_directory:
            return

        rig_object = RigObject(rig_name)
        rig_object.set_directory(rig_directory)

        if self._data_override:
            override_rig_name, override_rig_directory = self._get_relative_object_path(relative_path=relative_path, from_override=True)
            if override_rig_name:
                override_rig = RigObject(override_rig_name)
                override_rig.set_directory(override_rig_directory)
                rig_object.set_data_override(override_rig)

        return rig_object

    def get_sub_rigs(self):
        """
        Returns the objects names found directly under the current object
        :return: list(str)
        """

        object_path = self.get_path()
        found = helpers.RigHelpers.find_rigs(object_path)

        return found

    def get_sub_rig(self, rig_name):
        """
        Returns sub rig if there is one that matches given name
        :param rig_name: str, name of a child rig
        :return: Rig
        """

        rig_inst = RigObject(rig_name)
        rig_inst.set_directory(self.get_path())

        return rig_inst

    def get_sub_rig_by_index(self, index):
        """
        Returns sub rig instance in given index if exists
        :param index: int
        :return: Rig
        """

        found = self.get_sub_rigs()
        if index < len(found):
            sub_rig = RigObject(found[index])
            sub_rig.set_directory(self.get_path())
            return sub_rig

        return None

    def get_sub_rig_count(self):
        """
        Returns the number of sub rigs under the current one
        :return: int
        """

        found = self.get_sub_rigs()
        if found:
            return len(found)

    def add_part(self, name):
        """
        Adsd given part to the rig
        :param name: str
        :return: Rig, instance of the given part
        """

        part_rig = RigObject(name)
        if self._name:
            path = path_utils.join_path(self._directory, self._name)
        else:
            path = self._directory

        part_rig.set_directory(path)
        part_rig.create()

        return part_rig

    def has_sub_parts(self):
        """
        Returns whether current rig has sub parts or not
        :return: bool
        """

        rig_path = self.get_path()
        if not rig_path:
            return False

        files = folder.get_folders(rig_path)
        if not files:
            return False

        for filename in files:
            file_path = path_utils.join_path(rig_path, filename)
            if helpers.RigHelpers.is_rig(file_path):
                return True

        return False

    def get_non_rig_parts(self):
        """
        Returns all non rig parts of current rig
        :return: list(str)
        """

        found = list()

        rig_path = self.get_path()
        if not rig_path:
            return found

        folders = folder.get_folders(rig_path)
        for f in folders:
            full_path = path_utils.join_path(rig_path, f)
            if not helpers.RigHelpers.is_rig(full_path):
                continue
            found.append(full_path)

        return found

    # ================================================================================================
    # ======================== NODE
    # ================================================================================================

    def create_build_node(self, builder_node, name, description=None, unique_name=True):
        """
        Creates a new node for current rig
        :param builder_node:
        :param name:
        :param description:
        :param unique_name:
        :return:
        """

        code_path = self.get_code_path()
        if not code_path:
            return

        if unique_name:
            test_path = path_utils.join_path(code_path, name)
            if path_utils.is_dir(test_path):
                test_path = path_utils.unique_path_name(test_path)
                name = path_utils.get_basename(test_path)

        node_folder = data.ScriptFolder(name, code_path, data_path=utils.get_data_files_directory())
        data_type = consts.DataTypes.Node
        node_folder.set_data_type(data_type)
        data_inst = node_folder.get_folder_data_instance()
        if not data_inst:
            LOGGER.warning('Impossible to create node of type {} because that data is not supported!'.format(data_type))
            return

        data_inst.create(builder_node)

        # # TODO: We should retrieve file path directly from data instance (not through data object)
        file_name = data_inst.get_file()

        if not self.is_in_manifest('{}.{}'.format(name, node.NodeData.get_data_extension())):
            self.set_scripts_manifest(
                ['{}.{}'.format(name, node.NodeData.get_data_extension())], append=True)

        return file_name

    # ================================================================================================
    # ======================== INTERNAL
    # ================================================================================================

    def _get_parent_rig_path(self, from_override=False):
        if not from_override:
            object_path = self.get_path()
        else:
            object_path = self._get_override_path()

        dir_name = path_utils.get_dirname(object_path)

        rig_object = RigObject()
        rig_object.set_directory(dir_name)
        if rig_object.is_rig():
            basename = path_utils.get_basename(dir_name)
            path = path_utils.get_dirname(dir_name)
            return basename, path
        else:
            return None, None

