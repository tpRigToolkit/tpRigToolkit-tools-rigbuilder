#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Initialization module for tpRigToolkit.tools.rigbuilder
"""

from __future__ import print_function, division, absolute_import

import os

from tpPyUtils import settings


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
