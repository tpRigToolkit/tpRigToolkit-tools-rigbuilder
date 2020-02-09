#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains class that defines Blueprints
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import string
import logging
import traceback

from tpDccLib.core import scripts
from tpPyUtils import jsonio, folder, fileio, settings, version, path as path_utils, name as name_utils

from tpRigToolkit.tools import rigbuilder
from tpRigToolkit.tools.rigbuilder.core import consts, data

LOGGER = logging.getLogger('tpRigToolkit')


class BuildObject(object):

    DATA_FOLDER_NAME = consts.DATA_FOLDER
    DATA_FILE_NAME = consts.DATA_FILE
    BACKUP_FOLDER = consts.BACKUP_FOLDER
    VERSION_NAME = consts.VERSION_NAME
    SETTINGS_FILE_NAME = consts.SETTINGS_FILE_NAME
    SETTINGS_FILE_EXTENSION = consts.SETTINGS_FILE_EXTENSION
    OPTIONS_FILE_NAME = consts.OPTIONS_FILE_NAME
    OPTIONS_FILE_EXTENSION = consts.OPTIONS_FILE_EXTENSION
    FOLDERS_PREFIX = consts.FOLDERS_PREFIX
    FOLDERS_SUFFIX = consts.FOLDERS_SUFFIX

    def __init__(self, name=None):
        super(BuildObject, self).__init__()

        self._name = name
        self._directory = folder.get_current_working_directory()
        self._settings = None
        self._option_settings = None
        self._option_values = dict()

    # ================================================================================================
    # ======================== STATIC / CLASS
    # ================================================================================================

    @classmethod
    def get_empty_object(cls, path=None):
        """
        Returns empty build object instance
        :param path: str
        :return: cls
        """

        build_object_inst = cls()
        build_object_inst.set_directory(path)

        return build_object_inst

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def get_name(self):
        """
        Returns the name of the blueprint
        :return: str
        """

        if not self._name:
            return path_utils.get_basename(self._directory)

        return self._name

    def get_directory(self):
        """
        Returns directory where rig is located
        :return: str
        """

        return self._directory

    def set_directory(self, directory):
        """
        Sets the directory where this rig is located
        :param directory: str
        """

        self._directory = directory

    def get_path(self):
        """
        Returns path where blueprint folder is located
        :return: str
        """

        if self._name:
            return path_utils.join_path(self._directory, self._name)
        else:
            return self._directory

    def get_basename(self):
        """
        Returns the base name of the rig
        :return: str
        """

        name = self._name
        if not name:
            name = self._directory

        return path_utils.get_basename(name)

    def get_setting_file(self, name):
        """
        Returns settings or option file depending of the setting name given
        :param name: str, "settings" || "options"
        :return: variant, str || None
        """

        if name == 'settings':
            return self.get_settings_file()

        if name == 'options':
            return self.get_option_file()

        return None

    def get_setting_names(self):
        """
        Returns a list with options and settings files
        :return: list<str>
        """

        settings_file = self.get_settings_file()
        settings_name = path_utils.get_basename(settings_file, with_extension=False)

        option_file = self.get_option_file()
        option_name = path_utils.get_basename(option_file, with_extension=False)

        return [settings_name, option_name]

    # ================================================================================================
    # ======================== CREATE / LOAD
    # ================================================================================================

    def create(self):
        """
        Creates build object
        :return: str, path where object is created
        """

        return self._create_folder()

    # ================================================================================================
    # ======================== DATA
    # ================================================================================================

    def get_data_path(self):
        """
        Returns the path to the data folder
        :return: str
        """

        return self._get_path(self.DATA_FOLDER_NAME)

    def is_data_folder(self, name, sub_folder=None):
        """
        Returns whether given folder is a data folder or not
        :param name: str, name of the folder to check
        :param sub_folder: str, name of the sub folder to check
        :return: bool
        """

        data_path = self.get_data_folder(name, sub_folder)
        if not data_path:
            return False
        if path_utils.is_dir(data_path):
            return True

        return False

    def get_data_folders(self):
        """
        Returns a list with all task data folders
        :return: list<str>
        """

        data_path = self.get_data_path()

        return folder.get_folders(data_path)

    def get_data_folder(self, name, sub_folder=None):
        """
        Returns path to a dat folder in the rig
        :param name: str, name of a data folder in the rig
        :param sub_folder: str, path to a sub folder in the data folder (optional)
        :return: str
        """

        data_folders = self.get_data_folders()
        if not data_folders:
            return

        for f in data_folders:
            if f == name:
                if sub_folder:
                    sub_folder_path = path_utils.join_path(self.get_data_sub_path(name), sub_folder)
                    return sub_folder_path
                else:
                    return path_utils.join_path(self.get_data_path(), name)

    def get_data_type(self, name):
        """
        Returns the data type stored in the given data folder
        :param name: str, name of a data folder in the rig
        :return: str, name of the data type of the data folder (if exists)
        """

        data_folder = data.DataFolder(name=name, file_path=self.get_data_path(),
                                      data_path=rigbuilder.get_data_files_directory())
        data_type = data_folder.get_data_type()

        return data_type

    def get_data_file_or_folder(self, name, sub_folder_name=None):
        """
        Data is saved to a top file or folder. This is the main data save under data folder
        This will return the file/folder that gets versioned
        :param name:str
        :param sub_folder_name: str
        :return: str
        """

        data_path = self.get_data_path()
        data_folder = data.DataFolder(name, data_path, data_path=rigbuilder.get_data_files_directory())
        inst = data_folder.get_folder_data_instance()
        if not inst:
            return
        file_path = inst.get_file_direct(sub_folder_name)

        return file_path

    def get_data_instance(self, name):
        """
        Returns an instance of the data type class for data wit the given name
        :param name: str, name of data type you want to get
        :return: DataWidget
        """

        data_path = self.get_data_path()
        data_folder = data.DataFolder(name=name, file_path=data_path, data_path=rigbuilder.get_data_files_directory())

        return data_folder.get_folder_data_instance()

    def create_data(self, name, data_type, sub_folder=None):
        """
        Creates a new data item folder in the task
        :param name: str, name of a data folder in the task
        :param data_type: str, string that defines the type of data we want to create
        :param sub_folder: str, sub folder where data is located (optional)
        :return: str, path where item data folder was created
        """

        orig_name = name
        data_path = self.get_data_path()

        test_path = path_utils.join_path(data_path, name)
        if not sub_folder:
            test_path = path_utils.unique_path_name(test_path)
        name = path_utils.get_basename(test_path)

        data_folder = data.DataFolder(name=name, file_path=data_path, data_path=rigbuilder.get_data_files_directory())
        data_folder.set_data_type(data_type)
        return_path = data_folder.folder_path

        if sub_folder:
            sub_path = self.get_data_sub_path(orig_name)
            sub_folder_path = path_utils.join_path(sub_path, sub_folder)
            if path_utils.is_dir(sub_folder_path):
                return sub_folder_path
            sub_folder_path = path_utils.unique_path_name(sub_folder_path)
            return_path = folder.create_folder(sub_folder_path)

        return return_path

    # ================================================================================================
    # ======================== SETTINGS
    # ================================================================================================

    def get_settings_file(self):
        """
        Returns settings file of the rig
        :return: str
        """

        self._setup_settings()
        return self._settings.get_file()

    def get_settings_instance(self):
        """
        Returns settings object of the rig
        :return: JSONSettings
        """

        self._setup_settings()
        return self._settings

    def set_setting(self, name, value):
        """
        Set a setting of the rig
        :param name: str, name of the setting to set. If does not exists, the settings will be created
        :param value: variant
        """

        self._setup_settings()
        self._settings.set(name, value)

    def get_setting(self, name):
        """
        Returns setting value with the given name (if exists)
        :param name: str, name of the setting to retrieve
        :return: str
        """

        self._setup_settings()
        return self._settings.get(name)

    # ================================================================================================
    # ======================== OPTIONS
    # ================================================================================================

    def get_option_file(self):
        """
        Returns options file
        :return: str
        """

        self._setup_options()
        return self._option_settings.get_file()

    def has_options(self):
        """
        Returns whether the current has options or not
        :return: bool
        """

        self._setup_options()
        return self._option_settings.has_settings()

    def has_option(self, name, group=None):
        """
        Returns whether the current object has given option or not
        :param name: str, name of the option
        :param group: variant, str || None, group of the option (optional)
        :return: bool
        """

        self._setup_options()
        if group:
            name = '{}.{}'.format(group, name)
        else:
            name = str(name)

        return self._option_settings.has_setting(name)

    def add_option(self, name, value, group=None, option_type=None):
        """
        Adds a new option to the options file
        :param name: str, name of the option
        :param value: variant, value of the option
        :param group: variant, str || None, group of the option (optional)
        :param option_type: variant, str || None, option type (optional)
        """

        self._setup_options()

        if group:
            name = '{}.{}'.format(group, name)
        else:
            name = str(name)

        if option_type == 'script':
            value = [value, 'script']
        elif option_type == 'dictionary':
            value = [value, 'dictionary']

        self._option_settings.set(name, value)

    def set_option(self, name, value, group=None):
        """
        Set an option of the option settings file. If the option does not exist, it will be created
        :param name: str, name of the option we want to set
        :param value: variant, value of the option
        :param group: variant, str || None, group of the option (optional)
        """

        if group:
            name = '{}.{}'.format(group, name)
        else:
            name = str(name)

        self._option_settings.set(name, value)

    def get_unformatted_option(self, name, group=None):
        """
        Returns option without format (string format)
        :param name: str, name of the option we want to retrieve
        :param group: variant, str || None, group of the option (optional)
        :return: str
        """

        self._setup_options()
        if group:
            name = '{}.{}'.format(group, name)
        else:
            name = str(name)

        value = self._option_settings.get(name)

        return value

    def get_option(self, name, group=None):
        """
        Returns option by name and group
        :param name: str, name of the option we want to retrieve
        :param group: variant, str || None, group of the option (optional)
        :return: variant
        """

        self._setup_options()

        value = self.get_unformatted_option(name, group)
        if value is None:
            LOGGER.warning(
                'Impossible to access option with proper format from {}'.format(self._option_settings.directory))
            if self.has_option(name, group):
                if group:
                    LOGGER.warning('Could not find option: "{}" in group: "{}"'.format(name, group))
                else:
                    LOGGER.warning('Could not find option: {}'.format(name))

        value = self._format_option_value(value)

        LOGGER.debug('Accessed Option - Option: "{}" | Group: "{}" | Value: "{}"'.format(name, group, value))

        return value

    def get_option_match(self, name, return_first=True):
        """
        Function that tries to find a matching option in all the options
        :param name: str
        :param return_first: bool
        :return: variant
        """

        self._setup_options()
        options_dict = self._option_settings.settings_dict
        found = dict()
        for key in options_dict:
            if key.endswith(name):
                if return_first:
                    value = self._format_option_value(options_dict[key])
                    LOGGER.debug('Accessed - Option: {}, value: {}'.format(name, options_dict[key]))
                    return value
                found[name] = options_dict[key]

        return found

    def get_options(self):
        """
        Returns all optiosn contained in the settings file
        :return: str
        """

        self._setup_options()
        options = list()
        if self._option_settings:
            options = self._option_settings.get_settings()

        return options

    def clear_options(self):
        """
        Clears all the options
        """

        if self._option_settings:
            self._option_settings.clear()

    # ================================================================================================
    # ======================== INTERNAL
    # ================================================================================================

    def _create_folder(self):
        """
        Internal function that creates the folder of the rig
        :return: str, path where object is created
        """

        raise NotImplementedError(
            '_create_folder function for "{}" is not implemented!'.format(self.__class__.__name__))

    def _get_path(self, name):
        """
        Internal function used to return the path with given name inside the rig folder
        :param name: str, sub folder to append to the rig folder path
        :return: str
        """

        return path_utils.join_path(self.get_path(), name)

    def _get_folders_without_prefix_suffix(self, directory, recursive=False, base_directory=None):
        """
        Returns folders without rig tasks fixes and suffixes
        :param directory:
        :param recursive:
        :param base_directory:
        :return:
        """

        if not path_utils.is_dir(directory):
            return

        found_folders = list()
        folders = folder.get_folders(directory)
        if not base_directory:
            base_directory = directory

        for f in folders:
            if folder == self.VERSION_NAME:
                folder_version = version.VersionFile(directory)
                if folder_version.updated_old:
                    continue
            if f.startswith(self.FOLDERS_PREFIX) and f.endswith(self.FOLDERS_SUFFIX):
                continue

            folder_path = path_utils.join_path(directory, f)
            folder_name = os.path.relpath(folder_path, base_directory)
            folder_name = path_utils.clean_path(folder_name)
            found_folders.append(folder_name)
            if recursive:
                sub_folders = self._get_folders_without_prefix_suffix(folder_path, recursive, base_directory)
                found_folders += sub_folders

        return found_folders

    def _setup_settings(self):
        """
        Internal function that initializes settings files for the rig
        """

        if not self._settings:
            self._settings = settings.JSONSettings()

        self._settings.set_directory(
            self.get_path(), '{}.{}'.format(self.SETTINGS_FILE_NAME, self.SETTINGS_FILE_EXTENSION))

    def _setup_options(self):
        """
        Internal function that initializes option files
        """

        if not self._option_settings:
            self._option_settings = settings.JSONSettings()

        self._option_settings.set_directory(
            self.get_path(), '{}.{}'.format(self.OPTIONS_FILE_NAME, self.OPTIONS_FILE_EXTENSION))

    def _format_option_value(self, value):
        """
        Internal function used to format object option value
        :param value: variant
        :return: variant
        """

        new_value = value
        if type(value) == list:
            option_type = value[1]
            value = value[0]
            if option_type == 'dictionary':
                new_value = value[0]
                if type(new_value) == list:
                    new_value = new_value[0]
        if type(value) == str or type(value) in [unicode, str]:
            eval_value = None
            try:
                if value:
                    eval_value = eval(value)
            except Exception:
                pass
            if eval_value:
                if type(eval_value) in [list, tuple, dict]:
                    new_value = eval_value
                    value = eval_value
        if type(value) in [str, unicode]:
            if value.find(',') > -1:
                new_value = value.split(',')

        return new_value


class ScriptObject(BuildObject, object):

    CODE_FOLDER = consts.CODE_FOLDER
    MANIFEST_FILE = consts.MANIFEST_FILE

    def __init__(self, name):
        super(ScriptObject, self).__init__(name=name)

    # OVERRIDES
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

    # MANIFEST
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

    # CODE
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


class Blueprint(ScriptObject, object):

    BLUEPRINTS_FOLDER = consts.BLUEPRINTS_FOLDER
    DATA_FILE_NAME_EXTENSION = 'json'

    def __init__(self, name):
        super(Blueprint, self).__init__(name=name)

    # OVERRIDES
    def _create_folder(self):
        """
        Overrides base BuildObject _create_folder function
        Internal function that creates the folder of the rig
        :return: str, path where object is created
        """

        blueprint_directory = path_utils.clean_path(os.path.join(self._directory, self.BLUEPRINTS_FOLDER))
        blueprint_path = folder.create_folder(self._name, blueprint_directory)
        if not blueprint_path or not path_utils.is_dir(blueprint_path):
            return blueprint_path

        folder.create_folder(self.DATA_FOLDER_NAME, blueprint_path)
        code_folder = folder.create_folder(self.CODE_FOLDER, blueprint_path)
        folder.create_folder(self.BACKUP_FOLDER, blueprint_path)
        manifest_folder = path_utils.join_path(code_folder, self.MANIFEST_FILE)
        if not path_utils.is_dir(manifest_folder):
            self.create_code(self.MANIFEST_FILE, scripts.ScriptManifestData.get_data_type())

        self._create_data_file()
        self._create_options_file()

        return blueprint_path

    # BASE
    def get_path(self):
        """
        Overrides base BuildObject get_path function
        Returns path where blueprint folder is located
        :return: str
        """

        if self._name:
            return path_utils.clean_path(os.path.join(self._directory, self.BLUEPRINTS_FOLDER, self._name))
        else:
            return path_utils.clean_path(os.path.join(self._directory, self.BLUEPRINTS_FOLDER))

    def get_blueprint_data_path(self):
        """
        Returns path where blueprint options file is located
        :return: str
        """

        options_path = path_utils.clean_path(os.path.join(self.get_path(), self.DATA_FILE_NAME))

        return options_path

    def get_blueprint_options_path(self):
        """
        Returns path where blueprint options file is located
        :return: str
        """

        options_path = path_utils.clean_path(os.path.join(self.get_path(), self.OPTIONS_FILE_NAME))

        return options_path

    def _create_data_file(self):
        """
        Internal function that creates blueprint options file
        :return: str
        """

        blueprint_data_dict = self._get_data_dict()

        data_file = self.get_blueprint_data_path()
        if not os.path.isfile(data_file):
            data_file = jsonio.write_to_file(blueprint_data_dict, data_file)
        if not os.path.isfile(data_file):
            LOGGER.warning('Error while creating Blueprint data file: "{}"'.format(data_file))
            return

        return data_file

    def _create_options_file(self):
        """
        Internal function that creates blueprint options file
        :return: str
        """

        options_file = self.get_blueprint_options_path()
        if not os.path.isfile(options_file):
            options_file = jsonio.write_to_file({}, options_file)
        if not os.path.isfile(options_file):
            LOGGER.warning('Error while creating Blueprint options file: "{}"'.format(options_file))
            return

        return options_file

    def _get_data_dict(self):
        """
        Returns blueprint info dict
        :return: dict
        """

        return {
            'name': self._name,
            'data_type': consts.DataTypes.Blueprint
        }
