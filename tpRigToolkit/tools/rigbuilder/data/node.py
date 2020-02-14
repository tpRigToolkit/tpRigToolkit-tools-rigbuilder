#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains core data widgets for tpRigToolkit.tools.rigbuilder
"""

from __future__ import print_function, division, absolute_import

import os
import logging

from tpPyUtils import yamlio, path as path_utils
from tpDccLib.core import data

from tpRigToolkit.tools.rigbuilder.core import consts

LOGGER = logging.getLogger('tpRigToolkit')


class NodeData(data.FileData, object):
    """
    Class used to define Python scripts stored in disk files
    """

    @staticmethod
    def get_data_type():
        return consts.DataTypes.Node

    @staticmethod
    def get_data_extension():
        return 'yml'

    @staticmethod
    def get_data_title():
        return 'Builder Node'

    def open(self):
        lines = ''
        return lines

    def create(self, builder_node):
        if not builder_node:
            LOGGER.warning(
                'Impossible to create new Bulder Node becasue no builder node instancer given!'.format(builder_node))
            return

        data = {
            'class': builder_node.__name__,
            'package': builder_node.PACKAGE_NAME
        }
        file_path = path_utils.clean_path(os.path.join(self.directory, '{}.{}'.format(self.name, self.extension)))
        self.file = yamlio.write_to_file(data, file_path)
