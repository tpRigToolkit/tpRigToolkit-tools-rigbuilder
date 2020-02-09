#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains constants definitions for tpRigToolkit.tools.rigbuilder
"""

from __future__ import print_function, division, absolute_import

from tpDccLib.core import scripts

FOLDERS_PREFIX = '__'
FOLDERS_SUFFIX = '__'
BLUEPRINTS_FOLDER = '__blueprints__'
CODE_FOLDER = '__code__'
DATA_FOLDER = '__data___'
BACKUP_FOLDER = '__backup__'
VERSIONS_FOLDER = '__versions__'
DATA_FILE = 'data'
VERSION_NAME = 'version'
MANIFEST_FILE = 'manifest'
SETTINGS_FILE_NAME = 'settings'
SETTINGS_FILE_EXTENSION = 'json'
OPTIONS_FILE_NAME = 'options'
OPTIONS_FILE_EXTENSION = 'json'


class DataTypes(object):
    """
    Class that defines all data types found in tpRigToolkit.tools.rigbuilder
    """

    Unknown = scripts.ScriptTypes.Unknown
    Python = scripts.ScriptTypes.Python
    Manifest = scripts.ScriptTypes.Manifest
    Blueprint = 'Blueprint'
