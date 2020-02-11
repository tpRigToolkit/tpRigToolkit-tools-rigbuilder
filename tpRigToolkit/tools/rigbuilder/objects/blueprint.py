#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains blueprint object implementation
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import logging

from tpDccLib.core import scripts
from tpPyUtils import jsonio, folder, path as path_utils

from tpRigToolkit.tools.rigbuilder.core import consts
from tpRigToolkit.tools.rigbuilder.objects import script

LOGGER = logging.getLogger('tpRigToolkit')


class Blueprint(script.ScriptObject, object):

    BLUEPRINTS_FOLDER = consts.BLUEPRINTS_FOLDER
    DATA_FILE_NAME_EXTENSION = 'json'

    def __init__(self, name):
        super(Blueprint, self).__init__(name=name)

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

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

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

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

    def build(self, start_new=False):
        """
        Builds current blueprint
        """

        valid_run = self.run(start_new=start_new)

        return valid_run

    # ================================================================================================
    # ======================== INTERNAL
    # ================================================================================================

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


