#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains data manager widgets
"""

from __future__ import print_function, division, absolute_import

import pkgutil
import inspect
import logging
import traceback

from tpPyUtils import path, decorators
from tpQtLib.widgets.library import manager

from tpRigToolkit.tools.rigbuilder import register
from tpRigToolkit.tools.rigbuilder.core import data

LOGGER = logging.getLogger('tpRigToolkit')


class DataManager(manager.LibraryManager, object):
    def __init__(self, settings=None, update_on_init=True):
        super(DataManager, self).__init__(settings=settings)

        self._directories = list()

        if update_on_init:
            self.update_data_classes()

    def add_directory(self, directory, do_update=False):
        """
        Adds a new directory where data should be find
        :param directory: str
        :param do_update: bool
        """

        if directory not in self._directories:
            self._directories.append(directory)
            if do_update:
                self.update_data_classes()

    def set_directories(self, directories):
        """
        Sets the directories where data should be find
        :param directories: list(str)
        """

        new_dir = False
        for d in directories:
            if d not in self._directories:
                new_dir = True
                self._directories.append(d)

        if new_dir:
            self.update_data_classes()

    def update_data_classes(self, do_reload=False):
        """
        Adds custom dat files located in the current data manager registered directories
        """

        data_classes = list()
        for d in self._directories:
            data_classes.extend(self._load_data_classes(d))

        for data_cls in data_classes:
            self.register_item(data_cls)

    def _load_data_classes(self, directory, do_reload=False):
        """
        Internal function that loads data classes
        :param directory: str
        :param do_reload: bool
        :return: list
        """

        data_classes = list()

        if directory is None or not path.is_dir(directory):
            LOGGER.warning('Data Path {} does not exists!'.format(directory))
            return data_classes

        for loader, mod_name, is_package in pkgutil.walk_packages([directory]):
            try:
                print('Module Name: {}'.format(mod_name))
                module = loader.find_module(mod_name).load_module(mod_name)
                if do_reload:
                    reload(module)
                for cname, obj in inspect.getmembers(module, inspect.isclass):
                    if not issubclass(obj, data.DataItem):
                        continue
                    data_classes.append(obj)
            except Exception as e:
                LOGGER.warning('Aborting loading Data Class {} : {}'.format(mod_name, str(e)))
                LOGGER.error(traceback.format_exc())

        for data_cls in data_classes:
            print('Data Class: {}'.format(data_cls))

        return sorted(list(set(data_classes)))


@decorators.Singleton
class DataManagerSingleton(DataManager, object):
    def __init__(self):
        DataManager.__init__(self)


register.register_class('DataMgr', DataManagerSingleton)
