#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains rig item implementation
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *

from tpDcc.libs.python import path as path_utils

from tpRigToolkit.tools.rigbuilder.items import base
from tpRigToolkit.tools.rigbuilder.objects import helpers, rig


class RigItem(base.BaseItem, object):
    def __init__(self, directory, name, library, parent_item=None):

        self._directory = directory
        self._library = library
        self._name = name

        self._rig = None
        self._detail = False
        self._folder = False

        super(RigItem, self).__init__(parent=parent_item)

        split_name = name.split('/')
        self.setText(0, split_name[-1])
        self.setSizeHint(0, QSize(50, 20))

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def text(self, column):
        """
        Overrides base QTreeWidgetItem text function
        Used to cleanup text spaces
        :param column: int
        :return: str
        """

        text = super(RigItem, self).text(column)
        text = text.strip()
        return text

    def setText(self, column, text):
        """
        Overrides base QTreeWidgetItem setText function
        We add custom space text
        :param column: int
        :param text: str
        """

        text = '   ' + text
        super(RigItem, self).setText(column, text)

    def setData(self, column, role, value):
        """
        Overrides base QTreeWidgetItem setData function
        :param column: int
        :param role: QRole
        :param value: variant
        """

        super(RigItem, self).setData(column, role, value)

        rig = self._get_rig()
        if not rig:
            return

        if hasattr(rig, 'filepath') and not rig.filepath:
            return

        if role == Qt.CheckStateRole:
            if value == 0:
                rig.set_enabled(False)
            if value == 2:
                rig.set_enabled(True)

    def create(self):
        """
        Implements BaseItem create function
        Creates the rig of this item
        """

        if self.is_folder():
            return

        rig_inst = self._get_rig()
        if rig_inst.is_rig():
            return

        rig_inst.create()

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def get_name(self):
        """
        Returns the name of the rig
        :return: str
        """

        rig_inst = self._get_rig()
        return rig_inst.get_name()

    def set_name(self, name):
        """
        Set the name of the rig item
        :param name: str
        """

        self._name = name

    def get_path(self):
        """
        Returns the full path to the rig folder
        If the rig has not been create d yet, the rig directory will be return
        :return: str
        """

        rig_inst = self._get_rig()
        return rig_inst.get_path()

    def library(self):
        """
        Returns library linked to this item
        :return: Library
        """

        return self._library

    def set_library(self, library):
        """
        Sets library linked to this item
        :param library: Library
        """

        self._library = library

    def is_folder(self):
        """
        Returns whether the task is a folder or not
        :return: bool
        """

        return self._folder

    def get_directory(self):
        """
        Returns the directory of the task item
        :return: str
        """

        return self._directory

    def set_directory(self, directory):
        """
        Sets the directory of the task item
        :param directory: str
        """

        self._directory = directory

    def set_folder(self, flag):
        """
        Sets whether the rig is a folder or not
        :param flag: bool
        """

        self._folder = flag
        self.setDisabled(flag)

    def get_rig(self):
        """
        Returns the rig of the item
        :return: Rig
        """

        return self._get_rig()

    def get_parent_rig(self):
        """
        Returns the parent rig of the item
        :return: variant, Rig or None
        """

        return self._get_parent_rig()

    def rename(self, name):
        """
        Renames the rig item
        :param name: str, new name of the rig
        :return: bool, Whether the operation was successful or not
        """

        rig_inst = self._get_rig()
        state = rig_inst.rename(name)
        if state:
            self._name = name

        return state

    def has_parts(self):
        """
        Returns whether the current item has sub rigs or not
        :return: bool
        """

        rig_path = path_utils.join_path(self._directory, self._name)
        rigs, folders = helpers.RigHelpers.find_rigs(rig_path, return_also_non_objects_list=True)
        if rigs or folders:
            return True

        return False

    # ================================================================================================
    # ======================== INTERNAL
    # ================================================================================================

    def _add_rig(self, directory, name, library):
        """
        Internal function that links a new Rig to this item
        :param directory: str, directory of the rig
        :param name: str, name of the rig
        """

        self._rig = rig.RigObject(name=name)
        self._rig.set_directory(directory)
        self._rig.set_library(library)

        self._rig.create()

    def _get_rig(self):
        """
        Internal function that returns the rig of the item
        :return: Rig
        """

        rig_inst = rig.RigObject(name=self._name)
        rig_inst.set_directory(self._directory)
        rig_inst.set_library(self.library())

        return rig_inst

    def _get_parent_rig(self):
        """
        Internal function that returns, if exists, the parent rig of the current rig
        :return: variant, Rig or None
        """

        rig_inst = rig.RigObject(name=self._name)
        parent_rig = rig_inst.get_parent_rig()

        return parent_rig
