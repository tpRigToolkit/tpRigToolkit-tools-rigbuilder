#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains script object implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import string
import logging
import traceback

from tpDccLib.core import scripts
from tpPyUtils import folder, fileio, version, path as path_utils, name as name_utils

from tpRigToolkit.tools import rigbuilder
from tpRigToolkit.tools.rigbuilder.core import consts, data
from tpRigToolkit.tools.rigbuilder.objects import build

LOGGER = logging.getLogger('tpRigToolkit')


class ScriptObject(build.BuildObject, object):

    CODE_FOLDER = consts.CODE_FOLDER
    MANIFEST_FILE = consts.MANIFEST_FILE

    def __init__(self, name):
        super(ScriptObject, self).__init__(name=name)

        self._external_code_paths = list()
        self._runtime_values = dict()
        self._runtime_globals = dict()

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def check(self):
        """
        Overrides base BuildObject check function
        Returns whether or not current object is valid or not
        :return: bool
        """

        if not path_utils.is_dir(self.get_code_path()):
            if not path_utils.is_dir(self.get_code_path()):
                return False

        return True

    def _create_folder(self):
        """
        Overrides base BuildObject _create_folder function
        Internal function that creates the folder of the rig
        :return: str, path where object is created
        """

        script_path = folder.create_folder(self._name, self._directory)
        if not script_path or not path_utils.is_dir(script_path):
            return script_path

        folder.create_folder(self.DATA_FOLDER_NAME, script_path)
        code_folder = folder.create_folder(self.CODE_FOLDER, script_path)
        folder.create_folder(self.BACKUP_FOLDER, script_path)
        manifest_folder = path_utils.join_path(code_folder, self.MANIFEST_FOLDER)
        if not path_utils.is_dir(manifest_folder):
            self.create_code(self.MANIFEST_FILE, scripts.ScriptManifestData.get_data_type())

        return script_path

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def set_external_code_library(self, external_directory):
        """
        Sets the external application used to edit scripts
        :param external_directory: str
        """

        external_directory = python.force_list(external_directory)
        self._external_code_paths = external_directory

    # ================================================================================================
    # ======================== MANIFEST
    # ================================================================================================

    def get_scripts_manifest_folder(self):
        """
        Returns path where scripts manifest file is located
        :return: str
        """

        code_path = self.get_code_path()
        manifest_path = path_utils.join_path(code_path, self.MANIFEST_FILE)
        if not path_utils.is_dir(manifest_path):
            try:
                self.create_code(self.MANIFEST_FILE, consts.DataTypes.Manifest)
            except RuntimeError:
                LOGGER.warning(
                    'Could not create script manifest file in folder: {} | {}'.format(
                        manifest_path, traceback.format_exc()))

        return manifest_path

    def get_scripts_manifest_file(self):
        """
        Returns path to the script manifest file
        :return: str
        """

        manifest_path = self.get_scripts_manifest_folder()
        manifest_file = path_utils.join_path(
            manifest_path, '{}.{}'.format(self.MANIFEST_FILE, scripts.ScriptManifestData.get_data_extension()))
        if not path_utils.is_file(manifest_file):
            try:
                self.create_code(self.MANIFEST_FILE, scripts.ScriptManifestData.get_data_extension())
            except RuntimeError:
                LOGGER.warning(
                    'Could not create script manifest file: {} | {}'.format(manifest_file, traceback.format_exc()))

        return manifest_file

    def get_scripts_manifest(self, manifest_file=None):
        """
        Returns a list of scripts and states on the current scripts manifest file
        :param manifest_file: str,
        :return: tuple<list, list>
        """

        if not manifest_file:
            manifest_file = self.get_scripts_manifest_file()
        if not path_utils.is_file(manifest_file):
            return None, None

        lines = fileio.get_file_lines(manifest_file)
        if not lines:
            return None, None

        scripts = list()
        states = list()

        for l in lines:
            if not l:
                continue
            states.append(False)
            split_line = l.split()
            if len(split_line):
                script_name = string.join(split_line[:-1])
                scripts.append(script_name)

            if len(split_line) >= 2:
                state = eval(split_line[-1])
                states[-1] = state

        return scripts, states

    def set_scripts_manifest(self, scripts_to_add, states=None, append=False):
        """
        Sets the scripts and their states on the scripts manifest file
        :param scripts: list<str>, list of scripts to add to the manifest
        :param states: list<str>, list of states for the manifest scripts
        :param append: bool, Whether to add the scripts to the end of the manifest or replace existing manifest content
        """

        if states is None:
            states = list()

        manifest_file = self.get_scripts_manifest_file()
        lines = list()
        script_count = len(scripts_to_add)
        state_count = 0
        if states:
            state_count = len(states)

        for i in range(script_count):
            if scripts_to_add[i] == '{}.{}'.format(self.MANIFEST_FILE, scripts.ScriptPythonData.get_data_extension()):
                continue
            if i > state_count - 1:
                state = False
            else:
                state = states[i]

            line = '{} {}'.format(scripts_to_add[i], state)
            lines.append(line)

        fileio.write_lines(manifest_file, lines, append=append)

    def get_scripts_from_manifest(self, basename=True):
        """
        Returns script files of the manifest
        :param basename: str, Whether to return the full path to the script file or just the script name
        :return: list<str>
        """

        manifest_file = self.get_scripts_manifest_file()
        if not manifest_file:
            return
        if not path_utils.is_file(manifest_file):
            return

        script_files = self.get_code_files(basename=False)
        scripts, states = self.get_scripts_manifest()

        if basename:
            return scripts
        else:
            found = list()
            for script in scripts:
                if script.count('/') > 0:
                    script_dir = path_utils.get_dirname(script)
                    script_name = path_utils.get_basename(script)
                    sub_name = path_utils.get_basename(basename, with_extension=False)
                    script = path_utils.join_path(script_dir, sub_name)
                    script = path_utils.join_path(script, script_name)

                for f in script_files:
                    if not f:
                        continue
                    if f.endswith(script):
                        found.append(f)
                        break

            return found

    def is_in_manifest(self, entry):
        """
        Checks whether the given script name is stored in the scripts manifest file or not
        :param entry: str, name of script to check
        :return: bool
        """

        manifest_file = self.get_scripts_manifest_file()
        lines = fileio.get_file_lines(manifest_file)
        for l in lines:
            split_line = l.split(' ')
            if split_line[0] == entry:
                return True

        return False

    def get_scripts_manifest_dict(self, manifest_file=None):
        """
        Returns scripts manifest dicitonary
        :param manifest_file: variant, str or None
        :return: dict
        """

        if not manifest_file:
            manifest_file = self.get_scripts_manifest_file()

        manifest_dict = dict()

        if not path_utils.is_file(manifest_file):
            return manifest_dict
        lines = fileio.get_file_lines(manifest_file)
        if not lines:
            return manifest_dict

        for line in lines:
            script_name = None
            if not line:
                continue
            split_line = line.split()
            if len(split_line):
                script_name = string.join(split_line[:-1])
                manifest_dict[script_name] = False
            if len(split_line) >= 2 and script_name:
                state = eval(split_line[-1])
                manifest_dict[script_name] = state

        return manifest_dict

    def get_manifest_history(self):
        """
        Returns version history file associated to the scripts manifest file
        :return: version.VersionFile
        """

        manifest_file = self.get_scripts_manifest_file()
        version_file = version.VersionFile(manifest_file)

        return version_file

    def sync_scripts(self):
        """
        Syncs scripts manifest file with the scripts that are located in the code folder of the current object in disk
        """

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
                    LOGGER.warning('Script "{}" does not exists in proper path: {}'.format(script_name, script_path))
                    continue
                if scripts_list[i] in synced_scripts:
                    LOGGER.warning(
                        'Script "{}" is already synced. Do you have scripts with duplicates names?'.format(script_name))
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
                            common_path_name = common_path + '.{}'.format(scripts.ScriptPythonData.get_data_extension())
                            if common_path_name in synced_scripts:
                                print(code_folders[i])
                                code_script = code_folders[i] + '.{}'.format(
                                    scripts.ScriptPythonData.get_data_extension())
                                synced_scripts.append(code_script)
                                synced_states.append(False)
                                remove_index = i
                if remove_index:
                    code_folders.pop(remove_index)

        for code_folder in code_folders:
            code_folder += '.{}'.format(scripts.ScriptPythonData.get_data_extension())
            if code_folder not in synced_scripts:
                synced_scripts.append(code_folder)
                synced_states.append(False)

        self.set_scripts_manifest(scripts_to_add=synced_scripts, states=synced_states)

    # ================================================================================================
    # ======================== CODE
    # ================================================================================================

    def get_code_path(self):
        """
        Returns path where object code folder is located
        :return: str
        """

        return self._get_path(self.CODE_FOLDER)

    def get_code_folder(self, name):
        """
        Returns a path to the code folder with the given name
        :param name: str, name of a code folder in the rig
        :return: str
        """

        code_folder = path_utils.join_path(self.get_code_path(), name)
        if path_utils.is_dir(code_folder):
            return code_folder

        return None

    def is_code_folder(self, name):
        """
        Returns whether the given folder name is a object code folder
        :param name: str, name of folder
        :return: bool
        """

        code_path = self.get_code_folder(name)
        if not code_path:
            return False
        if path_utils.is_dir(code_path):
            return True

        return False

    def get_code_folders(self, code_name=None):
        """
        Returns a list of code folder names in the current rig
        :param code_name: str
        :return: list<str>
        """

        code_directory = self.get_code_path()
        if code_name:
            code_directory = path_utils.join_path(code_directory, code_name)

        return self._get_folders_without_prefix_suffix(code_directory, recursive=True)

    def get_top_level_code_folders(self):
        """
        Returns the highest level folders in the code folder path
        :return: str
        """

        code_folders = self.get_code_folders()
        found = list()
        for f in code_folders:
            if f.count('/') > 1:
                continue
            found.append(f)

        return found

    def get_code_children(self, code_name):
        """
        Returns a list of codes in childrens
        :param code_name: str
        :return: list(str)
        """

        found = list()

        scripts, states = self.get_scripts_manifest()
        for script in scripts:
            if script.startswith(code_name):
                found.append(script)

        return found

    def get_code_type(self, name):
        """
        Returns the code type name of the code folder with the given name
        :param name: str, name of a code folder in the rig
        :return: str
        """

        file_path = path_utils.join_path(self.get_code_path(), name)
        python_file = path_utils.join_path(
            file_path, path_utils.get_basename(name) + '.' + consts.DataTypes.Python)
        if path_utils.is_file(python_file):
            data_type = consts.DataTypes.Python
            return data_type

        data_folder = data.DataFolder(name, self.get_code_path())
        data_type = data_folder.get_data_type()

        return data_type

    def get_code_files(self, basename=False):
        """
        Returns path to the code files found in the code folder of the rig
        :param basename: bool, Whether to return full path of code files or only the code file names
        :return: list<str>
        """

        code_path = self.get_code_path()
        code_files = list()
        code_folders = self.get_code_folders()

        for f in code_folders:
            data_folder = data.DataFolder(
                name=f, file_path=code_path, data_path=rigbuilder.get_data_files_directory()
            )
            data_inst = data_folder.get_folder_data_instance()
            if data_inst:
                code_file = data_inst.get_file()
                if not basename:
                    code_files.append(code_file)
                else:
                    code_files.append(path_utils.get_basename(code_file))

        return code_files

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
            code_name += '.{}'.format(scripts.ScriptManifestData.get_data_extension())
        else:
            code_name += '.{}'.format(scripts.ScriptPythonData.get_data_extension())

        if not basename:
            code_name = path_utils.join_path(code_file, code_name)

        return code_name

    def get_code_name_from_path(self, code_path):
        """
        Returns code name from given path
        :param code_path: str
        :return: str
        """

        split_path = code_path.split('{}/'.format(self.CODE_FOLDER_NAME))
        if len(split_path) == 2:
            parts = split_path[1].split('/')
            if len(parts) > 2:
                last_part = fileio.remove_extension(parts[-1])
                if last_part == parts[-2]:
                    if len(parts) > 2:
                        return string.join(parts[:-1], '/')
                else:
                    return string.join(parts, '/')
            elif len(parts) == 2:
                return parts[0]

        return None

    def get_code_module(self, name):
        """
        Returns module instance of a code with the given name (if exists)
        :param name: str, name of the code to instantiate
        :return: tuple<module, bool, bool>l tuple containing the module instance, initialization state and status
        """

        script = self.get_code_file(name)
        module, init_passed, status = self._source_script(script)

        return module, init_passed, status

    def create_code(self, name, data_type=consts.DataTypes.Python, unique_name=False, import_data=None):
        """
        Creates a new code folder with the given name and data type
        :param name: str, name of the code to create
        :param data_type: str, type of code
        :param unique_name: str, whether or not to increment name
        :param import_data: str, name of data in the rig
        :return: str, new code file name
        """

        code_path = self.get_code_path()
        if not code_path:
            return

        if unique_name:
            test_path = path_utils.join_path(code_path, name)
            if path_utils.is_dir(test_path):
                test_path = path_utils.unique_path_name(test_path)
                name = path_utils.get_basename(test_path)

        data_folder = data.ScriptFolder(name, code_path, data_path=rigbuilder.get_data_files_directory())
        data_folder.set_data_type(data_type)
        data_inst = data_folder.get_folder_data_instance()
        if not data_inst:
            LOGGER.warning('Impossible to create data of type {} because that data is not supported!'.format(data_type))
            return

        if name == consts.MANIFEST_FILE:
            data_inst.create()
            return

        if import_data:
            data_inst.set_lines(['', 'def main():', "    rig.import_data('%s')" % import_data])
        else:
            data_inst.set_lines(['', 'def main():', '    return'])

        data_inst.create()

        # TODO: We should retrieve file path directly from data instance (not through data object)
        file_name = data_inst.get_file()

        if not self.is_in_manifest('{}.{}'.format(name, scripts.ScriptPythonData.get_data_extension())):
            self.set_scripts_manifest(
                ['{}.{}'.format(name, scripts.ScriptPythonData.get_data_extension())], append=True)

        return file_name

    def move_code(self, old_name, new_name):
        """
        Moves given script folder to the new path
        :param old_name: str, current code folder path
        :param new_name: str, new code folder path
        :return: str, new code folder path
        """

        code_path = self.get_code_path()
        old_path = path_utils.join_path(code_path, old_name)
        new_path = path_utils.join_path(code_path, new_name)
        basename = path_utils.get_basename(new_name)
        dir_name = path_utils.get_dirname(new_name)
        test_path = new_name

        if path_utils.is_dir(test_path):
            last_number = 1
            while path_utils.is_dir(test_path):
                basename = name_utils.replace_last_number(basename, last_number)
                new_name = basename
                if dir_name:
                    new_name = path_utils.join_path(dir_name, basename)
                test_path = path_utils.join_path(code_path, new_name)
                last_number += 1

        folder.move_folder(old_path, new_path)
        file_name = new_name
        old_basename = path_utils.get_basename(old_name)
        new_basename = path_utils.get_basename(new_name)

        update_path = path_utils.join_path(
            test_path, old_basename + '.{}'.format(scripts.ScriptPythonData.get_data_extension()))
        folder.rename_folder(update_path, new_basename+'.{}'.format(scripts.ScriptPythonData.get_data_extension()))

        return file_name

    def rename_code(self, old_name, new_name):
        """
        Renames the code folder given with old_name to new_name
        :param old_name: str, current name of the code folder
        :param new_name: str, new name for the code folder
        :return: str, new path to the code folder if rename was successful
        """

        # new_name = name_utils.clean_file_string(new_name).replace('.', '_')
        new_name = name_utils.clean_file_string(new_name).replace('.', '_')
        old_len = old_name.count('/')
        new_len = new_name.count('/')

        if old_len != new_len:
            LOGGER.warning('Rename works on code folder in the same folder. Try to move instead!')
            return

        sub_new_name = path_utils.remove_common_path(old_name, new_name)
        code_folder = data.ScriptFolder(old_name, self.get_code_path())
        code_folder.rename(sub_new_name)

        code_name = new_name + '.py'

        return code_name

    def delete_code(self, name):
        """
        Deletes the given code folder from disk
        :param name: str, name of a code folder in the task
        """

        folder.delete_folder(name, self.get_code_path())