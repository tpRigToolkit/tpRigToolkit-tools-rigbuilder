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

import os
import string
import logging

from tpPyUtils import folder, fileio, path as path_utils

from tpRigToolkit.tools.rigbuilder.core import consts, utils, data
from tpRigToolkit.tools.rigbuilder.data import node
from tpRigToolkit.tools.rigbuilder.objects import helpers, script

LOGGER = logging.getLogger('tpRigToolkit')


class RigObject(script.ScriptObject, object):

    DESCRIPTION = 'rig'
    NODE_FOLDER = consts.NODE_FOLDER

    def __init__(self, name=None):
        super(RigObject, self).__init__(name=name)

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def _get_invalid_code_names(self):
        invalid_folders = super(RigObject, self)._get_invalid_code_names()
        invalid_folders.append('{}.yml'.format(self.MANIFEST_FILE))

        return invalid_folders

    def get_code_file(self, name, basename=False):
        """
        Returns path to code file with the given name in the current object code folder
        :param name: str, name of the script we want to get
        :param basename: bool, Whether to return full path of code file or only the code file name
        :return: str
        """

        code_file = path_utils.join_path(self.get_code_path(), name)
        if not path_utils.is_dir(code_file):
            LOGGER.warning('Code File: "{}" does not exists!'.format(code_file))
            return

        code_name = path_utils.get_basename(code_file)
        if code_name == self.MANIFEST_FILE:
            code_name += '.{}.yml'
        else:
            code_name += '.yml'

        if not basename:
            code_name = path_utils.join_path(code_file, code_name)

        return code_name

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

        if script_count:
            for i in range(script_count):
                script_name = fileio.remove_extension(scripts_list[i])
                script_path = self.get_code_file(script_name)
                if not path_utils.is_file(script_path):
                    script_path_split = os.path.splitext(script_path)
                    script_path = '{}.yml'.format(script_path_split[0])
                    if not path_utils.is_file(script_path):
                        LOGGER.warning(
                            'Script "{}" does not exists in proper path: {}'.format(script_name, script_path))
                        continue
                    if scripts_list[i] in synced_scripts:
                        LOGGER.warning(
                            'Script "{}" is already synced. Do you have scripts with duplicates names?'.format(
                                script_name))
                        continue

                    synced_scripts.append(scripts_list[i])
                    synced_states.append(states[i])

                    remove_index = None
                    for i in range(len(code_folders)):
                        if code_folders[i] == script_name:
                            remove_index = i
                        if code_folders in synced_scripts:
                            if not code_folders[i].count('/'):
                                continue
                            common_path = path_utils.get_common_path(code_folders[i], script_name)
                            if common_path:
                                common_path_name = common_path + '.{}'.format('yml')
                                if common_path_name in synced_scripts:
                                    code_script = code_folders[i] + '.{}'.format('yml')
                                    synced_scripts.append(code_script)
                                    synced_states.append(False)
                                    remove_index = i
                    if remove_index:
                        code_folders.pop(remove_index)

        for code_folder in code_folders:
            code_folder += '.{}'.format('yml')
            if code_folder not in synced_scripts:
                synced_scripts.append(code_folder)
                synced_states.append(False)

        self.set_scripts_manifest(scripts_to_add=synced_scripts, states=synced_states)

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def is_rig(self):
        """
        Returns whether the rig is valid or not
        :return: bool
        """

        if not path_utils.is_dir(self.get_code_path()):
            if not path_utils.is_dir(self.get_code_path()):
                return False

        return True

    def get_parent_rig(self):
        """
        Returns parent rig of current one
        :return: variant, Rig or None
        """

        object_path = self.get_path()
        dir_name = path_utils.get_dirname(object_path)
        rig_inst = RigObject()
        rig_inst.set_directory(dir_name)

        if rig_inst.check():
            object_name = path_utils.get_basename(dir_name)
            object_dir = path_utils.get_dirname(dir_name)
            parent_object = RigObject(object_name)
            parent_object.set_directory(object_dir)
            LOGGER.debug('Parent Rig: {}'.format(parent_object.get_path()))
            return parent_object

        return None

    def get_relative_rig(self, relative_path):
        """
        Returns instance of an object in the relative path
        :param relative_path: str
        :return: object
        """

        object_path = self.get_path()
        if not object_path:
            return

        split_path = self.get_path().split('/')
        split_relative_path = relative_path.split('/')
        up_directory = 0
        new_sub_path = list()
        new_path = list()
        for sub_path in split_relative_path:
            if sub_path == '..':
                up_directory += 1
            else:
                new_sub_path.append(sub_path)

        if up_directory:
            new_path = split_path[:-up_directory]
            new_path += new_sub_path
        if up_directory == 0:
            new_path = split_path + split_relative_path
            new_path_test = string.join(new_path, '/')
            if not path_utils.is_dir(new_path_test):
                temp_split_path = list(split_path)
                temp_split_path.reverse()
                found_path = list()
                for i in range(len(temp_split_path)):
                    if temp_split_path[i] == split_relative_path[0]:
                        found_path = temp_split_path[i+1:]
                found_path.reverse()
                new_path = found_path + split_relative_path

        object_name = string.join([new_path[-1]], '/')
        object_directory = string.join(new_path[:-1], '/')

        object_inst = RigObject(object_name)
        object_inst.set_directory(object_directory)

        return object_inst

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

        # TODO: We should retrieve file path directly from data instance (not through data object)
        file_name = data_inst.get_file()

        if not self.is_in_manifest('{}.{}'.format(name, node.NodeData.get_data_extension())):
            self.set_scripts_manifest(
                ['{}.{}'.format(name, node.NodeData.get_data_extension())], append=True)

        return file_name
