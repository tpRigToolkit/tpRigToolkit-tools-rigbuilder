#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains functions to interact with tpRigBuilder API
"""

import tpDcc as tp
from tpDcc.libs.qt.widgets import project

import tpRigToolkit
from tpRigToolkit.tools import rigbuilder
from tpRigToolkit.tools.rigbuilder.core import consts, project as project_rigbuilder, rigbuilder as core_rigbuilder


def reload_rigbuilder():
    """
    Reloads rigbuilder tool
    """

    tp.ToolsMgr().get_tool_by_id('tpRigToolkit-tools-rigbuilder', do_reload=True)


def get_project_by_name(projects_path, project_name):
    """
    Returns a project located in the given path and with the given name (if exists)
    :param projects_path: str
    :param project_name: str
    :return: Project or None
    """

    return project.get_project_by_name(projects_path, project_name, project_class=project_rigbuilder.RigBuilderProject)


def get_projects(projects_path):
    """
    Returns all projects located in given path
    :param projects_path: str
    :return: list(Project)
    """

    return project.get_projects(projects_path, project_class=project_rigbuilder.RigBuilderProject)


def get_current_project():
    """
    Returns project currently being used by rigbuilder
    :return: RigBuilderProject
    """

    if not hasattr(rigbuilder, 'project'):
        return None

    return rigbuilder.project


def set_project(project_inst):
    """
    Sets the project used by tpRigBuilder
    :param project_inst: Project
    """

    core_rigbuilder.init()
    rigbuilder.project = project_inst
    if project_inst:
        rigbuilder.project.naming_lib.load_session()


def solve_name(*args, **kwargs):
    """
    Resolves name with given rule and attributes
    :param args: list
    :param kwargs: str
    """

    kwargs['unique_name'] = True

    solved_name = tpRigToolkit.NamesMgr().solve_name(*args, **kwargs)

    return solved_name


def parse_name(node_name, rule_name=None, ):
    """
    Parse a current solved name and return its different fields (metadata information)
    :param node_name: str
    :param rule_name: str
    :param use_auto_suffix: bool
    :return: dict(str)
    """

    return tpRigToolkit.NamesMgr().parse_name(node_name=node_name, rule_name=rule_name)


def get_sides():
    """
    Returns sides being used
    This is the order that is used to check the list of available sides
        1) Check if project has already a dict option called sides. Default side will be the first side in the list.
        2) Check project nomenclature rule looking for a rule called side
        3) Default sides for tpRigToolkit will be used
    :return: List of sides and default one
    :rtype: list(str), str
    """

    current_project = rigbuilder.project
    if current_project:
        # Check project options
        if current_project.has_option('sides'):
            sides = current_project.get_option('sides')
            if sides:
                default_side = sides[0]
                return sides, default_side
        # Check project nomenclature
        name_lib = current_project.naming_lib
        side_token = name_lib.get_token('side')
        if side_token:
            token_items = side_token.get_items().keys()
            token_default = side_token.default or 1
            token_default_value = token_items[token_default - 1] if token_items else ''
            return token_items, token_default_value
    else:
        # Default fallback
        return consts.DEFAULT_SIDES, consts.DEFAULT_SIDE


def get_default_side():
    """
    Returns current default side used by the project
    :return: str
    """

    sides, default_side = get_sides()

    return default_side


def get_color_of_side(side, sub_color=False):
    """
    Returns override color of the given side
     This is the order that is used to check the list of available sides
        1) Check if project has already side colors defined.
        2) Default sides for DCC will be used
    :param side: str
    :param sub_color: fool, whether to return a sub color or not
    :return:
    """

    current_project = rigbuilder.project
    if current_project:
        side_color = None
        groups = ['Controls', 'controls'] if not sub_color else ['SubControls', 'subcontrols']
        for group in groups:
            if current_project.has_option(side, group=group):
                side_color = current_project.get_option(side, group=group)
            elif current_project.has_option(side, group=group):
                side_color = current_project.get_option(side, group=group)
            if side_color:
                break
        if side_color:
            return side_color
    else:
        return tp.Dcc.get_color_of_side(side=side, sub_color=sub_color)
