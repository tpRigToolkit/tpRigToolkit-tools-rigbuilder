 #! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains item implementation for build
"""

from __future__ import print_function, division, absolute_import

import os

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDcc

import tpRigToolkit
from tpRigToolkit.tools.rigbuilder.items import base


class BuildItemsDelegate(QStyledItemDelegate, object):

    MAX_TEXT_WIDTH = 0

    def __init__(self, parent=None):
        super(BuildItemsDelegate, self).__init__(parent)

    def editorEvent(self, event, model, option, index):
        if event.type() == QEvent.MouseButtonRelease:
            if event.button() == Qt.LeftButton:
                cbx_rect = self._get_checkbox_rect(option)
                pte = event.pos()
                if cbx_rect.contains(pte):
                    value = bool(index.data(Qt.CheckStateRole))
                    model.setData(index, not value, Qt.CheckStateRole)
                    return True

        return super(BuildItemsDelegate, self).editorEvent(event, model, option, index)

    def paint(self, painter, option, index):
        if index.column() == 0:
            item = self.parent().itemFromIndex(index)

            if option.state & QStyle.State_Selected:
                painter.fillRect(option.rect, option.palette.highlight())

            if not item.node:
                super(BuildItemsDelegate, self).paint(painter, option, index)
            else:
                self.initStyleOption(option, index)

                painter.setRenderHint(QPainter.Antialiasing)
                option_rect = option.rect
                state = QIcon.On if option.state & QStyle.State_Open else QIcon.Off

                # Draw custom background if start point is set
                start_index = self.parent().start_index
                if start_index and index.internalId() == start_index:
                    brush = QBrush(QColor(0, 70, 20) if tpDcc.is_maya() else QBrush(QColor(230, 240, 230)))
                    painter.fillRect(option_rect, brush)

                # Draw custom background if break point is set
                break_index = self.parent().break_index
                if break_index and index.internalId() == break_index:
                    brush = QBrush(QColor(70, 0, 0) if tpDcc.is_maya() else QBrush(QColor(240, 230, 230)))
                    painter.fillRect(option_rect, brush)

                # Draw Check Box
                option_btn = QStyleOptionButton()
                option_btn.rect = option.rect
                cbx_is_checked = bool(index.data(Qt.CheckStateRole))
                if cbx_is_checked:
                    option_btn.state |= QStyle.State_On
                else:
                    option_btn.state |= QStyle.State_Off
                QApplication.style().drawControl(QStyle.CE_CheckBox, option_btn, painter)
                cbx_rect = QApplication.style().subElementRect(QStyle.SE_ViewItemCheckIndicator, option_btn)

                # Draw default icon
                option_rect.setTopLeft(option_rect.topLeft() + QPoint(cbx_rect.width() + 3, 0))
                option.icon.paint(painter, option_rect, Qt.AlignLeft | Qt.AlignVCenter,  QIcon.Normal, state)

                # Draw tag text
                default_font = painter.font()
                text_font = QFont('Arial', 8)
                text_font.setBold(True)
                metrics = QFontMetrics(text_font)
                text_width = metrics.width(item.node.SHORT_NAME)
                if text_width > self.MAX_TEXT_WIDTH:
                    self.MAX_TEXT_WIDTH = text_width

                # Draw tag
                painter_path = QPainterPath()
                tag_rect = self._get_tag_rect(option_rect)
                tag_rect.setWidth(text_width + 28)
                painter_path.addRoundedRect(tag_rect, 5, 5)
                painter.fillPath(painter_path, QColor(*item.node.COLOR))
                painter.drawPath(painter_path)

                # Draw item icon
                icon_rect = self._get_icon_rect(option_rect)
                item.node.get_icon().paint(painter, icon_rect, Qt.AlignLeft | Qt.AlignVCenter,  QIcon.Normal, state)

                # Draw tag text
                tag_text_rect = self._get_text_rect(option_rect)
                painter.setFont(text_font)
                metrics = QFontMetrics(text_font)
                text_width = metrics.width(item.node.SHORT_NAME)
                tag_text_rect.setWidth(text_width)
                painter.drawText(tag_text_rect, Qt.AlignCenter, item.node.SHORT_NAME)

                # Draw default text
                default_text_rect = option_rect
                extra_width = (tag_text_rect.width() if tag_text_rect.width() > self.MAX_TEXT_WIDTH else
                               self.MAX_TEXT_WIDTH) - tag_text_rect.width()
                default_text_rect.setTopLeft(
                    default_text_rect.topLeft() + QPoint(tag_rect.width() - 10 + extra_width, 0))
                painter.setFont(default_font)
                painter.drawText(default_text_rect, Qt.AlignLeft | Qt.AlignVCenter, os.path.splitext(option.text)[0])

        else:
            super(BuildItemsDelegate, self).paint(painter, option, index)

    def _get_checkbox_rect(self, option):
        opt_btn = QStyleOptionButton()
        opt_btn.rect = option.rect
        sz = QApplication.style().subElementRect(QStyle.SE_ViewItemCheckIndicator, opt_btn)
        r = option.rect
        # dx = (r.width() - sz.widht()) / 2
        dy = (r.height() - sz.height()) / 2
        # r.setTopLeft(r.topLeft() + QPoint(dx, dy))
        r.setTopLeft(r.topLeft() + QPoint(0, dy))
        r.setWidth(sz.width())
        r.setHeight(sz.height())

        return r

    def _get_tag_rect(self, item_rect):
        return QRect(item_rect.left() + 28, item_rect.top() + 2, 65, item_rect.height() - 3)

    def _get_icon_rect(self, item_rect):
        return QRect(item_rect.left() + 30, item_rect.top() + 4, 20, item_rect.height() - 5)

    def _get_text_rect(self, item_rect):
        return QRect(item_rect.left() + 50, item_rect.top() + 2, 35, item_rect.height() - 3)


class BuildItemSignals(QObject, object):

    runNode = Signal()
    runBlock = Signal()
    addNode = Signal()
    renameNode = Signal()
    duplicateNode = Signal()
    deleteNode = Signal()
    changeBackgroundColor = Signal()
    resetBackgroundColor = Signal()
    setStartPoint = Signal()
    cancelStartPoint = Signal()
    setBreakPoint = Signal()
    cancelBreakPoint = Signal()
    browseNode = Signal()


class BuildItem(base.BaseItem, object):

    buildSignals = BuildItemSignals()

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

        play_icon = tpDcc.ResourcesMgr().icon('play')
        add_icon = tpDcc.ResourcesMgr().icon('add')
        rename_icon = tpDcc.ResourcesMgr().icon('rename')
        duplicate_icon = tpDcc.ResourcesMgr().icon('clone')
        delete_icon = tpDcc.ResourcesMgr().icon('delete')
        color_icon = tpDcc.ResourcesMgr().icon('fill_color')
        reset_icon = tpDcc.ResourcesMgr().icon('reset')
        browse_icon = tpDcc.ResourcesMgr().icon('open')
        cancel_icon = tpDcc.ResourcesMgr().icon('cancel')
        start_icon = tpDcc.ResourcesMgr().icon('start')
        flag_icon = tpDcc.ResourcesMgr().icon('finish_flag')

        build_action = self._context_menu.addAction(play_icon, 'Build')
        build_block_action = self._context_menu.addAction(play_icon, 'Build Block')
        self._context_menu.addSeparator()
        add_action = self._context_menu.addAction(add_icon, 'Add Builder Node')
        self._context_menu.addSeparator()
        rename_action = self._context_menu.addAction(rename_icon, 'Rename')
        duplicate_action = self._context_menu.addAction(duplicate_icon, 'Duplicate')
        delete_action = self._context_menu.addAction(delete_icon, 'Delete')
        self._context_menu.addSeparator()
        bg_color_action = self._context_menu.addAction(color_icon, 'Change Background Color')
        reset_color_action = self._context_menu.addAction(reset_icon, 'Reset Background Color')
        self._context_menu.addSeparator()
        set_start_point_action = self._context_menu.addAction(start_icon, 'Set Start Point')
        cancel_start_point_action = self._context_menu.addAction(cancel_icon, 'Cancel Start Point')
        self._context_menu.addSeparator()
        set_break_point_action = self._context_menu.addAction(flag_icon, 'Set Break Point')
        cancel_break_point_action = self._context_menu.addAction(cancel_icon, 'Cancel Break Point')
        self._context_menu.addSeparator()
        browse_action = self._context_menu.addAction(browse_icon, 'Browse')
        self._context_menu.addSeparator()

        build_action.triggered.connect(self.buildSignals.runNode.emit)
        build_block_action.triggered.connect(self.buildSignals.runBlock.emit)
        add_action.triggered.connect(self.buildSignals.addNode.emit)
        rename_action.triggered.connect(self.buildSignals.renameNode.emit)
        duplicate_action.triggered.connect(self.buildSignals.duplicateNode.emit)
        delete_action.triggered.connect(self.buildSignals.deleteNode.emit)
        bg_color_action.triggered.connect(self.buildSignals.changeBackgroundColor.emit)
        reset_color_action.triggered.connect(self.buildSignals.resetBackgroundColor.emit)
        set_start_point_action.triggered.connect(self.buildSignals.setStartPoint)
        cancel_start_point_action.triggered.connect(self.buildSignals.cancelStartPoint)
        set_break_point_action.triggered.connect(self.buildSignals.setBreakPoint)
        cancel_break_point_action.triggered.connect(self.buildSignals.cancelBreakPoint)
        browse_action.triggered.connect(self.buildSignals.browseNode.emit)

    # ================================================================================================
    # ======================== NODE
    # ================================================================================================

    def update_node(self):
        rig_object = self.get_object()
        item_name = self.get_name()
        builder_node, builder_node_pkg = rig_object.get_build_node_instance(item_name)
        self._node = builder_node
        if self._node:
            self._node.setup_context_menu(self._context_menu)

    def rename_node(self, new_name):
        rig_object = self.get_object()
        item_name = self.get_name()
        valid_rename = rig_object.rename_build_node(item_name, new_name)
        if not valid_rename:
            tpRigToolkit.logger.warning('Was not possible to rename build node: {} >> {}'.format(item_name, new_name))
            return False

        item_name_split = item_name.split('/')
        new_item_name = item_name.replace(item_name_split[-1], os.path.splitext(new_name)[0])
        self._node.set_option('Name', [new_item_name, 'nonedittext'], group='Base')

        return True
