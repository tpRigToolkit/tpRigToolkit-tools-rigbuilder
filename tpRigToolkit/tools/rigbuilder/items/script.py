#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains item implementation for scripts
"""

from __future__ import print_function, division, absolute_import

import os

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc
from tpDcc.libs.python import fileio, path as path_utils

import tpRigToolkit
from tpRigToolkit.tools.rigbuilder.items import base


class ScriptItemSignals(QObject, object):

    createPythonCode = Signal()
    createDataImport = Signal()
    runCode = Signal()
    runCodeGroup = Signal()
    renameCode = Signal()
    duplicateCode = Signal()
    deleteCode = Signal()
    setStartPoint = Signal()
    cancelStartPoint = Signal()
    setBreakPoint = Signal()
    cancelBreakPoint = Signal()
    browseCode = Signal()


class ScriptItem(base.BaseItem, object):

    scriptSignals = ScriptItemSignals()

    def __init__(self, parent=None):
        super(ScriptItem, self).__init__(parent)

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def _create_context_menu(self):
        """
        Overrides base BuildItem create_context_menu function
        Creates context menu for this item
        :return: QMenu
        """

        self._context_menu = QMenu()

        python_icon = tpDcc.ResourcesMgr().icon('python')
        import_icon = tpDcc.ResourcesMgr().icon('import')
        play_icon = tpDcc.ResourcesMgr().icon('play')
        rename_icon = tpDcc.ResourcesMgr().icon('rename')
        duplicate_icon = tpDcc.ResourcesMgr().icon('clone')
        delete_icon = tpDcc.ResourcesMgr().icon('delete')
        browse_icon = tpDcc.ResourcesMgr().icon('open')
        external_icon = tpDcc.ResourcesMgr().icon('external')
        new_window_icon = tpDcc.ResourcesMgr().icon('new_window')
        cancel_icon = tpDcc.ResourcesMgr().icon('cancel')
        start_icon = tpDcc.ResourcesMgr().icon('start')
        flag_icon = tpDcc.ResourcesMgr().icon('finish_flag')

        new_python_action = self._context_menu.addAction(python_icon, 'New Python Code')
        new_data_import_action = self._context_menu.addAction(import_icon, 'New Data Import')
        self._context_menu.addSeparator()
        run_action = self._context_menu.addAction(play_icon, 'Run')
        run_group_action = self._context_menu.addAction(play_icon, 'Run Group')
        self._context_menu.addSeparator()
        rename_action = self._context_menu.addAction(rename_icon, 'Rename')
        duplicate_action = self._context_menu.addAction(duplicate_icon, 'Duplicate')
        delete_action = self._context_menu.addAction(delete_icon, 'Delete')
        self._context_menu.addSeparator()
        set_start_point_action = self._context_menu.addAction(start_icon, 'Set Start Point')
        cancel_start_point_action = self._context_menu.addAction(cancel_icon, 'Cancel Start Point')
        self._context_menu.addSeparator()
        set_break_point_action = self._context_menu.addAction(flag_icon, 'Set Break Point')
        cancel_break_point_action = self._context_menu.addAction(cancel_icon, 'Cancel Break Point')
        self._context_menu.addSeparator()
        browse_action = self._context_menu.addAction(browse_icon, 'Browse')
        external_window_action = self._context_menu.addAction(external_icon, 'Open in External')
        new_window_action = self._context_menu.addAction(new_window_icon, 'Open in New Window')

        new_python_action.triggered.connect(self.scriptSignals.createPythonCode.emit)
        new_data_import_action.triggered.connect(self.scriptSignals.createDataImport.emit)
        run_action.triggered.connect(self.scriptSignals.runCode.emit)
        run_group_action.triggered.connect(self.scriptSignals.runCodeGroup.emit)
        rename_action.triggered.connect(self.scriptSignals.renameCode.emit)
        duplicate_action.triggered.connect(self.scriptSignals.duplicateCode.emit)
        delete_action.triggered.connect(self.scriptSignals.deleteCode.emit)
        set_start_point_action.triggered.connect(self.scriptSignals.setStartPoint.emit)
        cancel_start_point_action.triggered.connect(self.scriptSignals.cancelStartPoint.emit)
        set_break_point_action.triggered.connect(self.scriptSignals.setBreakPoint.emit)
        cancel_break_point_action.triggered.connect(self.scriptSignals.cancelBreakPoint.emit)
        browse_action.triggered.connect(self.scriptSignals.browseCode.emit)
        external_window_action.triggered.connect(self._on_open_in_external)
        new_window_action.triggered.connect(self._on_open_in_window)

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def get_code_name(self, remove_extension=False):
        """
        Returns item code path
        :return: str
        """

        script_name = path_utils.get_basename(self.get_text(), with_extension=False)
        script_path = self.get_path()
        if script_path:
            script_name = path_utils.join_path(script_path, script_name)

        if remove_extension:
            return fileio.remove_extension(script_name)

        return script_name

    # ================================================================================================
    # ======================== CALLBACKS
    # ================================================================================================

    def _on_open_in_external(self):
        """
        Internal callback function that opens script in external editor
        :param item: ScripItem
        :return:
        """

        current_object = self.get_object()
        if not current_object:
            tpRigToolkit.logger.warning('Impossible to open script because object is not defined!')
            return

        code_name = self.get_code_name(remove_extension=True)
        code_file = current_object.get_code_file(code_name)
        if not code_file or not os.path.isfile(code_file):
            tpRigToolkit.logger.warning('Impossible to open script "{}" because it does not exists!'.format(code_file))
            return

        # TODO: Add support for custom external editors
        # external_editor = self._settings.get('external_directory')
        # if external_editor:
        #     p = subprocess.Popen([external_editor, code_file])

        fileio.open_browser(code_file)

    def _on_open_in_window(self, item=None):
        """
        Internal callback function that opens script in script editor
        :param item: ScripItem
        :return:
        """

        current_object = self.get_object()
        if not current_object:
            tpRigToolkit.logger.warning('Impossible to open script because object is not defined!')
            return

        code_name = self.get_code_name(remove_extension=True)
        code_file = current_object.get_code_file(code_name)
        if not code_file or not os.path.isfile(code_file):
            tpRigToolkit.logger.warning('Impossible to open script "{}" because it does not exists!'.format(code_file))
            return

        raise NotImplementedError('open in new window functionality is not implemented yet!')

