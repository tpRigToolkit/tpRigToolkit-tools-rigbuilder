#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget to handle editable options for rigbuilder
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.qt.core import base
from tpDcc.libs.qt.widgets import layouts, label, lineedit, buttons, options

from tpRigToolkit.tools.rigbuilder.core import controls


class RigBuilderOptionList(options.OptionList, object):
    def __init__(self, parent=None, option_object=None):
        super(RigBuilderOptionList, self).__init__(parent=parent, option_object=option_object)

    def _create_context_menu(self):
        create_menu = super(RigBuilderOptionList, self)._create_context_menu()

        control_icon = tp.ResourcesMgr().icon('rigcontrol')
        create_menu.addSeparator()
        add_rig_control_action = QAction(control_icon, 'Add Rig Control', create_menu)
        create_menu.addAction(add_rig_control_action)

        add_rig_control_action.triggered.connect(self.add_control_rig)

    def add_custom(self, option_type, name, value=None, parent=None, **kwargs):
        if option_type == 'rigcontrol':
            self.add_control_rig(name=name, value=value, parent=parent)

    def add_control_rig(self, name='rigcontrol', value=None, parent=None):
        name = self._get_unique_name(name, parent)
        control_widget = RigControlOption(name=name, parent=parent, main_widget=self._parent)
        control_widget.set_value(value)
        self._handle_parenting(control_widget, parent)
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
        self._line = lineedit.BaseLineEdit()
        self._btn = buttons.BaseButton(text='...')

        self.main_layout.addWidget(self._label)
        self.main_layout.addWidget(self._line)
        self.main_layout.addWidget(self._btn)

    def get_value(self):
        return self._control_data

    def set_value(self, value_dict):
        self._control_data = value_dict or dict()
        name = self._control_data.get('control_name', '')
        self._line.setText(name)
        self._line.setToolTip(str(self._control_data))

    def setup_signals(self):
        self._btn.clicked.connect(self._on_open_rig_control_selector)

    def get_name(self):
        return self._label.text()

    def set_name(self, value):
        self._label.setText(value)

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
        self.set_value(control_data)
        self.valueChanged.emit(control_data)
