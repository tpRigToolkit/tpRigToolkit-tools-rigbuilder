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

import string
import logging

from tpPyUtils import folder, path as path_utils

from tpRigToolkit.tools.rigbuilder.objects import helpers, script

LOGGER = logging.getLogger('tpRigToolkit')


class RigObject(script.ScriptObject, object):

    DESCRIPTION = 'rig'

    def __init__(self, name=None):
        super(RigObject, self).__init__(name=name)

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
