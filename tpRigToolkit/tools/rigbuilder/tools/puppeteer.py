#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains pupetter tools implementation
"""

from __future__ import print_function, division, absolute_import

import os
from functools import partial

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.python import strings, fileio, yamlio
from tpDcc.libs.qt.core import base, qtutils
from tpDcc.libs.qt.widgets import accordion

from tpRigToolkit.tools.rigbuilder.core import consts, tool, puppet


class PuppetPartsBuilderTool(tool.DockTool, object):

    NAME = 'Puppet Parts Builder'
    TOOLTIP = 'Allow the creation of new Puppet Parts'
    DEFAULT_DOCK_AREA = Qt.LeftDockWidgetArea

    def __init__(self):
        super(PuppetPartsBuilderTool, self).__init__()

        self._created = False
        self._content = QWidget()
        self._content_layout = QVBoxLayout()
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(0)
        self._content.setLayout(self._content_layout)
        self.setWidget(self._content)

    def show_tool(self):
        super(PuppetPartsBuilderTool, self).show_tool()

        if not self._created:
            self._create_ui()
            self._created = True

    def _create_ui(self):
        project = self._app.get_project()
        self._parts_builder = PuppetPartsBuilder(project=project)
        self._content_layout.addWidget(self._parts_builder)


class PuppetPartsBuilder(base.BaseWidget, object):
    def __init__(self, project=None, parent=None):

        self._project = project
        self._part_groups = None

        super(PuppetPartsBuilder, self).__init__(parent)

    def ui(self):
        super(PuppetPartsBuilder, self).ui()

        part_title_layout = QHBoxLayout()
        part_title_layout.setContentsMargins(2, 2, 2, 2)
        part_title_layout.setSpacing(2)
        self._current_part_lbl = QLabel('Current Puppet Part: ')
        self._current_part_line = QLineEdit()
        self._current_part_line.setReadOnly(True)
        part_title_layout.addWidget(self._current_part_lbl)
        part_title_layout.addWidget(self._current_part_line)

        self._accordion = accordion.AccordionWidget()

        part_widget = QWidget()
        part_layout = QVBoxLayout()
        part_layout.setContentsMargins(2, 2, 2, 2)
        part_layout.setSpacing(2)
        part_widget.setLayout(part_layout)
        self._create_btn = QPushButton('Create New')
        self._duplicate_btn = QPushButton('Duplicate')
        self._edit_btn = QPushButton('Edit')
        self._add_metadata_btn = QPushButton('Add Metadata')
        part_group_layout = QHBoxLayout()
        part_group_layout.setContentsMargins(2, 2, 2, 2)
        part_group_layout.setSpacing(2)
        part_group_lbl = QLabel('Part Group: ')
        self._part_group_combo = QComboBox()
        self._part_group_combo.setEditable(True)
        self._part_group_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._part_group_set_btn = QPushButton('Set')
        part_group_layout.addWidget(part_group_lbl)
        part_group_layout.addWidget(self._part_group_combo)
        part_group_layout.addWidget(self._part_group_set_btn)
        part_layout.addWidget(self._create_btn)
        part_layout.addWidget(self._duplicate_btn)
        part_layout.addWidget(self._edit_btn)
        part_layout.addWidget(self._add_metadata_btn)
        part_layout.addLayout(part_group_layout)

        guides_widget = QWidget()
        guides_layout = QVBoxLayout()
        guides_layout.setContentsMargins(2, 2, 2, 2)
        guides_layout.setSpacing(2)
        guides_widget.setLayout(guides_layout)
        self._create_main_guide_btn = QPushButton('Create Main Guide')
        self._create_guide_btn = QPushButton('Create Guide')
        self._connect_guides_btn = QPushButton('Connect Guides')
        guides_layout.addWidget(self._create_main_guide_btn)
        guides_layout.addWidget(self._create_guide_btn)
        guides_layout.addWidget(self._connect_guides_btn)

        checks_widget = QWidget()
        checks_layout = QVBoxLayout()
        checks_layout.setContentsMargins(2, 2, 2, 2)
        checks_layout.setSpacing(2)
        checks_widget.setLayout(checks_layout)
        self._check_part_btn = QPushButton('Check Part')
        self._mirror_part_btn = QPushButton('Mirror Part')
        checks_layout.addWidget(self._check_part_btn)
        checks_layout.addWidget(self._mirror_part_btn)

        self._accordion.add_item('Puppet Part', part_widget)
        self._accordion.add_item('Puppet Guides', guides_widget)
        self._accordion.add_item('Puppet Checks', checks_widget)

        self.main_layout.addLayout(part_title_layout)
        self.main_layout.addWidget(self._accordion)

        self._setup_duplicate_menu()
        self._setup_edit_menu()
        self._update_groups()
        self.update_current_module()

    def setup_signals(self):
        self._create_btn.clicked.connect(self._on_create_new_part)
        self._add_metadata_btn.clicked.connect(self._on_show_part_metadata)
        self._part_group_set_btn.clicked.connect(self._on_set_part_group)
        self._create_main_guide_btn.clicked.connect(self._on_create_main_guide)
        self._create_guide_btn.clicked.connect(self._on_create_guide)
        self._connect_guides_btn.clicked.connect(self._on_connect_guides)
        self._mirror_part_btn.clicked.connect(self._on_mirror_guide)

    def update_current_module(self):
        """
        Updates module in current scene
        """

        if tp.Dcc.object_exists(consts.PUPPET_PART_GROUP):
            part_name = os.path.splitext(os.path.basename(tp.Dcc.scene_name()))[0]
            part_dir = puppet.get_part_path(part_name=part_name)
            if not os.path.isdir(part_dir):
                return
            metadata = yamlio.read_file(os.path.join(part_dir, consts.PUPPET_METADATA_FILE))
            group = metadata.get('group', 'Custom')
            self._part_group_combo.setEditText(group)
        else:
            part_name = ''
            self._part_group_combo.setEditText('Custom')

        self._current_part_line.setText(part_name)

    def _setup_duplicate_menu(self):
        """
        Internal function that initializes duplicate menu
        """

        menu = QMenu(self)
        groups = puppet.get_part_groups()

        for group_name in sorted(groups):
            sub_menu = menu.addMenu('&{}'.format(group_name))
            for group in groups[group_name]:
                menu_action = QAction(self)
                menu_name = puppet.format_name(group)
                menu_action.setText(menu_name)
                menu_action.setToolTip(menu_name.upper())
                menu_action.triggered.connect(partial(self._on_duplicate_part, group))
                sub_menu.addAction(menu_action)

        self._duplicate_btn.setMenu(menu)

    def _setup_edit_menu(self):
        """
        Internal function that initializes duplicate menu
        """

        menu = QMenu(self)
        groups = puppet.get_part_groups()

        for group_name in sorted(groups):
            sub_menu = menu.addMenu('&{}'.format(group_name))
            for group in groups[group_name]:
                menu_action = QAction(self)
                menu_name = puppet.format_name(group)
                menu_action.setText(menu_name)
                menu_action.setToolTip(menu_name.upper())
                menu_action.triggered.connect(partial(self._on_edit_part, group))
                menu_action.setEnabled(puppet.part_has_file(part_name=group))
                sub_menu.addAction(menu_action)

        self._edit_btn.setMenu(menu)

    def _update_groups(self):
        """
        Internal callback function that updates current available part groups
        """

        self._part_group_combo.clear()

        self._part_groups = puppet.get_part_groups()
        self._part_group_combo.addItems(self._part_groups.keys())

    def _create_guide(self, guide_name=''):
        """
        Creates a new guide into current opened DCC puppet part
        :param guide_name: str
        :return: str
        """

        if not guide_name:
            guide_name = qtutils.get_string_input(
                'Please enter new guide name', 'Create Guide', old_name=consts.PUPPET_ROOT_GUIDE_NAME)
            if not guide_name:
                return False

        if not tp.Dcc.object_exists(consts.PUPPET_MAIN_GUIDE):
            qtutils.warning_message(
                'Main Guide "{}" does not exists in current scene!'.format(consts.PUPPET_MAIN_GUIDE))
            return False

        guide_suffix = '_{}'.format(consts.PUPPET_GUIDE)
        if not guide_name.endswith(guide_suffix):
            guide_name = '{}{}'.format(guide_name, guide_suffix)

        if tp.Dcc.object_exists(guide_name):
            qtutils.warning_message('Guide "{}" already exists!'.format(guide_name))
            return False

        if ' ' in guide_name or '-' in guide_name or guide_name[0].isdigit():
            qtutils.warning_message('Guide "{}" cannot contains spaces, - or start with a digit'.format(guide_name))
            return False

        new_guide = puppet.create_guide(
            guide_name=guide_name, guide_parent=consts.PUPPET_MAIN_GUIDE, gizmo_shader='darkRed')

        return new_guide

    def _create_new_part(self):
        """
        Internal function that creates a new root guide in current scene
        :return:
        """

        new_part = puppet.create_part()

        tp.Dcc.fit_view()

        return new_part

    def _get_new_part_code(sel, part_name):
        """
        Internal function that returns code used by new parts
        :return: str
        """

        return """import logging

from tpRigToolkit.tools.rigbuilder.core import puppet

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)

class {}(puppet.PuppetPart, object):
    def __init__(self, name):
        super(self.__class__, self).__init__()
        
        self._name = name
        self._type = __name__.split('.')[-1]
        self._unique = False
""".format(strings.first_letter_upper(part_name.replace(' ', '')))

    def _get_new_part_metadata(self):
        """
        Internal function that returns metadata used by new parts
        :return: dict
        """

        return {
            'version': '1.0.0',
            'description': 'Puppet Part',
            'group': 'Custom',
            'advanced': False
        }

    def _create_new_part_files(self, part_name, part_directory):
        """
        Internal function that creates all the necessary files for a new part
        """

        fileio.write_to_file(os.path.join(part_directory, '__init__.py'), '')
        yamlio.write_to_file(self._get_new_part_metadata(), os.path.join(part_directory, consts.PUPPET_METADATA_FILE))
        fileio.write_to_file(
            os.path.join(part_directory, '{}.py'.format(part_name)), self._get_new_part_code(part_name))

    def _copy_part_files(self, source_part_name, source_part_directory, target_part_name, target_path_directory):
        """
        Internal function that copies all files from one puppet part to another one
        :param source_part_name: str
        :param source_part_directory: str
        :param target_part_name: str
        :param target_path_directory: str
        """

        source_init_file = os.path.join(source_part_directory, '__init__.py')
        source_metadata_file = os.path.join(source_part_directory, consts.PUPPET_METADATA_FILE)
        source_python_file = os.path.join(source_part_directory, '{}.py'.format(source_part_name))
        target_init_file = os.path.join(target_path_directory, '__init__.py')
        target_metadata_file = os.path.join(target_path_directory, consts.PUPPET_METADATA_FILE)
        target_python_file = os.path.join(target_path_directory, '{}.py'.format(target_part_name))
        fileio.copy_file(source_init_file, target_init_file)
        fileio.copy_file(source_metadata_file, target_metadata_file)
        fileio.copy_file(source_python_file, target_python_file)

    def _on_create_new_part(self):
        """
        Internal callback function that is called when New Part button is selected
        :return: bool
        """

        part_name = qtutils.get_string_input('Please enter new part name', 'Create Part')
        if not part_name:
            return False

        part_name = strings.first_letter_lower(part_name)
        part_name = part_name.replace(' ', '_')
        parts = puppet.get_part_files()
        if part_name in parts:
            qtutils.warning_message('Part "{}" already exists!'.format(part_name))
            return False

        part_dir = puppet.get_part_path(part_name=part_name)
        tp.Dcc.new_scene(force=True)

        if not os.path.isdir(part_dir):
            os.makedirs(part_dir)

        self._create_new_part()
        tp.Dcc.save_current_scene(force=True, path_to_save=part_dir, name_to_save=part_name)
        self._create_new_part_files(part_name, part_dir)

        self._setup_duplicate_menu()
        self._setup_edit_menu()
        self.update_current_module()

        return True

    def _on_duplicate_part(self, part_name):
        """
        Internal callback function that is called when an item from duplicate button menu is selected
        :param part_name: str, name of puppet part we want to duplicate
        :return: bool
        """

        dup_part_name = qtutils.get_string_input('Please enter new part name', 'Duplicate Part')
        if not dup_part_name:
            return False

        dup_part_name = strings.first_letter_lower(dup_part_name)
        dup_part_name = dup_part_name.replace(' ', '_')
        parts = puppet.get_part_files()
        if dup_part_name in parts:
            qtutils.warning_message('Part "{}" already exists!'.format(dup_part_name))
            return False

        source_part_dir = puppet.get_part_path(part_name=part_name)
        dup_part_dir = puppet.get_part_path(part_name=dup_part_name)
        part_dcc_file = puppet.get_part_dcc_file(part_name=part_name)
        if os.path.isfile(part_dcc_file):
            tp.Dcc.new_scene(force=True)
            tp.Dcc.open_file(part_dcc_file, force=True)

        if not os.path.isdir(dup_part_dir):
            os.makedirs(dup_part_dir)

        tp.Dcc.save_current_scene(path_to_save=dup_part_dir, name_to_save=dup_part_name, force=True)
        self._copy_part_files(part_name, source_part_dir, dup_part_name, dup_part_dir)
        dup_python_file = os.path.join(dup_part_dir, '{}.py'.format(dup_part_name))
        fileio.replace(
            dup_python_file,
            'class  {}'.format(strings.first_letter_upper(part_name.replace(' ', ''))),
            'class  {}'.format(strings.first_letter_upper(dup_part_name.replace(' ', '')))
        )

        self._setup_duplicate_menu()
        self._setup_edit_menu()
        self.update_current_module()

    def _on_edit_part(self, part_name):
        """
        Internal callback function that is called when an item from edit button menu is selected
        :param part_name: str, name of puppet part we want to edit
        :return: bool
        """

        part_dcc_file = puppet.get_part_dcc_file(part_name=part_name)
        if os.path.isfile(part_dcc_file):
            tp.Dcc.new_scene(force=True)
            tp.Dcc.open_file(part_dcc_file)

        self.update_current_module()

    def _on_show_part_metadata(self):
        """
        Internal callback function that is called when Add MetaData button is pressed
        """

        if not tp.Dcc.object_exists(consts.PUPPET_PART_GROUP):
            qtutils.warning_message('Current scene does not contains a valid Puppet Part!')
            return False

        part_name = os.path.splitext(os.path.basename(tp.Dcc.scene_name()))[0]
        part_dir = puppet.get_part_path(part_name=part_name)
        metadata_file = os.path.join(part_dir, consts.PUPPET_METADATA_FILE)
        if not os.path.isfile(metadata_file):
            qtutils.critical_message('Current Puppet Part does not contains a valid metadata file!'.format(part_name))
            return False

        metadata = yamlio.read_file(metadata_file)
        description = metadata.get('description', '')

        new_description = qtutils.get_comment(
            text_message='', title='Add Metadata', comment_text=description, parent=self)
        if new_description is None or new_description == description:
            return

        metadata['description'] = new_description

        yamlio.write_to_file(metadata, metadata_file)

    def _on_set_part_group(self):
        """
        Internal callback function that is called when set button is clicked
        """

        if not tp.Dcc.object_exists(consts.PUPPET_PART_GROUP):
            qtutils.warning_message('Current scene does not contains a valid Puppet Part!')
            return False

        part_name = os.path.splitext(os.path.basename(tp.Dcc.scene_name()))[0]
        part_dir = puppet.get_part_path(part_name=part_name)
        metadata_file = os.path.join(part_dir, consts.PUPPET_METADATA_FILE)

        metadata = yamlio.read_file(metadata_file)
        group = metadata.get('group', '')
        new_group = self._part_group_combo.currentText()
        if new_group and new_group == group:
            return

        metadata['group'] = new_group

        yamlio.write_to_file(metadata, metadata_file)

        self._setup_duplicate_menu()
        self._setup_edit_menu()

    def _on_create_main_guide(self):
        """
        Internal callback function that is called when create main guide button is clicked
        :return: str
        """

        return puppet.create_main_guide()

    def _on_create_guide(self):
        """
        Internal callback function that is called when create guide button is clicked
        :return: str
        """

        return self._create_guide()

    def _on_connect_guides(self):
        """
        Internal callback function that is called when connect guides button is clicked
        """

        return puppet.connect_guides()

    def _on_mirror_guide(self):
        pass