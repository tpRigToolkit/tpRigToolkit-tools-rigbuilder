#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains item implementation for scripts
"""

from __future__ import print_function, division, absolute_import

import os
import logging

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpPyUtils import fileio, path as path_utils

from tpRigToolkit.core import resource
from tpRigToolkit.tools.rigbuilder.items import base

LOGGER = logging.getLogger('tpRigToolkit')


class ScriptItemSignals(QObject, object):

    createPythonCode = Signal()
    createData = Signal()
    runCode = Signal()
    renameCode = Signal()
    duplicateCode = Signal()
    deleteCode = Signal()
    browseCode = Signal()


class ScriptItem(base.BaseItem, object):

    scriptSignals = ScriptItemSignals()

    def __init__(self, parent=None):

        self.handle_manifest = False

        super(ScriptItem, self).__init__(parent)

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def setData(self, column, role, value):
        """
        Overrides base QTreeWidgetItem setData function
        :param column: int
        :param role: QRole
        :param value: variant
        """

        super(ScriptItem, self).setData(column, role, value)

        if value == 0:
            check_state = Qt.Unchecked
        elif value == 2:
            check_state = Qt.Checked

        if role == Qt.CheckStateRole:
            if self.handle_manifest:
                tree = self.treeWidget()
                tree.update_scripts_manifest()
                if tree._shift_activate:
                    child_count = self.childCount()
                    for i in range(child_count):
                        child = self.child(i)
                        child.setCheckedState(column, check_state)
                        children = tree._get_ancestors(child)
                        for child in children:
                            child.setCheckedState(column, check_state)

    def _create_context_menu(self):
        """
        Overrides base BuildItem create_context_menu function
        Creates context menu for this item
        :return: QMenu
        """

        self._context_menu = QMenu()

        python_icon = resource.ResourceManager().icon('python')
        import_icon = resource.ResourceManager().icon('import')
        play_icon = resource.ResourceManager().icon('play')
        rename_icon = resource.ResourceManager().icon('rename')
        duplicate_icon = resource.ResourceManager().icon('clone')
        delete_icon = resource.ResourceManager().icon('delete')
        browse_icon = resource.ResourceManager().icon('open')
        external_icon = resource.ResourceManager().icon('external')
        new_window_icon = resource.ResourceManager().icon('new_window')

        new_python_action = self._context_menu.addAction(python_icon, 'New Python Code')
        new_data_import_action = self._context_menu.addAction(import_icon, 'New Data Import')
        self._context_menu.addSeparator()
        run_action = self._context_menu.addAction(play_icon, 'Run')
        rename_action = self._context_menu.addAction(rename_icon, 'Rename')
        duplicate_action = self._context_menu.addAction(duplicate_icon, 'Duplicate')
        delete_action = self._context_menu.addAction(delete_icon, 'Delete')
        self._context_menu.addSeparator()
        browse_action = self._context_menu.addAction(browse_icon, 'Browse')
        external_window_action = self._context_menu.addAction(external_icon, 'Open in External')
        new_window_action = self._context_menu.addAction(new_window_icon, 'Open in New Window')

        new_python_action.triggered.connect(self.scriptSignals.createPythonCode.emit)
        run_action.triggered.connect(self.scriptSignals.runCode.emit)
        rename_action.triggered.connect(self.scriptSignals.renameCode.emit)
        duplicate_action.triggered.connect(self.scriptSignals.duplicateCode.emit)
        delete_action.triggered.connect(self.scriptSignals.deleteCode.emit)
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
            LOGGER.warning('Impossible to open script because object is not defined!')
            return

        code_name = self.get_code_name(remove_extension=True)
        code_file = current_object.get_code_file(code_name)
        if not code_file or not os.path.isfile(code_file):
            LOGGER.warning('Impossible to open script "{}" because it does not exists!'.format(code_file))
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
            LOGGER.warning('Impossible to open script because object is not defined!')
            return

        code_name = self.get_code_name(remove_extension=True)
        code_file = current_object.get_code_file(code_name)
        if not code_file or not os.path.isfile(code_file):
            LOGGER.warning('Impossible to open script "{}" because it does not exists!'.format(code_file))
            return

        raise NotImplementedError('open in new window functionality is not implemented yet!')

