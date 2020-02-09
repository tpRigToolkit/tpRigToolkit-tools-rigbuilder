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

from Qt.QtWidgets import *

from tpQtLib.widgets import messagebox

import tpRigToolkit


def show_rename_dialog(title, message, input_text):
    """
    Shows the rename dialog
    """

    tool_info = tpRigToolkit.ToolsMgr().get_tool_data_from_id('tpRigToolkit-tools-rigbuilder')
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

    tool_info = tpRigToolkit.ToolsMgr().get_tool_data_from_id('tpRigToolkit-tools-rigbuilder')
    if not tool_info or not tool_info.get('attacher', None):
        return messagebox.MessageBox.question(None, title, text)
    else:
        attacher = tool_info['attacher']
        return messagebox.MessageBox.question(None, title, text, theme_to_apply=attacher.theme())
