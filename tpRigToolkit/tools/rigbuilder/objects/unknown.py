#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains build node implementation for unknown nodes
"""

from __future__ import print_function, division, absolute_import

from tpRigToolkit.tools.rigbuilder.objects import build


class UnknownNode(build.BuildObject, object):

    COLOR = [125, 125, 125]
    SHORT_NAME = 'MISS'
    DESCRIPTION = 'Unknown node'
    ICON = 'question'

    def __init__(self, name=None, rig=None):
        super(UnknownNode, self).__init__(name=name, rig=rig)

    def run(self, **kwargs):
        pass
