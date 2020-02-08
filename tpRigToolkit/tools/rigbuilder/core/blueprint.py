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
import shutil
import logging

from tpPyUtils import yamlio, path as path_utils

from tpRigToolkit.tools.rigbuilder.core import consts
from tpRigToolkit.tools.rigbuilder.widgets import scriptstree

LOGGER = logging.getLogger('tpRigToolkit')


class Blueprint(scriptstree.ScriptObject, object):

    BLUEPRINT_FOLDER_NAME = consts.BLUEPRINTS_FOLDER
    BLUEPRINT_DATA_FILE_NAME = consts.BLUEPRINTS_DATA_FILE
    BLUEPRINT_OPTIONS_FILE_NAME = consts.BLUEPRINTS_OPTIONS_FILE

    def __init__(self, name, directory):
        self._name = name
        self._directory = directory

    def get_name(self):
        """
        Returns the name of the blueprint
        :return: str
        """

        return self._name

    def get_path(self):
        """
        Returns path where blueprint folder is located
        :return: str
        """

        if self._name:
            return path_utils.clean_path(os.path.join(self._directory, consts.BLUEPRINTS_FOLDER, self._name))
        else:
            return path_utils.clean_path(os.path.join(self._directory, consts.BLUEPRINTS_FOLDER))

    def get_data_path(self):
        """
        Returns path where blueprint options file is located
        :return: str
        """

        options_path = path_utils.clean_path(os.path.join(self.get_path(), self.BLUEPRINT_DATA_FILE_NAME))

        return options_path

    def get_options_path(self):
        """
        Returns path where blueprint options file is located
        :return: str
        """

        options_path = path_utils.clean_path(os.path.join(self.get_path(), self.BLUEPRINT_OPTIONS_FILE_NAME))

        return options_path

    def create(self, unique_name=False):
        """
        Creates blueprint
        """

        blueprint_path = self.get_path()
        if not blueprint_path:
            return
        if unique_name:
            test_path = path_utils.join_path(blueprint_path, self._name)
            if path_utils.is_dir(test_path):
                test_path = path_utils.unique_path_name(test_path)
                self._name = path_utils.get_basename(test_path)

        blueprint_dir = os.path.dirname(blueprint_path)
        blueprint_path = path_utils.clean_path(os.path.join(blueprint_dir, self._name))
        if os.path.isdir(blueprint_path):
            LOGGER.warning('Blueprint "{}" in path "{}" already exists!'.format(self._name, blueprint_path))
            return
        else:
            os.makedirs(blueprint_path)

        try:
            data_file = self._create_data_file()
            options_file = self._create_options_file()
        except Exception as exc:
            if os.path.isdir(blueprint_path):
                shutil.rmtree(blueprint_path)
            LOGGER.warning('Error while create Blueprint "{}" | {}'.format(self._name, exc))
            return

        return blueprint_path

    def _create_data_file(self):
        """
        Internal function that creates blueprint data file
        :return: str
        """

        blueprint_data_dict = self._get_data_dict()
        if not blueprint_data_dict:
            LOGGER.warning('Error while create Blueprint because no data found!')
            return

        data_file = self.get_data_path()
        if not os.path.isfile(data_file):
            yamlio.write_to_file(blueprint_data_dict, data_file)
        if not os.path.isfile(data_file):
            LOGGER.warning('Error while creating Blueprint data file: "{}"'.format(data_file))
            return

        return data_file

    def _create_options_file(self):
        """
        Internal function that creates blueprint options file
        :return: str
        """

        options_file = self.get_options_path()
        if not os.path.isfile(options_file):
            yamlio.write_to_file({}, options_file)
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
