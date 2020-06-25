#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget to handle editable options for rigbuilder
"""

from __future__ import print_function, division, absolute_import

import os
import json

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.python import python
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, label, lineedit, buttons, options, dividers

from tpRigToolkit.tools.rigbuilder.core import controls
from tpRigToolkit.tools.rigbuilder.data import skeleton


class RigBuilderOptionList(options.OptionList, object):
    def __init__(self, parent=None, option_object=None):
        super(RigBuilderOptionList, self).__init__(parent=parent, option_object=option_object)

    def _create_context_menu(self):
        create_menu = super(RigBuilderOptionList, self)._create_context_menu()

        control_icon = tp.ResourcesMgr().icon('rigcontrol')
        bone_icon = tp.ResourcesMgr().icon('bone')

        create_menu.addSeparator()
        add_rig_control_action = QAction(control_icon, 'Add Rig Control', create_menu)
        create_menu.addAction(add_rig_control_action)
        add_bone_action = QAction(bone_icon, 'Add Rig Bone', create_menu)
        create_menu.addAction(add_bone_action)
        add_control_bone_link_action = QAction(bone_icon, 'Add Control/Bone Link', create_menu)
        create_menu.addAction(add_control_bone_link_action)

        add_rig_control_action.triggered.connect(self.add_control_rig)
        add_bone_action.triggered.connect(self.add_bone)
        add_control_bone_link_action.triggered.connect(self.add_control_bone_link)

    def add_custom(self, option_type, name, value=None, parent=None, **kwargs):
        if option_type == 'rigcontrol':
            self.add_control_rig(name=name, value=value, parent=parent)
        if option_type == 'bone':
            self.add_bone(name=name, value=value, parent=parent)
        elif option_type == 'boneList':
            self.add_bone_list(name=name, value=value, parent=parent)
        elif option_type == 'boneControlLink':
            self.add_control_bone_link(name=name, value=value, parent=parent)

    def add_control_rig(self, name='rigcontrol', value=None, parent=None):
        name = self._get_unique_name(name, parent)
        control_widget = RigControlOption(name=name, parent=parent, main_widget=self._parent)
        control_widget.set_value(value)
        self._handle_parenting(control_widget, parent)
        self._write_options(clear=False)

    def add_bone(self, name='bone', value=None, parent=None):
        name = self._get_unique_name(name, parent)
        bone_widget = BoneOption(name=name, parent=parent, main_widget=self._parent)
        bone_widget.set_value(value)
        self._handle_parenting(bone_widget, parent)
        self._write_options(clear=False)

    def add_bone_list(self, name='boneList', value=None, parent=None):
        value = python.force_list(value)
        name = self._get_unique_name(name, parent)
        bone_widget = BoneOptionList(name=name, parent=parent, main_widget=self._parent)
        bone_widget.set_value(value)
        self._handle_parenting(bone_widget, parent)
        self._write_options(clear=False)

    def add_control_bone_link(self, name='boneControlLink', value=None, parent=None):
        name = self._get_unique_name(name, parent)
        bone_widget = BoneControlLinkOption(name=name, parent=parent, main_widget=self._parent)
        bone_widget.set_value(value or list())
        self._handle_parenting(bone_widget, parent)
        self._write_options(clear=False)


class RigBuilderOptionsWidget(options.OptionsWidget, object):

    OPTION_LIST_CLASS = RigBuilderOptionList

    def __init__(self, option_object=None, settings=None, parent=None):
        super(RigBuilderOptionsWidget, self).__init__(option_object=option_object, settings=settings, parent=parent)


class RigControlOption(options.Option, object):
    def __init__(self, name, parent, main_widget):
        super(RigControlOption, self).__init__(name=name, parent=parent, main_widget=main_widget)

    def get_option_type(self):
        return 'rigcontrol'

    def get_option_widget(self):
        return GetControlRigWidget(name=self._name)

    def get_name(self):
        name = self._option_widget.get_name()
        return name

    def set_name(self, name):
        self._option_widget.set_name(name)

    def get_value(self):
        return self._option_widget.control_data

    def set_value(self, value):
        self._option_widget.set_value(value)

    def _setup_option_widget_value_change(self):
        self._option_widget.valueChanged.connect(self._on_value_changed)


class BoneOption(options.Option, object):
    def __init__(self, name, parent, main_widget):
        super(BoneOption, self).__init__(name=name, parent=parent, main_widget=main_widget)

    def get_option_type(self):
        return 'bone'

    def get_option_widget(self):
        return GetBoneWidget(name=self._name)

    def get_value(self):
        value = self._option_widget.get_text()
        if not value:
            value = ''

        return value

    def set_value(self, value):
        value = str(value)
        self._option_widget.set_text(value)

    def _setup_option_widget_value_change(self):
        self._option_widget.textChanged.connect(self._on_value_changed)


class BoneOptionList(options.ListOption, object):
    def __init__(self, name, parent, main_widget):
        super(BoneOptionList, self).__init__(name=name, parent=parent, main_widget=main_widget)

    def get_option_type(self):
        return 'boneList'


class GetControlRigWidget(base.BaseWidget, object):
    valueChanged = Signal(object)

    def __init__(self, name, parent=None):
        self._name = name
        super(GetControlRigWidget, self).__init__(parent=parent)

        self._control_data = dict()

    @property
    def control_data(self):
        return self._control_data

    def get_main_layout(self):
        main_layout = layouts.HorizontalLayout()
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(2, 2, 2, 2)

        return main_layout

    def ui(self):
        super(GetControlRigWidget, self).ui()

        self._label = label.BaseLabel(self._name)
        self._control = ControlLineEdit()

        self.main_layout.addWidget(self._label)
        self.main_layout.addWidget(self._control)

    def setup_signals(self):
        self._control.controlSelected.connect(self._on_selected_control)

    def get_value(self):
        return self._control_data

    def set_value(self, value_dict):
        self._control_data = value_dict or dict()
        self._control.set_data(self._control_data)

    def get_name(self):
        return self._label.text()

    def set_name(self, value):
        self._label.setText(value)

    def _on_selected_control(self, control_data):
        self.set_value(control_data)
        self.valueChanged.emit(control_data)


class ControlLineEdit(base.BaseWidget, object):
    controlSelected = Signal(object)

    def __init__(self, parent=None):
        super(ControlLineEdit, self).__init__(parent=parent)

        self._control_data = dict()

    @property
    def control_data(self):
        return self._control_data

    def get_main_layout(self):
        main_layout = layouts.HorizontalLayout()
        main_layout.setSpacing(2)
        main_layout.setContentsMargins(2, 2, 2, 2)

        return main_layout

    def ui(self):
        super(ControlLineEdit, self).ui()

        self._line = lineedit.BaseLineEdit()
        self._btn = buttons.BaseButton(text='...')

        self.main_layout.addWidget(self._line)
        self.main_layout.addWidget(self._btn)

    def setup_signals(self):
        self._btn.clicked.connect(self._on_open_rig_control_selector)

    def set_data(self, data):
        data = data if data is not None else dict()
        name = data.get('control_name', '')
        self._line.setText(str(name))
        self._line.setToolTip(str(data))
        self._control_data = data

    def _on_open_rig_control_selector(self):
        dlg = QDialog(parent=tp.Dcc.get_main_window() or None)
        dlg.setWindowTitle('Select Control')
        lyt = QVBoxLayout()
        lyt.setSpacing(0)
        lyt.setContentsMargins(0, 0, 0, 0)
        dlg.setLayout(lyt)
        control_selector = controls.RigBuilderControlSelector(parent=dlg)
        if self._control_data:
            control_selector.set_control_data(self._control_data)
        lyt.addWidget(control_selector)
        dlg.exec_()
        control_data = control_selector.control_data or dict()
        if not control_data and self._control_data:
            return
        if control_data:
            control_data.pop('shape_data', None)
            control_data.pop('name', None)

        self.controlSelected.emit(control_data)


class GetBoneWidget(options.TextWidget, object):
    def __init__(self, name='', parent=None):
        super(GetBoneWidget, self).__init__(name=name, parent=parent)

    def get_text_widget(self):
        return BoneLineEdit()


class BoneLineEdit(lineedit.BaseLineEdit, object):
    def __init__(self, text='', parent=None):
        super(BoneLineEdit, self).__init__(text=text, parent=parent)

    @property
    def selected_node(self):
        return self.text()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            data = event.mimeData().urls()
            file_info = QFileInfo(data[0].toLocalFile())
            file_name = file_info.absoluteFilePath()
            if file_name and os.path.isfile(file_name):
                file_extension = os.path.splitext(file_name)[-1]
                data_extension = skeleton.SkeletonFileData.get_data_extension()
                if not data_extension.startswith('.'):
                    data_extension = '.{}'.format(data_extension)
                if file_extension == data_extension:
                    self._show_bones_hierarchy(file_name)
                    event.accept()
        elif event.mimeData().hasText():
            self.setText(event.mimeData().text())

        event.accept()

    def _show_bones_hierarchy(self, file_path):
        dlg = QDialog(parent=tp.Dcc.get_main_window() or None)
        dlg.setWindowTitle('Select Skeleton Node')
        lyt = QVBoxLayout()
        lyt.setSpacing(0)
        lyt.setContentsMargins(0, 0, 0, 0)
        dlg.setLayout(lyt)
        bone_hierarchy_widget = BoneHierarchyWidget(file_path, parent=dlg)
        current_bone = self.text() or ''
        bone_hierarchy_widget.set_bone(current_bone)
        lyt.addWidget(bone_hierarchy_widget)
        dlg.exec_()
        selected_node = bone_hierarchy_widget.selected_node
        if not selected_node:
            return
        self.setText(selected_node)


class BoneHierarchyWidget(base.BaseWidget, object):
    def __init__(self, file_path, parent=None):
        self._file_path = file_path
        self._selected_node = None
        super(BoneHierarchyWidget, self).__init__(parent=parent)

        self._load_data()

    @property
    def selected_node(self):
        return self._selected_node

    def ui(self):
        super(BoneHierarchyWidget, self).ui()

        self._tree_hierarchy = QTreeWidget()
        self._node_line = QLineEdit()
        self._node_line.setReadOnly(True)
        self._ok_btn = buttons.BaseButton('Ok')
        self._cancel_btn = buttons.BaseButton('Cancel')
        buttons_layout = layouts.HorizontalLayout()
        buttons_layout.addStretch()
        buttons_layout.addWidget(self._ok_btn)
        buttons_layout.addWidget(self._cancel_btn)

        self.main_layout.addWidget(self._tree_hierarchy)
        self.main_layout.addWidget(self._node_line)
        self.main_layout.addWidget(dividers.Divider())
        self.main_layout.addLayout(buttons_layout)

    def setup_signals(self):
        self._tree_hierarchy.currentItemChanged.connect(self._on_item_selected)
        self._ok_btn.clicked.connect(self._on_ok)
        self._cancel_btn.clicked.connect(self._on_cancel)

    def set_bone(self, bone_name):
        if not bone_name:
            return

        find_items = self._tree_hierarchy.findItems(bone_name, Qt.MatchExactly | Qt.MatchRecursive, 0)
        if not find_items:
            return

        find_item = find_items[0]
        find_item.setSelected(True)
        self._tree_hierarchy.setCurrentItem(find_item)
        self._tree_hierarchy.scrollTo(self._tree_hierarchy.indexFromItem(find_item))

    def _load_data(self):
        self._tree_hierarchy.clear()
        if not self._file_path or not os.path.isfile(self._file_path):
            return

        with open(self._file_path, 'r') as fh:
            skeleton_data = json.load(fh)
        if not skeleton_data:
            return

        created_nodes = dict()
        for node_data in skeleton_data:
            node_index = node_data.get('index', 0)
            node_parent_index = node_data.get('parent_index', -1)
            node_name = node_data.get('name', 'new_node')
            new_node = QTreeWidgetItem()
            new_node.setText(0, node_name)
            created_nodes[node_index] = {'node': new_node, 'parent_index': node_parent_index}
        sorted(created_nodes.items(), key=lambda x: int(x[0]))

        for node_index, node_data in created_nodes.items():
            node_data = created_nodes.get(node_index, None)
            if not node_data:
                continue
            node_item = node_data.get('node')
            parent_index = node_data['parent_index']
            if parent_index <= -1:
                self._tree_hierarchy.addTopLevelItem(node_item)
                continue
            parent_node_data = created_nodes.get(parent_index, None)
            if not parent_node_data:
                continue
            parent_node_item = parent_node_data.get('node')
            parent_node_item.addChild(node_item)

        self._tree_hierarchy.expandAll()

    def _on_item_selected(self, current, previous):
        node_name = current.text(0)
        self._node_line.setText(node_name)
        self._selected_node = node_name

    def _on_ok(self):
        self.parent().close()

    def _on_cancel(self):
        self._selected_node = None
        self.parent().close()


class BoneControlLinkOption(options.ListOption, object):
    def __init__(self, name, parent=None, main_widget=None):
        super(BoneControlLinkOption, self).__init__(name=name, parent=parent, main_widget=main_widget)

    def get_option_type(self):
        return 'boneControlLink'

    def get_option_widget(self):
        return GetBoneControlLinkWidget(name=self._name)

    def get_value(self):
        list_value = self._option_widget.get_value()

        return list_value


class GetBoneControlLinkWidget(options.GetListWidget, object):
    def __init__(self, name, parent=None):
        super(GetBoneControlLinkWidget, self).__init__(name=name, parent=parent)

    def get_list_widget(self):
        return BoneControlLinkList()


class BoneControlLinkList(options.ListWidget, object):
    def __init__(self):
        super(BoneControlLinkList, self).__init__()

    def _get_entry_widget(self, name):
        return BoneControlLinkItem(name)

    def _build_entry(self,  link_info=None):
        entry_widget = self._get_entry_widget(link_info)
        entry_widget.itemRemoved.connect(self._cleanup_garbage)
        entry_widget.valueChanged.connect(self._on_value_changed)
        entry_widget.itemDuplicated.connect(self._on_duplicated_item)

        return entry_widget

    def _on_duplicated_item(self, widget):
        value = widget.get_value()
        if not value:
            return
        self.add_entry(value)

        self._on_value_changed()


class BoneControlLinkItem(base.BaseWidget, object):
    valueChanged = Signal(object, object)
    itemRemoved = Signal(object)
    itemDuplicated = Signal(object)

    def __init__(self, link_info=None, parent=None):
        link_info = link_info if link_info else dict()
        self._control_data = link_info.get('control', dict())
        self._bone_name = link_info.get('node', '')
        self._garbage = None
        super(BoneControlLinkItem, self).__init__(parent=parent)

    def get_main_layout(self):
        main_layout = layouts.HorizontalLayout()
        main_layout.setAlignment(Qt.AlignRight)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)

        return main_layout

    def ui(self):
        super(BoneControlLinkItem, self).ui()

        self._control_line = ControlLineEdit()
        self._bone_line = BoneLineEdit()
        self._duplicate_btn = buttons.BaseToolButton().image('clone').icon_only()
        self._remove_btn = buttons.BaseToolButton().image('delete').icon_only()

        self._control_line.set_data(self._control_data)
        self._bone_line.setText(self._bone_name)

        self.main_layout.addWidget(self._control_line)
        self.main_layout.addWidget(self._bone_line)
        self.main_layout.addSpacing(10)
        self.main_layout.addWidget(self._duplicate_btn)
        self.main_layout.addWidget(self._remove_btn)

    def setup_signals(self):
        self._control_line.controlSelected.connect(self._on_selected_control)
        self._duplicate_btn.clicked.connect(self._on_duplicate_item)
        self._remove_btn.clicked.connect(self._on_remove_item)
        self._control_line.controlSelected.connect(self._on_value_changed)
        self._bone_line.textChanged.connect(self._on_value_changed)

    def get_value(self):
        control_data = self._control_line.control_data
        selected_bone = self._bone_line.selected_node

        return {
            'control': control_data,
            'node': selected_bone
        }

    def _on_selected_control(self, control_data):
        self._control_data = control_data or dict()
        self._control_line.set_data(self._control_data)

    def _on_remove_item(self):
        self._garbage = True
        self.itemRemoved.emit(self)

    def _on_duplicate_item(self):
        self._garbage = True
        self.itemDuplicated.emit(self)

    def _on_value_changed(self):
        control_data = self._control_line.control_data
        bone_node = self._bone_line.selected_node
        self.valueChanged.emit(control_data, bone_node)
