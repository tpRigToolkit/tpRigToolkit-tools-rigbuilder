#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base object implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import logging

from tpPyUtils import folder, settings, version, path as path_utils

from tpRigToolkit.tools.rigbuilder.core import consts, utils, data
from tpRigToolkit.tools.rigbuilder.objects import helpers

LOGGER = logging.getLogger('tpRigToolkit')


class BaseObject(object):

    DESCRIPTION = 'base'
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
        super(BaseObject, self).__init__()

        self._name = name
        self._directory = folder.get_current_working_directory()
        self._settings = None
        self._library = None
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

    def check(self):
        """
        Returns whether or not current object is valid or not
        Overrides in specific classes
        :return: bool
        """

        return False

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

    def library(self):
        """
        Returns data library linked to this widget
        :return: Library
        """

        return self._library

    def set_library(self, library):
        """
        Sets the data library linked to this item
        :param library: Library
        """

        self._library = library

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

    def rename(self, new_name):
        """
        Renames the object
        :param new_name: str, new name for the object
        :return: bool, Whether the object was renamed or not
        """

        split_name = new_name.split('/')
        if path_utils.rename(self.get_path(), split_name[-1]):
            self.load(new_name)
            return True

        return False

    def delete(self):
        """
        Deletes the rig
        """

        if self._name:
            folder.delete_folder(self._name, self._directory)
        else:
            basename = path_utils.get_basename(self._directory)
            dir_name = path_utils.get_dirname(self._directory)
            folder.delete_folder(basename, dir_name)

    # ================================================================================================
    # ======================== CREATE / LOAD
    # ================================================================================================

    def load(self, *args, **kwargs):
        """
        Loads the given build object into the instance
        """

        self._refresh()

    def sync(self):
        """
        Syncs current object
        """

        raise NotImplementedError('sync function not implemented for "{}"'.format(self.__class__.__name__))

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
                                      data_path=utils.get_data_files_directory())
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
        data_folder = data.DataFolder(name, data_path, data_path=utils.get_data_files_directory())
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
        data_folder = data.DataFolder(name=name, file_path=data_path, data_path=utils.get_data_files_directory())

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

        data_folder = data.DataFolder(name=name, file_path=data_path, data_path=utils.get_data_files_directory())
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

    def get_data_sub_path(self, name):
        """
        Returns the path where data sub folders are stored
        :param name: str
        :return: str
        """

        data_sub_path = self._create_sub_data_folder(data_name=name)

        return data_sub_path

    def get_data_sub_folder_names(self, data_name):
        """
        Return data sub folders
        :param data_name: str, data name
        :return: list<str>
        """

        sub_folder = self.get_data_sub_path(data_name)
        sub_folders = folder.get_folders(sub_folder)

        return sub_folders

    def has_sub_folder(self, data_name, sub_folder_name):
        """
        Returns if the data folder has given sub folder stored in it
        :param data_name: str, data name
        :param sub_folder_name: str, sub bolder data name
        :return: bool
        """

        sub_folders = self.get_data_sub_folder_names(data_name)
        if sub_folder_name in sub_folders:
            return True

        return False

    def get_data_current_sub_folder(self, name):
        """
        Returns the current data sub folder
        :param name: str
        :return: str
        """

        data_folder = data.ScriptFolder(
            name=name, file_path=self.get_data_path(), data_path=utils.get_data_files_directory())
        sub_folder = data_folder.get_current_sub_folder()

        return sub_folder

    def get_data_current_sub_folder_and_type(self, name):
        """
        Returns the current data sub folder and its data type
        :param name: str
        :return: lsit<str, str>
        """

        data_folder = data.ScriptFolder(
            name=name, file_path=self.get_data_path(), data_path=tpRigBuilder.get_data_files_directory())
        data_type = data_folder.get_data_type()
        sub_folder = data_folder.get_sub_folder()

        return sub_folder, data_type

    def create_sub_folder(self, data_name, sub_folder_name):
        """
        Creates a new data sub folder
        :param data_name: str, name of the data sub folder
        :param sub_folder_name: str, sub folder name
        :return: str
        """

        data_type = self.get_data_type(data_name)
        return self.create_data(data_name, data_type, sub_folder_name)

    def copy_sub_folder_to_data(self, sub_folder_name, data_name):
        """
        Copies sub folder into data folder
        :param sub_folder_name: str
        :param data_name: str
        """

        if not self.has_sub_folder(data_name, sub_folder_name):
            LOGGER.warning('Data {} has no sub folder: {} to copy from!'.format(data_name, sub_folder_name))
            return

        source_file = self.get_data_file_or_folder(data_name, sub_folder_name)
        target_file = self.get_data_file_or_folder(data_name)

        helpers.ObjectsHelpers.copy(source_file, target_file)

    def copy_data_to_sub_folder(self, data_name, sub_folder_name):
        """
        Copies data folder into data sub folder
        :param data_name:
        :param sub_folder_name:
        """

        if not self.has_sub_folder(data_name, sub_folder_name):
            LOGGER.warning('Data {} has no sub folder: {} to copy to!'.format(data_name, sub_folder_name))
            return

        source_file = self.get_data_file_or_folder(data_name)
        target_file = self.get_data_file_or_folder(data_name, sub_folder_name)

        helpers.ObjectsHelpers.copy(source_file, target_file)

    def open_data(self, name, sub_folder=None):
        """
        Run open_data function on the data widget associated to the given data name
        :param name: str, name of a data folder in the rig
        :param sub_folder: bool
        """

        data_folder_name = self.get_data_folder(name)
        LOGGER.debug('Open data in: {}'.format(data_folder_name))
        if not path_utils.is_dir(data_folder_name):
            LOGGER.warning('{} data does not exists in {}!'.format(name, self.get_name()))
            return

        inst, original_sub_folder = self._get_data_instance(name, sub_folder)
        if hasattr(inst, 'import_data') and not hasattr(inst, 'open'):
            value = inst.import_data()
            inst.set_sub_folder(original_sub_folder)
            return value
        if hasattr(inst, 'open'):
            value = inst.open()
            inst.set_sub_folder(original_sub_folder)
            return value
        else:
            LOGGER.warning('Could not open data {} in rig {}. It has no open function'.format(name, self.get_name()))

    def import_data(self, name, sub_folder=None):
        """
        Runs import_data function found on the data widget associated to the given data name
        :param name:str, name of a data folder in the rig
        :param sub_folder: str
        """

        data_folder_name = self.get_data_folder(name)
        LOGGER.info('Import data from: {}'.format(data_folder_name))
        if not path_utils.is_dir(data_folder_name):
            LOGGER.warning('{} data does not exists in {}!'.format(name, self.get_name()))
            return

        if not self.library():
            return
        if not self.library().manager():
            return
        item = self.library().manager().item_from_path(data_folder_name)
        value = item.import_data()
        print(value)

        # inst, original_sub_folder = self._get_data_instance(name, sub_folder)
        # if hasattr(inst, 'import_data'):
        #     value = inst.import_data()
        #     inst.set_sub_folder(original_sub_folder)
        #     return value
        # else:
        #     tpRigBuilder.logger.error('Could not import data {} in rig {}. It has no import function'.format(name, self.get_name()))

    def reference_data(self, name, sub_folder=None):
        """
        Tries to reference the current process data
        :param name: str, name of a data folder in the rig
        :param sub_folder: bool
        :return:
        """

        data_folder_name = self.get_data_folder(name)
        LOGGER.debug('Reference data in {}'.format(data_folder_name))
        if not path_utils.is_dir(data_folder_name):
            LOGGER.warning('{} data does not exists in {}'.format(name, self.get_name()))
            return

        instance, original_sub_folder = self._get_data_instance(name, sub_folder)
        return_value = None
        if hasattr(instance, 'reference_data'):
            return_value = instance.reference_data()
        else:
            LOGGER.warning(
                'Could not reference data {0} in rig {1}. {1} has no reference function'.format(name, self.get_name()))

        instance.set_sub_folder(original_sub_folder)

        return return_value

    def save_data(self, name, comment='', sub_folder=None):
        """
        Tries the run the save function of the current rig data
        :param name: str, name of a data folder in the rig
        :param comment: str
        :param sub_folder: bool
        :return: bool
        """

        instance, original_sub_folder = self._get_data_instance(name, sub_folder)
        if not comment:
            comment = 'Saved through rig class with no comment'
        if hasattr(instance, 'save'):
            saved = instance.save(comment)
            instance.set_sub_folder(original_sub_folder)
            if saved:
                return True

        return False

    def export_data(self, name, comment='', sub_folder=None):
        """
        Tries to run the export function ot the current rig data
        :param name: str, name of the data folder in the rig
        :param comment: str
        :param sub_folder: bool
        :return: bool
        """

        instance, original_sub_folder = self._get_data_instance(name, sub_folder)
        if not comment:
            comment = 'Exported through rig class with no comment'
        if hasattr(instance, 'export_data'):
            exported = instance.export_data(comment)
            instance.set_sub_folder(original_sub_folder)
            if exported:
                return True

        return False

    def rename_data(self, old_name, new_name):
        """
        Renames the data folder specified with old_name to the new_name
        :param old_name: str, current name of the data
        :param new_name: str, new name for the data
        :return: str, new path to the data if rename operation was successful
        """

        data_folder = data.ScriptFolder(old_name, self.get_data_path(), data_path=utils.get_data_files_directory())
        return data_folder.rename(new_name)

    def delete_data(self, name, sub_folder=None):
        """
        Deletes the given data folder from disk
        :param name: str, name of the data folder on the rig to delete
        :param sub_folder: str, data sub folder to delete (optional)
        """

        data_folder = data.ScriptFolder(name, self.get_data_path(), data_path=utils.get_data_files_directory())
        data_folder.set_sub_folder(sub_folder)
        data_folder.delete()

    def clean_student_license(self, name):
        """
        Clean student license from given file
        :param name: name of a data folder in the rig
        """

        data_folder_name = self.get_data_folder(name)
        LOGGER.debug('Cleaning Student License in: {}'.format(data_folder_name))
        if not path_utils.is_dir(data_folder_name):
            LOGGER.warning('{} data does not exists in {}!'.format(name, self.get_name()))
            return

        inst, original_sub_folder = self._get_data_instance(name, None)
        if hasattr(inst, 'clean_student_license'):
            inst.clean_student_license()

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

    def _get_invalid_code_names(self):
        """
        Internal function that returns a list not valid code names
        :return: list(str)
        """

        return list()

    def _create_folder(self):
        """
        Internal function that creates the folder of the rig
        :return: str, path where object is created
        """

        raise NotImplementedError(
            '_create_folder function for "{}" is not implemented!'.format(self.__class__.__name__))

    def _refresh(self):
        """
        Internal function that is called when object is loaded
        """

        self._setup_options()
        self._setup_settings()

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

    def _create_sub_data_folder(self, data_name):
        """
        Internal function used to create sub data folders
        :param data_name: str, name of the data folder
        :return: str
        """

        data_path = self.get_data_folder(data_name)
        sub_path = folder.create_folder(self.SUB_DATA_FOLDER_NAME, data_path)

        return sub_path

    def _get_data_instance(self, name, sub_folder):
        """
        Internal function used to retrieve data widget associated to the given data name
        :param name: str, name of data in the rig
        :param sub_folder: str, sub folder where data is located
        :return: tuple<DataWidget, str>, data widget and sub folder tuple
        """

        data_folder = data.ScriptFolder(
            name=name, file_path=self.get_data_path(), data_path=utils.get_data_files_directory())
        current_sub_folder = sub_folder
        if sub_folder and sub_folder is not False:
            current_sub_folder = data_folder.get_current_sub_folder()
            data_folder.set_sub_folder(sub_folder)

        inst = data_folder.get_folder_data_instance()

        return inst, current_sub_folder
