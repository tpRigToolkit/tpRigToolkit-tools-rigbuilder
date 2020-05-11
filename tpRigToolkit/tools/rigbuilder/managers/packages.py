#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains packages manager
"""

from __future__ import print_function, division, absolute_import

import os
import pkgutil
import logging
import traceback

from tpDcc.libs.python import decorators, python, path as path_utils

from tpRigToolkit.tools.rigbuilder import register
from tpRigToolkit.tools.rigbuilder import packages
from tpRigToolkit.tools.rigbuilder.core import package

LOGGER = logging.getLogger('tpRigToolkit')


class PackagesManager(object):

    ENV_VAR_NAME = 'RIGBUILDER_PACKAGE_PATHS'
    ENV_VAR_PATHS_DELIMITER = ';'

    def __init__(self, packages_paths=None):
        super(PackagesManager, self).__init__()

        self._registered_packages = dict()
        self._registered_package_paths = dict()
        self._registered_bueprints = dict()

        self._package_paths = python.force_list(packages_paths) if packages_paths else list()
        self._update_package_paths_from_environment()

    @property
    def registered_packages(self):
        return self._registered_packages

    @property
    def registered_package_paths(self):
        return self._registered_package_paths

    @property
    def registered_blueprints(self):
        return self._registered_bueprints

    def initialize(self):
        """
        Initializes packages manager
        """

        self._load_packages()

    def register_package_path(self, package_path):
        """
        Registers given path into the manager so path is taking into account when loading packages
        :param package_path: str
        """

        package_paths = python.force_list(package_path)

        valid_paths = list()

        for package_path in package_paths:
            if not package_path or not os.path.isdir(package_path) or package_path in self._package_paths:
                continue
            self._package_paths.append(package_path)
            valid_paths.append(package_path)

        if valid_paths:
            self._load_packages(valid_paths)

    def get_package_by_name(self, package_name):
        """
        Returns package with given name if exists
        :param package_name: str, name of the package to search for
        :return: Package or None
        """

        if package_name not in self._registered_packages:
            return None

        return self._registered_packages[package_name]

    def _load_packages(self, package_path=None):
        """
        Internal function that loads all available packages
        :param package_path: str
        """

        if not package_path:
            package_paths = self._package_paths
        else:
            package_paths = python.force_list(package_path)

        for importer, pkg_name, is_pkg in pkgutil.iter_modules(package_paths):
            try:
                if is_pkg:
                    pkg = importer.find_module(pkg_name).load_module(pkg_name)
                    pkg_path = pkg.__path__[0]
                    if hasattr(pkg, 'PACKAGE_NAME'):
                        package_name = pkg.MODULE_NAME
                    else:
                        package_name = pkg_name
                    pkg_class = type(pkg_name, (package.Package,), {})
                    new_package = pkg_class(pkg_path)
                    self._registered_packages[package_name] = new_package
                    self._registered_package_paths[package_name] = path_utils.clean_path(pkg_path)
            except Exception as exc:
                LOGGER.error('Error on Package: {} : \n\t{}'.format(pkg_name, exc))
                LOGGER.error(traceback.format_exc())
                continue

        for name, pkg in self._registered_packages.items():
            package_name = pkg.__class__.__name__
            for n in pkg.builder_node_classes.values():
                n.PACKAGE_NAME = package_name

    def _update_package_paths_from_environment(self):
        """
        Internal function that updates registered package paths by taking into account current environment variables
        """

        def _recurse_package_paths(module_path):
            """
            Recursively loops through given path searching packages
            :param module_path: str
            :return: list(str)
            """

            paths_found = list()
            for sub_folder in os.listdir(module_path):
                sub_folder_path = os.path.join(module_path, sub_folder)
                if os.path.isdir(sub_folder_path):
                    if sub_folder_path.endswith('Package') or sub_folder_path.endswith('package'):
                        paths_found.append(sub_folder_path)

            return paths_found

        packages_paths = packages.__path__

        if self.ENV_VAR_NAME in os.environ:
            extra_paths = os.environ.get(self.ENV_VAR_NAME).rstrip(self.ENV_VAR_PATHS_DELIMITER)
            for modules_root in extra_paths.split(self.ENV_VAR_PATHS_DELIMITER):
                if os.path.isdir(modules_root):
                    paths = _recurse_package_paths(modules_root)
                    extra_paths.extend(paths)

            packages_paths.extend(extra_paths)

        for p in packages_paths:
            self.register_package_path(p)


@decorators.Singleton
class PackagesManagerSingleton(PackagesManager, object):
    def __init__(self):
        PackagesManager.__init__(self)


register.register_class('PkgsMgr', PackagesManagerSingleton)
