#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains implementation for Properties Editor widget
"""

from __future__ import print_function, division, absolute_import

from collections import OrderedDict

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpQtLib
from tpQtLib.core import qtutils, base
from tpQtLib.widgets import search


class PropertiesWidget(base.BaseWidget, object):

    spawnDuplicate = Signal()

    def __init__(self, search_by_headers=False, parent=None):

        self._search_by_headers = search_by_headers
        self._lock_icon = tpQtLib.resource.icon('lock')
        self._unlock_icon = tpQtLib.resource.icon('unlock')

        super(PropertiesWidget, self).__init__(parent=parent)

    def get_main_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)
        main_layout.setObjectName('propertiesMainLayout')
        main_layout.setContentsMargins(2, 2, 2, 2)

        return main_layout

    def ui(self):
        super(PropertiesWidget, self).ui()

        self.setWindowTitle('Properties Editor')
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self._search_widget = QWidget()
        self._search_layout = QHBoxLayout()
        self._search_layout.setContentsMargins(1, 1, 1, 1)
        self._search_widget.setLayout(self._search_layout)
        self._search_line = search.SearchFindWidget()
        self._search_line.setObjectName('searchLine')
        self._search_line.set_placeholder_text('Search Property ...')
        self._lock_btn = QToolButton()
        self._lock_btn.setCheckable(True)
        self._lock_btn.setIcon(self._unlock_icon)
        self._tear_off_btn = QToolButton()
        self._tear_off_btn.setIcon(tpQtLib.resource.icon('new_copy', theme='color'))

        self._search_layout.addWidget(self._search_line)
        self._search_layout.addWidget(self._lock_btn)
        self._search_layout.addWidget(self._tear_off_btn)
        self._search_widget.setVisible(False)

        self._content_layout = QVBoxLayout()
        self._content_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        self.main_layout.addWidget(self._search_widget)
        self.main_layout.addLayout(self._content_layout)
        self.main_layout.addItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

    def setup_signals(self):
        self._search_line.textChanged.connect(self._on_filter_by_headers if self._search_by_headers else self._on_filter_by_headers_and_fields)
        self._lock_btn.toggled.connect(self._on_change_lock_icon)
        self._tear_off_btn.clicked.connect(self._on_tear_off_copy)

    def is_locked(self):
        return bool(self._lock_btn.isChecked())

    def set_lock_visible(self, flag):
        self._lock_btn.setVisible(flag)

    def set_tear_off_copy_visible(self, flag):
        self._tear_off_btn.setVisible(flag)

    def set_search_widget_visible(self, flag):
        self._search_widget.setVisible(flag)

    def clear(self):
        if not self.is_locked():
            qtutils.clear_layout(self._content_layout)
            self._search_widget.hide()
            self._lock_btn.setChecked(False)

    def add_widget(self, collapsible_widget):
        if self.is_locked():
            return False

        if isinstance(collapsible_widget, CollapsibleFormWidget):
            self._search_widget.show()
            self._content_layout.insertWidget(-1, collapsible_widget)
            return True

        return False

    def insert_widget(self, collapsible_widget, index):
        if self.is_locked():
            return False

        if isinstance(collapsible_widget, CollapsibleFormWidget):
            self._search_widget.show()
            self._content_layout.insertWidget(index, collapsible_widget)
            return True

        return False

    def _on_filter_by_headers(self, text):
        print('Filtering by headers: {}'.format(text))
        count = self._content_layout.count()
        for i in range(count):
            item = self._content_layout.itemAt(i)
            w = item.widget()
            if w:
                if text.lower() in w.title().lower():
                    w.show()
                else:
                    w.hide()

    def _on_filter_by_headers_and_fields(self, text):
        count = self._content_layout.count()
        for i in range(count):
            item = self._content_layout.itemAt(i)
            w = item.widget()
            if w:
                w.filter_content(text)
                if w.are_all_widgets_hidden():
                    w.hide()
                else:
                    w.show()
                    w.set_collapsed(False)

    def _on_change_lock_icon(self, checked):
            self._lock_btn.setIcon(self._lock_icon) if checked else self._lock_btn.setIcon(self._unlock_icon)

    def _on_tear_off_copy(self):
        self.spawnDuplicate.emit()


class PropertiesTree(QTreeWidget, object):
    def __init__(self):
        super(PropertiesTree, self).__init__()
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setHeaderHidden(True)

    def add_folder(self, name, parent=None):
        icon = self.style().standardIcon(QStyle.SP_DirIcon)
        item = QTreeWidgetItem([name])
        item.setIcon(0, icon)
        item.is_folder = True
        if parent:
            parent.addChild(item)
        else:
            self.addTopLevelItem(item)

        return item

    def add_normal(self, name, parent=None):
        item = QTreeWidgetItem([name])
        item.setFlags(item.flags() & ~Qt.ItemIsDragEnabled)
        item.is_folder = False
        if parent:
            parent.addChild(item)
        else:
            self.addTopLevelItem(item)

        return item

    def fill_dict_from_model(self, parent_index, model_dict, model):
        v = OrderedDict()
        for i in range(model.rowCount(parent_index)):
            index = model.index(i, 0, parent_index)
            self.fill_dict_form_model(index, v, model)
        if len(v) == 0:
            v = None
        model_dict[parent_index.data()] = v

    def model_to_dict(self):
        model = self.model()
        model_dict = OrderedDict()
        for i in range(model.rowCount()):
            index = model.index(i, 0)
            self.fill_dict_from_model(index, model_dict, model)

        return model_dict


class CollapsibleTitleButton(QPushButton, object):
    def __init__(self, parent=None, max_height=25):
        super(CollapsibleTitleButton, self).__init__(parent)

        self.setObjectName(self.__class__.__name__)
        self.setDefault(True)
        self.setMaximumHeight(max_height)


class PropertyEntry(base.BaseWidget, object):
    def __init__(self, label, widget, parent=None, hide_label=False, max_label_width=None, tooltip=''):

        self._label = label
        self._hide_label = hide_label
        self._tooltip = tooltip
        self._max_label_width = max_label_width
        self._widget = widget
        self._index = -1

        super(PropertyEntry, self).__init__(parent=parent)

    def get_main_layout(self):
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(1, 1, 1, 1)

        return main_layout

    def ui(self):
        super(PropertyEntry, self).ui()

        if not self._hide_label:
            label = QLabel(self._label + ':')
            label.setStyleSheet('font: bold;')
            label.setToolTip(self._tooltip)
            if not self._max_label_width:
                label.setSizePolicy(QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Preferred))
            else:
                label.setMaximumWidth(self._max_label_width)
            self.main_layout.addWidget(label)

        self.main_layout.addWidget(self._widget)

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, new_index):
        self._index = new_index

    def get_label(self):
        return self._label


class CollapsibleGroupBox(base.BaseWidget, object):

    MINIMUM_HEIGHT = 30

    def __init__(self, name, parent=None):
        self._name = name
        super(CollapsibleGroupBox, self).__init__(parent=parent)

    def get_main_layout(self):
        main_layout = QGridLayout()

        return main_layout

    def ui(self):
        super(CollapsibleGroupBox, self).ui()

        self._control_group = QGroupBox()
        self._control_group.setTitle(self._name)
        self._control_group.setCheckable(True)
        self._control_group.setChecked(True)
        self._groups_layout = QVBoxLayout(self._control_group)
        self._control_group.setFixedHeight(self._control_group.sizeHint().height())
        self.main_layout.addWidget(self._control_group)

    def setup_signals(self):
        self._control_group.toggled.connect(lambda: self.toggle_collapsed())

    def are_all_widgets_hidden(self):
        count = self._groups_layout.count()
        hidden = 0
        for i in range(count):
            widget = self._groups_layout.itemAt(i).widget()
            if widget.isHidden():
                hidden += 1

        return count == hidden

    def set_collapsed(self, flag):
        self._control_group.setChecked(not flag)
        if not flag:
            self._control_group.setFixedHeight(self._control_group.sizeHint().height())
        else:
            self._control_group.setFixedHeight(self.MINIMUM_HEIGHT)

    def toggle_collapsed(self):
        state = self._control_group.isChecked()
        if state:
            self._control_group.setFixedHeight(self._control_group.sizeHint().height())
        else:
            self._control_group.setFixedHeight(self.MINIMUM_HEIGHT)

    def add_widget(self, widget):
        self._groups_layout.addWidget(widget)
        self._control_group.setFixedHeight(self._control_group.sizeHint().height())

    def insert_widget(self, index, widget):
        self._groups_layout.insertWidget(index, widget)
        self._control_group.setFixedHeight(self._control_group.sizeHint().height())


class CollapsibleWidget(base.BaseWidget, object):
    def __init__(self, parent=None, head_name='Collapse', no_spacer=True, collapsed=False):

        self._spacer_item = None

        super(CollapsibleWidget, self).__init__(parent=parent)

        self.setObjectName(self.__class__.__name__)
        self.set_button_name(head_name)
        if no_spacer:
            self.remove_spacer()
        self.set_collapsed(collapsed)

    def get_main_layout(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setObjectName('mainVLayout')
        main_layout.setSizeConstraint(QLayout.SetMinAndMaxSize)

        return main_layout

    def ui(self):
        super(CollapsibleWidget, self).ui()

        self.resize(400, 300)
        self.setMinimumHeight(30)
        self.setWindowTitle(self.__class__.__name__)

        self._head_btn = CollapsibleTitleButton(self)
        self._head_btn.setStyleSheet(self._head_btn.styleSheet() + '\ntext-align: left;')
        self._content_hidden_icon = self._head_btn.style().standardIcon(QStyle.SP_TitleBarUnshadeButton)
        self._content_visible_icon = self._head_btn.style().standardIcon(QStyle.SP_TitleBarShadeButton)
        self._content_widget = QWidget(self)
        self._content_widget.setObjectName('ContentWidget')
        size_policy = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        size_policy.setHorizontalStretch(0)
        size_policy.setVerticalStretch(0)
        size_policy.setHeightForWidth(self._content_widget.sizePolicy().hasHeightForWidth())
        self._content_widget.setSizePolicy(size_policy)
        self._spacer_item = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        self.main_layout.addWidget(self._head_btn)
        self.main_layout.addWidget(self._content_widget)
        self.main_layout.addItem(self._spacer_item)

        self._update_icon()

    def setup_signals(self):
        self._head_btn.clicked.connect(self._on_toggle_collapsed)

    def title(self):
        return self._head_btn.text()

    def is_collapsed(self):
        return self._content_widget.isHidden()

    def set_collapsed(self, flag):
        self._content_widget.setVisible(not flag)
        self._update_icon()

    def toggle_collapsed(self):
        self.set_collapsed(True) if self._content_widget.isVisible() else self.set_collapsed(False)

    def set_read_only(self, flag=True):
        self._content_widget.setEnabled(not flag)

    def set_content_hidden_icon(self, icon):
        self._content_hidden_icon = icon

    def set_content_visible_icon(self, icon):
        self._content_visible_icon = icon

    def set_button_name(self, name):
        self._head_btn.setText(name)

    def add_widget(self, widget):
        self.main_layout.addWidget(widget)

    def remove_spacer(self):
        if self._spacer_item:
            self.main_layout.removeItem(self._spacer_item)
            del self._spacer_item
            self._spacer_item = None

    def filter_content(self, pattern):
        pass

    def _update_icon(self):
        self._head_btn.setIcon(self._content_hidden_icon) if self.is_collapsed() else self._head_btn.setIcon(self._content_visible_icon)

    def _on_toggle_collapsed(self):
        self.toggle_collapsed()


class CollapsibleFormWidget(CollapsibleWidget, object):
    def __init__(self, parent=None, head_name='Collapse', no_spacer=True, collapsed=False, hide_labels=False):

        self._property_names = dict()
        self._entry_names = dict()
        self._groups = dict()
        self._hide_labels = hide_labels

        super(CollapsibleFormWidget, self).__init__(parent=parent, head_name=head_name, no_spacer=no_spacer, collapsed=collapsed)

        self._update_icon()

    def ui(self):
        super(CollapsibleFormWidget, self).ui()

        self._layout = QVBoxLayout(self._content_widget)
        self._layout.setObjectName('CollapsibleWidgetFormLayout')
        self._layout.setContentsMargins(0, 0, 0, 5)
        self._layout.setSpacing(2)

    @property
    def form_layout(self):
        return self._layout

    def filter_content(self, pattern):
        for key, value in self._entry_names.items():
            if isinstance(value, PropertyEntry):
                value.setVisible(pattern.lower() in value.get_label().lower())
        for key, value in self._groups.items():
            if isinstance(value, CollapsibleGroupBox):
                if value.are_all_widgets_hidden():
                    value.hide()
                else:
                    value.show()
                    value.set_collapsed(False)

    def add_widget(self, label=None, widget=None, max_label_width=None, group=None):
        if not widget or isinstance(widget, CollapsibleWidget):
            return False

        if group:
            if group in self._groups:
                group_widget = self._groups[group]
            else:
                group_widget = CollapsibleGroupBox(name=group)
                self._groups[group] = group_widget

        entry = PropertyEntry(label=str(label), widget=widget, hide_label=self._hide_labels, max_label_width=max_label_width, tooltip=widget.toolTip())
        self._property_names[label] = widget
        self._entry_names[label] = entry
        if not group:
            self._layout.addWidget(entry)
        else:
            group_widget.add_widget(entry)
            self._layout.addWidget(group_widget)

        return True

    def insert_widget(self, index=0, label=None, widget=None, max_label_width=None, group=None):
        if not widget or isinstance(widget, CollapsibleWidget):
            return False

        if group:
            if group in self._groups:
                group_widget = self._groups[group]
            else:
                group_widget = CollapsibleGroupBox(name=group)
                self._groups[group] = group_widget

        entry = PropertyEntry(label=str(label), widget=widget, hide_label=self._hide_labels,
                              max_label_width=max_label_width, tooltip=widget.toolTip())
        self._property_names[label] = widget
        self._entry_names[label] = label
        if not group:
            self._layout.insertWidget(index, entry)
        else:
            group_widget.insert_widget(index, group_widget)
            self._layout.addWidget(group_widget)

        return True

    def are_all_widgets_hidden(self):
        count = self._layout.count()
        hidden = 0
        for i in range(count):
            widget = self._layout.itemAt(i).widget()
            if widget.isHidden():
                hidden += 1

        return count == hidden

    def set_spacing(self, spacing=2):
        self._layout.setSpacing(spacing)

    def get_widget_by_name(self, name):
        if name in self._property_names:
            return self._property_names[name]

        return None
