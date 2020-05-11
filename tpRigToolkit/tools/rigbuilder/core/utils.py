#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains utils functions and classes for tpRigToolkit.tools.rigbuilder
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os

from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.python import settings, osplatform, path as path_utils
from tpDcc.libs.qt.widgets import messagebox


def show_rename_dialog(title, message, input_text):
    """
    Shows the rename dialog
    """

    tool_info = tp.ToolsMgr().get_plugin_data_from_id('tpRigToolkit-tools-rigbuilder')
    if not tool_info or not tool_info.get('attacher', None):
        name, btn = messagebox.MessageBox.input(None, title, message, input_text=input_text)
    else:
        attacher = tool_info['attacher']
        name, btn = messagebox.MessageBox.input(
            None, title, message, input_text=input_text, theme_to_apply=attacher.theme())
    if btn == QDialogButtonBox.Ok:
        return name

    return None


def show_question_dialog(title, text):
    """
    Function that shows a question dialog to the user
    :param title: str
    :param text: str
    :return: QMessageBox.StandardButton
    """

    tool_info = tp.ToolsMgr().get_plugin_data_from_id('tpRigToolkit-tools-rigbuilder')
    if not tool_info or not tool_info.get('attacher', None):
        return messagebox.MessageBox.question(None, title, text)
    else:
        attacher = tool_info['attacher']
        return messagebox.MessageBox.question(None, title, text, theme_to_apply=attacher.theme())


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
    library_settings = settings.JSONSettings(
        directory=os.path.dirname(settings_path), filename=os.path.basename(settings_path))

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

    # TODO: We should add here the option to add data files from project also

    data_directories = [os.path.join(get_rig_builder_directory(), 'data')]
    if tp.is_maya():
        from tpRigToolkit.tools.rigbuilder.dccs.maya.core import utils
        data_directories.append(utils.get_data_files_directory())

    return data_directories


def get_script_files_directory():
    """
    Returns path where script files for tpRigToolkit.tools.rigbuilder are located
    :return: str
    """

    # TODO: We should add here the option to add data files from project also

    script_directories = [os.path.join(get_rig_builder_directory(), 'scripts')]
    if tp.is_maya():
        from tpRigToolkit.tools.rigbuilder.dccs.maya.core import utils
        script_directories.append(utils.get_script_files_directory())

    return script_directories