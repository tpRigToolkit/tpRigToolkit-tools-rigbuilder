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
import string
import logging
import __builtin__      # Not remove because its used to clean rig script builtins

import tpDccLib as tp
from tpPyUtils import folder, path as path_utils

from tpRigToolkit.tools.rigbuilder.core import consts

LOGGER = logging.getLogger('tpRigToolkit')


def show_list_to_string(*args):
    """
    Converts given arguments into a string
    :param args: list(variant)
    :return: str
    """

    try:
        if args is None:
            return 'None'
        if not args:
            return ''

        new_args = list()
        for arg in args:
            if args is not None:
                new_args.append(str(arg))
        args = new_args
        if not args:
            return ''

        string_value = string.join(args).replace('\n', '\t\n')
        if string_value.endswith('\t\n'):
            string_value = string_value[:-2]

        return string_value
    except RuntimeError as e:
        raise RuntimeError(e)


def show(*args):
    """
    Helper function that prints given arguments into proper Dcc logs and temp logger
    :param args: list(variant)
    """

    try:
        string_value = show_list_to_string(*args)
        log_value = string_value.replace('\n', '\nLOG:\t\t')
        text = '\t\t{}'.format(string_value)
        print(text)
        log.record_temp_log(tpRigBuilder.logger.name, '\n{}'.format(log_value))
    except RuntimeError as e:
        text = '\t\tCould not show {}'.format(args)
        print(text)
        log.record_temp_log(tpRigBuilder.logger.name, '\n{}'.format(log_value))
        raise RuntimeError(e)


def warning(*args):
    """
    Helper function that prints given arguments as warning into proper Dcc logs and temp logger
    :param args: list(variant)
    """

    try:
        string_value = show_list_to_string(*args)
        log_value = string_value.replace('\n', '\nLOG:\t\t')
        text = '[WARNING]\t{}'.format(string_value)
        if not tp.is_maya():
            print(text)
        else:
            tp.Dcc.warning('LOG: \t{}'.format(string_value))

        log.record_temp_log(tpRigBuilder.logger.name, '\n[WARNING]: {}'.format(log_value))
    except RuntimeError as e:
        raise RuntimeError(e)


def error(*args):
    """
    Helper function that prints given arguments as error into proper Dcc logs and temp logger
    :param args: list(variant)
    """

    try:
        string_value = show_list_to_string(*args)
        log_value = string_value.replace('\n', '\nLOG:\t\t')
        text = '[ERROR]\t{}'.format(string_value)
        print(text)
        log.record_temp_log(LOGGER.name, '\n[ERROR]: {}'.format(log_value))
    except RuntimeError as e:
        raise RuntimeError(e)


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


def get_code_builtins(script_object):
    """
    Returns all current code builtins of the given script object
    :param script_object: ScriptObject
    :return: dict
    """

    builtins = {'script_object': script_object, 'show': show, 'warning': warning}
    if tp.is_maya():
        import maya.cmds as cmds
        import pymel.all as pymel
        maya_builtins = {'cmds': cmds, 'mc': cmds, 'pymel': pymel, 'pm': pymel}
        for builtin in maya_builtins:
            builtins[builtin] = maya_builtins[builtin]

    return builtins


def setup_code_builtins(script_object):
    """
    Setup given rig builtins
    :param script_object: ScriptObject
    """

    builtins = get_code_builtins(script_object)
    for builtin in builtins:
        try:
            exec ('del(__builtin__.%s)' % builtin)
        except Exception:
            pass
        builtin_value = builtins[builtin]
        exec '__builtin__.%s = builtin_value' % builtin


def reset_code_bultins(script_object):
    """
    Reset given rig builtins
    :param script_object: ScriptObject
    """

    builtins = get_code_builtins(script_object)
    for builtin in builtins:
        try:
            exec('del(__builtin__.{}'.format(builtin))
        except Exception:
            pass
