#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for tpRigToolkit.tools.rigbuilder
"""

from __future__ import print_function, division, absolute_import

import os

from tpPyUtils import settings, osplatform, path as path_utils

os.environ['RIGBUILDER_PATH'] = os.path.abspath(os.path.dirname(__file__))


def get_library_settings_path():
    """
    Returns path to tpRigBuilderMaya settings file
    :return: str
    """

    settings_path = os.getenv('APPDATA') or os.getenv('HOME')
    return os.path.join(settings_path, 'tpRigGraphMaya', 'library.json')


def get_library_settings():
    """
    Returns settings object for the tpRigBuilder Data library
    :return: JSONSettings
    """

    settings_path = get_library_settings_path()
    library_settings = settings.JSONSettings(directory=os.path.dirname(settings_path), filename=os.path.basename(settings_path))

    return library_settings


def get_rig_builder_directory():
    """
    Returns RigBuilder directory
    :return: str
    """

    file_path = osplatform.get_env_var('RIGBUILDER_PATH')
    file_path = path_utils.clean_path(file_path)

    return file_path


def get_data_files_directory():
    """
    Returns path where data files for tpRigToolkit.tools.rigbuilder are located
    :return: str
    """

    return os.path.join(get_rig_builder_directory(), 'data')
