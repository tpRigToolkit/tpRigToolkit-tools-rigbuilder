#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains core data widgets for tpRigBuilder
"""

from __future__ import print_function, division, absolute_import

import os

from Qt.QtCore import *
from Qt.QtWidgets import *

from tpPyUtils import path as path_utils

from tpQtLib.core import qtutils
from tpQtLib.widgets.library import manager

from tpQtLib.widgets.library import items, loadwidget

from tpRigToolkit.tools import rigbuilder
from tpRigToolkit.tools.rigbuilder.core import utils


class ScriptFolder(manager.LibraryDataFolder, object):
    def __init__(self, name, file_path, data_path=None):
        super(ScriptFolder, self).__init__(name=name, file_path=file_path, data_path=data_path)

    def get_manager(self):
        """
        Implements base manager.LibraryDataFolder get_manager function
        We use tpRigBuilder data manager
        :return: LibraryManager
        """

        return rigbuilder.ScriptsMgr()


class DataPreviewWidget(loadwidget.LoadWidget, object):
    def __init__(self, item, parent=None):
        super(DataPreviewWidget, self).__init__(item=item, parent=parent)

    def ui(self):
        super(DataPreviewWidget, self).ui()

        self._export_btn = QPushButton('Export')
        self._export_btn.setObjectName('exportButton')
        self._export_btn.setMinimumSize(QSize(60, 35))
        self._export_btn.setMaximumSize(QSize(125, 35))

        self._import_btn = QPushButton('Import')
        self._import_btn.setObjectName('impotButton')
        self._import_btn.setMinimumSize(QSize(60, 35))
        self._import_btn.setMaximumSize(QSize(125, 35))

        self._reference_btn = QPushButton('Reference')
        self._reference_btn.setObjectName('referenceButton')
        self._reference_btn.setMinimumSize(QSize(60, 35))
        self._reference_btn.setMaximumSize(QSize(125, 35))

        self._preview_buttons_lyt.addWidget(self._export_btn)
        self._preview_buttons_lyt.addWidget(self._import_btn)
        self._preview_buttons_lyt.addWidget(self._reference_btn)

        # By default, export button is disabled
        self._export_btn.setVisible(False)

    def setup_signals(self):
        super(DataPreviewWidget, self).setup_signals()

        self._export_btn.clicked.connect(self.export_data)
        self._import_btn.clicked.connect(self.import_data)
        self._reference_btn.clicked.connect(self.reference_data)

    def export_data(self):
        """
        Export data into hard disk
        """

        if not self.item():
            return

        comment = qtutils.get_comment(parent=self)
        if comment is None:
            return

        self.item().export_data(comment)

        self.update_history()

    def import_data(self):
        """
        Imports data into current scene
        """

        if not self.item():
            return

        self.item().import_data()

    def reference_data(self):
        """
        References data into current scene
        """

        if not self.item():
            return

        self.item().reference_data()


class DataItem(items.BaseItem, object):

    PreviewWidgetClass = DataPreviewWidget

    def __init__(self, *args, **kwargs):
        super(DataItem, self).__init__(*args, **kwargs)

        self._data_class = None
        self._data_object = None

    # OVERRIDES

    def settings(self):
        """
        Returns tpRigBuilder library settings file
        :return: JSONSettings
        """

        return utils.get_library_settings()

    def load(self, objects=None, namespaces=None, **kwargs):
        """
        Loads the data from the transfer object
        :param objects: list(str) or None
        :param namespaces: list(str) or None
        :param kwargs: dict
        """

        stored_path = path_utils.clean_path(os.path.join(self.path(), self.name()))
        data_object_path = path_utils.clean_path(self.data_object().get_file())
        if stored_path != data_object_path:
            self.show_error_dialog('Impossible to open file', 'Stored Path and Data Path are different: {}\n{}'.format(stored_path, data_object_path))
            return

        self.data_object().open(stored_path)

    def export_data(self, comment):
        """
        Export data from current scene
        :param comment: str
        """

        stored_path = path_utils.clean_path(os.path.join(self.path(), self.name()))
        data_object_path = path_utils.clean_path(self.data_object().get_file())
        if stored_path != data_object_path:
            self.show_error_dialog('Impossible to reference file',
                                   'Stored Path and Data Path are different: {}\n{}'.format(stored_path,
                                                                                            data_object_path))
            return

        self.data_object().export_data(comment)

    def import_data(self):
        """
        Imports data into current scene
        """

        stored_path = path_utils.clean_path(os.path.join(self.path(), self.name()))
        data_object_path = path_utils.clean_path(self.data_object().get_file())
        if stored_path != data_object_path:
            self.show_error_dialog('Impossible to reference file',
                                   'Stored Path and Data Path are different: {}\n{}'.format(stored_path,
                                                                                            data_object_path))
            return

        self.data_object().import_data(stored_path)

    def reference_data(self):
        """
        References data into current scene
        """

        stored_path = path_utils.clean_path(os.path.join(self.path(), self.name()))
        data_object_path = path_utils.clean_path(self.data_object().get_file())
        if stored_path != data_object_path:
            self.show_error_dialog('Impossible to import file',
                                   'Stored Path and Data Path are different: {}\n{}'.format(stored_path,
                                                                                            data_object_path))
            return

        self.data_object().reference_data(stored_path)

    # DATA

    def data_class(self):
        """
        Returns the data class for this item
        :return: Data
        """

        return self._data_class

    def set_data_class(self, class_name):
        """
        Sets the data class for this item
        :param class_name: str
        """

        if hasattr(class_name, 'get_data_extension()'):
            if class_name.Extension != '.{}'.format(class_name.get_data_extension()):
                LOGGER.error('Data class {} (.{}) has not the same extension as the data item: {} ({})'.format(class_name, class_name.get_data_extension(), self, self.Extension))
                return

        self._data_class = class_name

    def data_object(self, name=None, path=None):
        """
        Returns the data object for this item
        :param name: str
        :param path: str
        :return: Data
        """

        if not self._data_object:
            name = os.path.splitext(name or self.name())[0]
            path = path or self.path()
            self._data_object = self.data_class()(name, path)
            self._data_object.set_directory(path)

        return self._data_object
