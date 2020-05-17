#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains functions to interact with tpRigBuilder API
"""

import tpDcc as tp
from tpDcc.libs.qt.widgets import project

import tpRigToolkit
from tpRigToolkit.tools import rigbuilder
from tpRigToolkit.tools.rigbuilder.core import project as project_rigbuilder, rigbuilder as core_rigbuilder


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

    use_auto_suffix = kwargs.pop('use_auto_suffix', True)
    node_type = kwargs.get('node_type', None)
    if use_auto_suffix and node_type:
        auto_suffixes = tpRigToolkit.NamesMgr().get_auto_suffixes() or dict()
        if node_type in auto_suffixes:
            kwargs['node_type'] = auto_suffixes[node_type]

    solved_name = tpRigToolkit.NamesMgr().solve_name(*args, **kwargs)

    return tp.Dcc.find_unique_name(solved_name)


def parse_name(node_name, rule_name=None, ):
    """
    Parse a current solved name and return its different fields (metadata information)
    :param node_name: str
    :param rule_name: str
    :param use_auto_suffix: bool
    :return: dict(str)
    """

    return tpRigToolkit.NamesMgr().parse_name(node_name=node_name, rule_name=rule_name)
