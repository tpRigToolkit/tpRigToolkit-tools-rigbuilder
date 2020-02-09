#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains helpers functions for objects in tpRigToolkit.tools.rigbuilder
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import string
import logging
import __builtin__      # Not remove because its used to clean rig script builtins

import tpDccLib as tp
from tpPyUtils import folder, fileio, version, path as path_utils

from tpRigToolkit.tools import rigbuilder
from tpRigToolkit.tools.rigbuilder.core import consts

LOGGER = logging.getLogger('tpRigToolkit')


class ObjectsHelpers(object):

    @staticmethod
    def show_list_to_string(*args):
        """
        Converts given arguments into a string
        :param args: list(variant)
        :return: str
        """

        try:
            if args is None:
                return 'None'
            if not args:
                return ''

            new_args = list()
            for arg in args:
                if args is not None:
                    new_args.append(str(arg))
            args = new_args
            if not args:
                return ''

            string_value = string.join(args).replace('\n', '\t\n')
            if string_value.endswith('\t\n'):
                string_value = string_value[:-2]

            return string_value
        except RuntimeError as e:
            raise RuntimeError(e)

    @staticmethod
    def show(*args):
        """
        Helper function that prints given arguments into proper Dcc logs and temp logger
        :param args: list(variant)
        """

        try:
            string_value = ObjectsHelpers.show_list_to_string(*args)
            log_value = string_value.replace('\n', '\nLOG:\t\t')
            text = '\t\t{}'.format(string_value)
            print(text)
            log.record_temp_log(LOGGER.name, '\n{}'.format(log_value))
        except RuntimeError as e:
            text = '\t\tCould not show {}'.format(args)
            print(text)
            log.record_temp_log(LOGGER.name, '\n{}'.format(log_value))
            raise RuntimeError(e)

    @staticmethod
    def warning(*args):
        """
        Helper function that prints given arguments as warning into proper Dcc logs and temp logger
        :param args: list(variant)
        """

        try:
            string_value = ObjectsHelpers.show_list_to_string(*args)
            log_value = string_value.replace('\n', '\nLOG:\t\t')
            text = '[WARNING]\t{}'.format(string_value)
            if not tp.is_maya():
                print(text)
            else:
                tp.Dcc.warning('LOG: \t{}'.format(string_value))

            log.record_temp_log(LOGGER.name, '\n[WARNING]: {}'.format(log_value))
        except RuntimeError as e:
            raise RuntimeError(e)

    @staticmethod
    def error(*args):
        """
        Helper function that prints given arguments as error into proper Dcc logs and temp logger
        :param args: list(variant)
        """

        try:
            string_value = ObjectsHelpers.show_list_to_string(*args)
            log_value = string_value.replace('\n', '\nLOG:\t\t')
            text = '[ERROR]\t{}'.format(string_value)
            print(text)
            log.record_temp_log(LOGGER.name, '\n[ERROR]: {}'.format(log_value))
        except RuntimeError as e:
            raise RuntimeError(e)

    @staticmethod
    def copy(source, target, description=''):
        """
        Copis given file or files and creates a new version of the file with the given description
        :param source: str, source file or folder we want to copy
        :param target: str, destination file or folder we want to copy into
        :param description: str, description of the new version
        """

        is_source_a_file = path_utils.is_file(source)

        if is_source_a_file:
            copied_path = fileio.copy_file(source, target)
        else:
            if not path_utils.exists(source):
                LOGGER.info('Nothing to copy: {}\t\tData was probably created but not saved yet.'.format(
                    path_utils.get_dirname(is_source_a_file)))
                return
            if path_utils.exists(target):
                folder.delete_folder(target)
            copied_path = folder.copy_folder(source, target)

        if not copied_path:
            LOGGER.warning('Error copying {}\t to\t{}'.format(source, target))
            return

        if copied_path > -1:
            LOGGER.info('Finished copying {} from {} to {}'.format(description, source, target))
            version_file = version.VersionFile(copied_path)
            version_file.save('Copied from {}'.format(source))


class ScriptHelpers(ObjectsHelpers, object):

    @staticmethod
    def get_code_builtins(script_object):
        """
        Returns all current code builtins of the given script object
        :param script_object: ScriptObject
        :return: dict
        """

        builtins = {'script_object': script_object, 'show': show, 'warning': warning}
        if tp.is_maya():
            import maya.cmds as cmds
            import pymel.all as pymel
            maya_builtins = {'cmds': cmds, 'mc': cmds, 'pymel': pymel, 'pm': pymel}
            for builtin in maya_builtins:
                builtins[builtin] = maya_builtins[builtin]

        return builtins

    @staticmethod
    def setup_code_builtins(script_object):
        """
        Setup given rig builtins
        :param script_object: ScriptObject
        """

        builtins = ScriptHelpers.get_code_builtins(script_object)
        for builtin in builtins:
            try:
                exec ('del(__builtin__.%s)' % builtin)
            except Exception:
                pass
            builtin_value = builtins[builtin]
            exec '__builtin__.%s = builtin_value' % builtin

    @staticmethod
    def reset_code_bultins(script_object):
        """
        Reset given rig builtins
        :param script_object: ScriptObject
        """

        builtins = ScriptHelpers.get_code_builtins(script_object)
        for builtin in builtins:
            try:
                exec ('del(__builtin__.{}'.format(builtin))
            except Exception:
                pass


class RigHelpers(ScriptHelpers, object):

    @staticmethod
    def is_rig(directory):
        """
        Returns whether the given directory contains a valid build object or not
        :param directory: str, directory to check if it contains objects or not
        :return: bool
        """

        if not directory or not path_utils.is_dir(directory):
            return False

        code_path = path_utils.join_path(directory, consts.CODE_FOLDER)
        if not path_utils.is_dir(code_path):
            return False

        return True

    @staticmethod
    def get_rig(directory):
        """
        Returns object if the given directory is a valid one
        :param directory: str
        :return: object or not
        """

        from tpRigToolkit.tools.rigbuilder.objects import rig

        if not RigHelpers.is_rig(directory):
            return

        new_object = rig.RigObject(os.path.basename(directory))
        new_object.set_directory(os.path.dirname(directory))

        return new_object

    @staticmethod
    def find_rigs(directory=None, return_also_non_objects_list=False):
        """
        Will try to find the objects in the given directory
        If no directory is given, it will search in teh current working directory
        :param directory: str, directory to search for objects
        :param return_also_non_objects_list: bool
        :return: list<str>, objects in the given directory
        """

        if not directory:
            directory = folder.get_current_working_directory()

        LOGGER.info('Finding rigs on "{}"'.format(directory))

        found = list()
        non_found = list()
        for root, dirs, files in os.walk(directory):
            for d in dirs:
                try:
                    full_path = path_utils.join_path(root, d)
                except Exception:
                    pass
                if RigHelpers.is_rig(full_path):
                    found.append(d)
                    continue
                elif return_also_non_objects_list:
                    if not d.startswith(consts.FOLDERS_PREFIX) and not d.endswith(
                            consts.FOLDERS_SUFFIX) and d != 'Trash':
                        non_found.append(d)
            break

        if not return_also_non_objects_list:
            return found
        else:
            return [found, non_found]

    @staticmethod
    def get_unused_rig_name(directory=None, name=None):
        """
        Will try to find a rig name in the given directory
        It will increment the name to rug1 and beyond until it finds a unique name
        If no directory is supplied, it will search the current working directory
        :param directory: str, directory to search for tasks
        :param name: str, name to give the task
        :return: str, unique rig name
        """

        from tpRigToolkit.tools.rigbuilder.objects import rig

        if directory is None:
            directory = folder.get_current_working_directory()
        rigs = RigHelpers.find_rigs(directory=directory)
        if name is None:
            name = rig.RigObject.DESCRIPTION
        new_name = name
        not_name = True
        index = 1
        while not_name:
            if new_name in rigs:
                new_name = name + str(index)
                index += 1
                not_name = True
            else:
                not_name = False
            if index > 1000:
                break

        return new_name

    @staticmethod
    def copy_rig(source_rig, target_rig=None):
        """
        Copies given source rig into given target rig
        If no target rig is given, the target rig will be set to the directory where the source rig is located
        If exists a rig with the same target name, the name will be incremented
        :param source_rig: Rig
        :param target_rig: Rig
        :return:
        """

        from tpRigToolkit.tools.rigbuilder.objects import rig

        if target_rig:
            parent = target_rig.get_parent_rig()
            if parent:
                if parent.get_path() == source_rig.get_path():
                    error('Cannot paste parent under child!')
                    return

        sub_folders = source_rig.get_sub_rigs()
        source_name = source_rig.get_name().split('/')[-1]

        if not target_rig:
            target_rig = rig.Rig()
            target_rig.set_directory(source_rig.directory)
            target_rig.set_library(source_rig.library())

        if not osplatform.get_permission(target_rig.get_path()):
            warning('Could not get permission in directory: {} Copy operation aborted!'.format(target_rig.get_path()))
            return

        if source_rig._name == target_rig._name and source_rig._directory == target_rig._directory:
            parent_task = target_rig.get_parent_rig()
            if parent_task:
                target_rig = parent_task

        rig_path = target_rig.get_path()
        new_rig_name = get_unused_rig_name(rig_path, source_name)
        new_rig = target_rig.add_part(new_rig_name)

        data_folders = source_rig.get_data_folders()
        code_folders = source_rig.get_code_folders()
        settings = source_rig.get_setting_names()

        for data_folder in data_folders:
            RigHelpers.copy_rig_data(source_rig, new_rig, data_folder)

        scripts_manifest_found = False
        if '{}'.format(rig.RigObject.MANIFEST_FILE) in code_folders:
            code_folders.remove('{}'.format(rig.RigObject.MANIFEST_FILE))
            scripts_manifest_found = True

        for code_folder in code_folders:
            copy_rig_code(source_rig, new_rig, code_folder)

        for sub_folder in sub_folders:
            sub_rig = new_rig.get_sub_rig(sub_folder)
            source_sub_rig = source_rig.get_sub_rig(sub_folder)
            if not sub_rig.is_task():
                RigHelpers.copy_rig(source_sub_rig, new_rig)

        if scripts_manifest_found:
            RigHelpers.copy_rig_code(source_rig, new_rig, '{}'.format(rig.Rig.MANIFEST_FILE_NAME))

        for setting in settings:
            RigHelpers.copy_rig_setting(source_rig, new_rig, setting)

        return new_rig

    @staticmethod
    def copy_rig_into(source_rig, target_rig, merge_sub_folders=False):
        """
        Copies given source rig into given target rig
        :param source_rig: Rig
        :param target_rig: Rig
        :param merge_sub_folders: bool
        :return:
        """

        from tpRigToolkit.tools.rigbuilder.objects import rig

        if not target_rig or not target_rig.is_rig():
            return

        if source_rig._name == target_rig._name and source_rig._directory == target_rig._directory:
            warning('Source and target rigs are the same. Skipping merge.')
            return

        sub_folders = source_rig.get_sub_rigs()
        source_name = source_rig.get_name().split('/')[-1]

        data_folders = source_rig.get_data_folders()
        code_folders = source_rig.get_code_folders()
        settings = source_rig.get_setting_names()

        for data_folder in data_folders:
            RigHelpers.copy_rig_data(source_rig, target_rig, data_folder)

        scripts_manifest_found = False
        if '{}'.format(rig.RigObject.MANIFEST_FILE) in code_folders:
            code_folders.remove('{}'.format(rig.RigObject.MANIFEST_FILE))
            scripts_manifest_found = True

        for code_folder in code_folders:
            RigHelpers.copy_rig_code(source_rig, target_rig, code_folder)

        if sub_folders and merge_sub_folders:
            for sub_folder in sub_folders:
                sub_rig = target_rig.get_sub_rig(sub_folder)
                if sub_rig:
                    if not sub_rig.is_rig():
                        sub_rig.create()

                    source_sub_rig = source_rig.get_sub_rig(sub_folder)
                    RigHelpers.copy_rig(source_sub_rig, sub_rig)

        if scripts_manifest_found:
            RigHelpers.copy_rig_code(source_rig, target_rig, '{}'.format(rig.Rig.MANIFEST_FILE_NAME))

        for setting in settings:
            RigHelpers.copy_rig_setting(source_rig, target_rig, setting)

    @staticmethod
    def copy_rig_data(source_rig, target_rig, data_name, replace=False, sub_folder=None):
        """
        Copy given data folder from source rig into target rig
        :param source_rig: Rig
        :param target_rig: Rig
        :param data_name: str, name of the data folder we want to copy
        :param replace: bool, Whether to replace the data in the target task or just version it up
        :param sub_folder: srt, name of the data sub folder to copy
        :return:
        """

        from tpRigToolkit.tools.rigbuilder.core import data

        if not target_rig.is_rig():
            return

        data_type = source_rig.get_data_type(data_name)

        if target_rig.is_data_folder(data_name, sub_folder):
            data_folder_path = target_rig.get_data_folder(data_name, sub_folder)
            if replace:
                other_data_type = target_rig.get_data_type(data_name)
                if data_type != other_data_type:
                    target_rig.delete_data(data_name, sub_folder)
                    RigHelpers.copy_rig_data(source_rig, target_rig, data_name, sub_folder)
                    return
        else:
            data_folder_path = target_rig.create_data(data_name, data_type, sub_folder)

        data_path = source_rig.get_data_path()
        data_folder = data.ScriptFolder(data_name, data_path, data_path=rigbuilder.get_data_files_directory())
        data_inst = data_folder.get_folder_data_instance()
        if not data_inst:
            return

        file_path = data_inst.get_file_direct(sub_folder)
        if file_path:
            file_name = path.get_basename(file_path)
            target_dir = path.join_path(data_folder_path, file_name)
            if not path_utils.is_dir(data_folder_path):
                folder.create_folder(data_folder_path)
            if sub_folder:
                sub_path = target_rig.create_sub_folder(data_name, sub_folder)
                target_dir = path_utils.join_path(sub_path, file_name)

            ObjectsHelpers.copy(file_path, target_dir, data_name)

            if not sub_folder:
                sub_folders = source_rig.get_data_sub_folder_names(data_name)
                for sub_folder in sub_folders:
                    RigHelpers.copy_rig_data(source_rig, target_rig, data_name, replace, sub_folder)

    @staticmethod
    def copy_rig_code(source_rig, target_rig, code_name, replace=False):
        """
        Copy given source folder from source task into target rig
        :param source_rig: Rig
        :param target_rig: Rig
        :param code_name: str, name of the code folder we want to copy
        :param replace: bool, Whether to replace the data in the target task or just version it up
        """

        from tpRigToolkit.tools.rigbuilder.core import data

        if not code_name:
            return

        data_type = source_rig.get_code_type(code_name)
        if not data_type:
            LOGGER.warning('No data type found for: {}'.format(code_name))
            return

        if target_rig.is_code_folder(code_name):
            code_folder_path = target_rig.get_code_folder(code_name)
            code_file_path = target_rig.get_code_file(code_name)
            if not code_file_path:
                LOGGER.warning('Could not find code: {}'.format(code_name))
                return

            code_file = path_utils.get_basename(code_file_path)
            code_folder_path = path_utils.join_path(code_folder_path, code_file)
            other_data_type = target_rig.get_code_type(code_name)
            if data_type != other_data_type:
                if replace:
                    target_rig.delete(code_name)
                    RigHelpers.copy_rig_code(source_rig, target_rig, code_name)
                    return
        else:
            code_folder_path = target_rig.create_code(code_name, scripts.ScriptTypes.Python)

        code_path = source_rig.get_code_path()
        data_folder = data.ScriptFolder(code_name, code_path, data_path=rigbuilder.get_data_files_directory())
        data_inst = data_folder.get_folder_data_instance()
        if not data_inst:
            return

        file_path = data_inst.get_file()
        copied_path = None
        target_dir = ''
        if file_path:
            target_dir = code_folder_path
            target_path = target_rig.get_code_path()
            data.ScriptFolder(code_name, target_path, data_path=rigbuilder.get_data_files_directory())
            if path_utils.is_file(file_path):
                copied_path = fileio.copy_file(file_path, target_dir)
            elif path_utils.is_dir(file_path):
                copied_path = folder.copy_folder(file_path, target_dir)

            if copied_path:
                data_version = version.VersionFile(file_path=copied_path)
                data_version.save('Copied from {}'.format(file_path))
            else:
                LOGGER.warning('Error copying {}\t to\t {}'.format(file_path, target_dir))
                return

        LOGGER.info('Finished copying code from {} to {}'.format(file_path, target_dir))

    @staticmethod
    def copy_rig_setting(source_rig, target_rig, setting_name):
        """
        Copy setting from one rig to another
        :param source_rig: Rig
        :param target_rig: Rig
        :param setting_name: str, name of the setting we want to copy
        """

        file_path = source_rig.get_setting_file(setting_name)
        if not file_path:
            return

        target_path = target_rig.get_path()
        target_file_path = target_rig.get_setting_file(setting_name)
        if path.is_file(target_file_path):
            file_name = path.get_basename(target_file_path)
            file_dir = path.get_dirname(target_file_path)
            fileio.delete_file(file_name, file_dir)

        fileio.copy_file(file_path, target_path)
        source_path = source_rig.get_path()

        LOGGER.info('Finished copying settings from {}'.format(source_path))
