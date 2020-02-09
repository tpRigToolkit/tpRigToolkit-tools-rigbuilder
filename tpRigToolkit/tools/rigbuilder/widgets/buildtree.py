#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget for build tree
"""

from __future__ import print_function, division, absolute_import

from tpRigToolkit.tools.rigbuilder.widgets import basetree


class BuildItem(basetree.BaseItem, object):
    def __init__(self, parent=None):
        super(BuildItem, self).__init__(parent=parent)


class BuildTree(basetree.BaseTree, object):

    HEADER_LABELS = ['Build']
    ITEM_WIDGET = BuildItem
    NEW_ITEM_NAME = 'new_item'

    def __init__(self, settings=None, parent=None):
        super(BuildTree, self).__init__(settings=settings, parent=parent)

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def refresh(self):
        print('refreshgin ...')
