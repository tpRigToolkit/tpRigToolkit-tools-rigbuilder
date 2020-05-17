#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains build node implementation for node blocks
"""

from __future__ import print_function, division, absolute_import

from tpRigToolkit.tools.rigbuilder.objects import build


class NodeBlock(build.BuildObject, object):

    COLOR = [102, 153, 255]
    SHORT_NAME = 'BLOCK'
    DESCRIPTION = 'Block that contains other nodes'
    ICON = 'group_objects'

    def __init__(self, name=None, rig=None):
        super(NodeBlock, self).__init__(name=name, rig=rig)

    def run(self, **kwargs):
        return True
