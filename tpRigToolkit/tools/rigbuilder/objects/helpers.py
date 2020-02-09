#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains helpers functions for objects in tpRigToolkit.tools.rigbuilder
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os
import logging

from tpPyUtils import folder, path as path_utils

from tpRigToolkit.tools.rigbuilder.core import consts

LOGGER = logging.getLogger('tpRigToolkit')


def is_object(directory):
    """
    Returns whether the given directory contains a valid build object or not
    :param directory: str, directory to check if it contains objects or not
    :return: bool
    """

    if not directory or not path_utils.is_dir(directory):
        return False

    code_path = path_utils.join_path(directory, consts.CODE_FOLDER)
    if not path_utils.is_dir(code_path):
        return False

    return True


def get_object(directory, object_class=None):
    """
    Returns object if the given directory is a valid one
    :param directory: str
    :param object_class: cls
    :return: object or not
    """

    if not is_object(directory):
        return

    if not object_class:
        from tpRigToolkit.tools.rigbuilder.objects import build
        object_class = build.BuildObject

    new_object = object_class(os.path.basename(directory))
    new_object.set_directory(os.path.dirname(directory))

    return new_object


def find_objects(directory=None, return_also_non_objects_list=False):
    """
    Will try to find the objects in the given directory
    If no directory is given, it will search in teh current working directory
    :param directory: str, directory to search for objects
    :param return_also_non_objects_list: bool
    :return: list<str>, objects in the given directory
    """

    if not directory:
        directory = folder.get_current_working_directory()

    LOGGER.debug('Finding objects on "{}"'.format(directory))

    found = list()
    non_found = list()
    for root, dirs, files in os.walk(directory):
        for d in dirs:
            try:
                full_path = path_utils.join_path(root, d)
            except Exception:
                pass
            if is_object(full_path):
                found.append(d)
                continue
            elif return_also_non_objects_list:
                if not d.startswith(consts.FOLDERS_PREFIX) and not d.endswith(
                        consts.FOLDERS_SUFFIX) and d != 'Trash':
                    non_found.append(d)
        break

    if not return_also_non_objects_list:
        return found
    else:
        return [found, non_found]
