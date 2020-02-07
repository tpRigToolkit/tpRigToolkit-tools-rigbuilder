#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains project definition for tpRigToolkit.tools.rigbuilder
"""

from __future__ import print_function, division, absolute_import

from tpQtLib.widgets import project


class ProjectWidget(project.ProjectWidget, object):
    def __init__(self, parent=None):
        super(ProjectWidget, self).__init__(parent=parent)
