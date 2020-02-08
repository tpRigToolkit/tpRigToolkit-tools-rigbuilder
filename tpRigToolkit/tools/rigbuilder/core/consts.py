#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains constants definitions for tpRigToolkit.tools.rigbuilder
"""

from __future__ import print_function, division, absolute_import

from tpDccLib.core import scripts


BLUEPRINTS_FOLDER = '__blueprints__'
BLUEPRINTS_DATA_FILE = 'data.yml'
BLUEPRINTS_OPTIONS_FILE = 'options.yml'


class DataTypes(object):
    """
    Class that defines all data types found in tpRigToolkit.tools.rigbuilder
    """

    Unknown = scripts.ScriptTypes.Unknown
    Python = scripts.ScriptTypes.Python
    Manifest = scripts.ScriptTypes.Manifest
    Blueprint = 'Blueprint'
