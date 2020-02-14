#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains item implementation for build
"""

from __future__ import print_function, division, absolute_import

import os
import logging

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

from tpPyUtils import fileio, yamlio

from tpRigToolkit.tools import rigbuilder
from tpRigToolkit.core import resource
from tpRigToolkit.tools.rigbuilder.items import base

LOGGER = logging.getLogger('tpRigToolkit')


class BuildItemsDelegate(QItemDelegate, object):
    def __init__(self, parent=None):
        super(BuildItemsDelegate, self).__init__(parent)

    def paint(self, painter, option, index):
        if index.column() == 0:
            item = self.parent().itemFromIndex(index)
            if not item.node:
                super(BuildItemsDelegate, self).paint(painter, option, index)
            else:
                margin = 10
                mode = QIcon.Normal
                painter.setRenderHint(QPainter.Antialiasing)
                painter_path = QPainterPath()
                painter_rect = self._get_tag_rect(option.rect)
                painter_path.addRoundedRect(painter_rect, 5, 5)
                painter.fillPath(painter_path, QColor(*item.node.COLOR))
                painter.drawPath(painter_path)
                icon_rect = self._get_icon_rect(option.rect)
                # icon_rect = QRect(QPoint(), option.decorationSize)
                # icon_rect.moveCenter(option.rect.center())
                # icon_rect.setRight(option.rect.right() - margin)
                state = QIcon.On if option.state & QStyle.State_Open else QIcon.Off
                item.node.ICON.paint(painter, icon_rect, Qt.AlignRight | Qt.AlignVCenter, mode, state)
                tag_text_rect = self._get_text_rect(option.rect)
                text_font = QFont('Arial', 8)
                text_font.setBold(True)
                painter.setFont(text_font)
                painter.drawText(tag_text_rect, Qt.AlignCenter, item.node.SHORT_NAME)
                txt = QStyleOptionViewItem(option)
                super(BuildItemsDelegate, self).paint(painter, txt, index)
        else:
            super(BuildItemsDelegate, self).paint(painter, option, index)

    def _get_tag_rect(self, item_rect):
        return QRect(45, item_rect.top() + 3, 65, item_rect.height() - 3)

    def _get_icon_rect(self, item_rect):
        return QRect(45, item_rect.top() + 5, 20, item_rect.height() - 5)

    def _get_text_rect(self, item_rect):
        return QRect(64, item_rect.top() + 3, 45, item_rect.height() - 3)


class BuildItem(base.BaseItem, object):
    def __init__(self, parent=None):
        super(BuildItem, self).__init__(parent=parent)

        self._node = None

        self.setSizeHint(0, QSize(self.sizeHint(0).width(), 26))

    # ================================================================================================
    # ======================== PROPERTIES
    # ================================================================================================

    @property
    def node(self):
        return self._node

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def set_text(self, text):
        """
        Function used to set text of the item
        :param text: str
        """

        text = '                ' + text
        super(BuildItem, self).setText(0, text)

    def _create_context_menu(self):
        """
        Overrides base BuildItem create_context_menu function
        Creates context menu for this item
        :return: QMenu
        """

        self._context_menu = QMenu()

        python_icon = resource.ResourceManager().icon('python')
        new_python_action = self._context_menu.addAction(python_icon, 'New Python Code')

    # ================================================================================================
    # ======================== NODE
    # ================================================================================================

    def update_node(self):
        node_info = self.get_node_info()
        node_class = node_info.get('class', None)
        if not node_class:
            LOGGER.warning(
                'Impossible to retrieve builder node with class: "{}" for "{}"'.format(node_class, self.get_text()))
            return
        node_package = node_info.get('package', None)
        if not node_package:
            LOGGER.warning(
                'Impossible to retrieve builder node from package: "{}" for "{}"'.format(node_class, self.get_text()))
            return

        pkg = rigbuilder.PkgsMgr().get_package_by_name(node_package)
        if not pkg:
            LOGGER.warning('No package with name "{}" found!'.format(node_package))
            return

        rig_object = self.get_object()
        item_name = fileio.remove_extension(self.get_text())
        builder_node_class = pkg.get_builder_node_class_by_name(node_class)
        builder_node = builder_node_class(item_name)
        builder_node.set_directory(os.path.dirname(rig_object.get_code_folder(item_name)))
        builder_node.get_option_file()
        self._node = builder_node

    def get_node_info(self):
        rig_object = self.get_object()
        item_name = fileio.remove_extension(self.get_text())
        node_info_file = rig_object.get_code_file(item_name)
        if not node_info_file or not os.path.isfile(node_info_file):
            LOGGER.warning('Impossible to retrieve node info for "{}"!'.format(self.get_text()))
            return dict()

        return yamlio.read_file(node_info_file)

