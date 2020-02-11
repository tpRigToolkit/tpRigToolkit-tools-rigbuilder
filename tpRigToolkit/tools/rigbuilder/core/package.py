#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains base class to create tpRigBuilder packages
"""

import os
import pkgutil
import inspect
import logging

LOGGER = logging.getLogger('tpRigToolkit')


class Package(object):
    """
    Base class that defines packages that can be used to extend tpRigToolkit.tools.rigbuilder functionality
    """

    def __init__(self, package_path):
        super(Package, self).__init__()

        self._package_path = package_path

        self._builder_node_classes = dict()
        self._builder_node_paths = dict()
        self._blueprint_classes = dict()
        self._blueprint_paths = dict()

        self.load()

    @property
    def package_path(self):
        """
        Returns path where package is located
        :return: str
        """

        return self._package_path

    @property
    def builder_node_classes(self):
        return self._builder_node_classes

    @property
    def builder_node_paths(self):
        return self._builder_node_paths

    @property
    def blueprint_classes(self):
        return self._blueprint_classes

    @property
    def blueprint_paths(self):
        return self._blueprint_paths

    def load(self):
        """
        Load info of the package
        """

        from tpRigToolkit.tools.rigbuilder.objects import node

        if not self._package_path or not os.path.isdir(self._package_path):
            LOGGER.warning('Package path is not valid "{}"!'.format(self._package_path))
            return

        for importer, pkg_name, is_pkg in pkgutil.walk_packages([self._package_path]):
            pkg = importer.find_module(pkg_name).load_module(pkg_name)
            for cname, obj in inspect.getmembers(pkg, inspect.isclass):
                obj_name = obj.__name__
                try:
                    obj_path = inspect.getfile(obj)
                except Exception as exc:
                    continue

                if issubclass(obj, node.BuilderNode):
                    self._builder_node_classes[obj_name] = obj
                    self._builder_node_paths[obj_name] = obj_path
                    print('Found Builder Node: {}'.format(obj, obj_path))
