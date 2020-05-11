#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Procedural Script based auto rigger
"""

from __future__ import print_function, division, absolute_import

__author__ = "Tomas Poveda"
__license__ = "MIT"
__maintainer__ = "Tomas Poveda"
__email__ = "tpovedatd@gmail.com"

import os

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import logging

import tpDcc
from tpDcc.libs.python import path as path_utils
from tpDcc.libs.qt.core import window
from tpDcc.libs.qt.widgets import stack, dividers

from tpRigToolkit.tools import rigbuilder
from tpRigToolkit.tools.rigbuilder.core import utils
from tpRigToolkit.tools.rigbuilder.widgets.hub import hub
from tpRigToolkit.tools.rigbuilder.widgets.base import project, console

LOGGER = logging.getLogger('tpRigToolkit')


class RigBuilder(window.BaseWindow, object):
    def __init__(self, settings, project_name=None, parent=None):
        self._project = None
        self._project_to_open = project_name

        self._projects_widget = project.ProjectWidget()
        self._console = console.Console()
        self._hub_widget = hub.HubWidget(settings=settings, console=self._console)
        self._project_settings_widget = project.ProjectSettingsWidget()
        self._toolbar = None
        self._progress_toolbar = None

        super(RigBuilder, self).__init__(settings=settings, parent=parent)

        # Force initialization of managers
        rigbuilder.DataMgr()
        rigbuilder.PkgsMgr().register_package_path(
            path_utils.clean_path(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'packages')))
        for data_file_dir in utils.get_script_files_directory():
            rigbuilder.ScriptsMgr().add_directory(data_file_dir)

        self._projects_widget.set_settings(self._settings)
        self._hub_widget.set_settings(self._settings)

        self._console_dock = self.add_dock('Console', widget=self._console, pos=Qt.BottomDockWidgetArea, tabify=False)
        self._console_dock.setVisible(False)

        self._toolbar = self._setup_toolbar()
        self._progress_toolbar = self._setup_progress_bar()
        self._hub_widget.set_progress_bar(self._progress_toolbar)
        self._setup_menubar()

        self._toolbar.setVisible(False)
        self._progress_toolbar.setVisible(False)
        self.menuBar().setVisible(False)

    #     self._register_tools()
        if self._project_to_open:
            self.open_project(self._project_to_open)

    def ui(self):
        super(RigBuilder, self).ui()

        self._stack = stack.SlidingStackedWidget()
        self.main_layout.addWidget(self._stack)

        self._stack.addWidget(self._projects_widget)
        self._stack.addWidget(self._hub_widget)
        self._stack.addWidget(self._project_settings_widget)

        self._console.setVisible(False)

    def setup_signals(self):
        self._projects_widget.projectOpened.connect(self._on_open_project)
        self._project_settings_widget.exitSettings.connect(self._on_open_project)

    # ============================================================================================================
    # PROJECT
    # ============================================================================================================

    def get_project(self):
        """
        Returns current project opened in rigbuilder
        :return: project.Project
        """

        return self._project

    def set_project(self, project):
        """
        Sets project opened in rigbuilder
        :param project: project.Project
        """

        self._project = project
        self._hub_widget.set_project(project)
        self._project_settings_widget.set_project(project)
        rigbuilder.project = project

    def open_project(self, project_name):
        """
        Open a project by its name
        :param project_name: str, name of the project to open
        """

        project_to_open = self._projects_widget.get_project_by_name(project_name)
        if not project_to_open:
            LOGGER.warning('Project with name {} not found!'.format(project_name))
            return

        self.set_project(project_to_open)
        self._open_project_widget()

    # ============================================================================================================
    # CONSOLE
    # ============================================================================================================

    def get_console(self):
        """
        Returns console widget
        :return: Console
        """

        return self._console

    # ============================================================================================================
    # INTERNAL
    # ============================================================================================================

    def _open_project_widget(self):
        """
        Internal function that opens current set project
        """

        if not self._project:
            LOGGER.warning('Impossible to open project. Project is not defined.')
            self._project_options_action.setIcon(QIcon())
            self._project_options_action.setText('')
            return False

        self._project_options_action.setIcon(QIcon(self._project.get_project_image()))
        self._project_options_action.setText(self._project.name.title())

        self._console.setVisible(True)
        self._console_dock.setVisible(True)
        self._console.clear()
        self._console.write('>> Opening Project: {} ...'.format(self._project.name))
        self._toolbar.setVisible(True)
        self.menuBar().setVisible(True)
        self._progress_toolbar.setVisible(False)
        self._stack.slide_in_index(1)
        self._console.write_ok('>> Project {} opened successfully!'.format(self._project.name))

    def _open_projects_widget(self):
        """
        Internal function that opens project selector widget
        """

        self._console.setVisible(False)
        self._console_dock.setVisible(False)
        self._console.clear()
        self.set_project(None)
        self._toolbar.setVisible(False)
        self.menuBar().setVisible(False)
        self._progress_toolbar.setVisible(False)
        self._stack.slide_in_index(0)

    def _open_project_options(self):
        if not self._project:
            LOGGER.warning('Impossible to open project settings. Project is not defined.')
            return False

        self._stack.slide_in_index(2)
        self._toolbar.setVisible(False)
        self.menuBar().setVisible(False)

    def _setup_toolbar(self):
        """
        Internal function used to setup RigBuilder toolbar
        """

        toolbar = self.add_toolbar('Main Toolbar')
        toolbar.setMovable(True)
        toolbar.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)

        play_icon = tpDcc.ResourcesMgr().icon('play')
        home_icon = tpDcc.ResourcesMgr().icon('home')

        project_options_btn = QToolButton()
        project_options_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self._project_options_action = QAction('', project_options_btn)
        project_options_btn.setDefaultAction(self._project_options_action)

        run_build_btn = QToolButton()
        run_build_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        run_build_action = QAction(play_icon, 'Run', run_build_btn)
        run_build_btn.setDefaultAction(run_build_action)

        browse_btn = QToolButton()
        browse_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        browse_action = QAction(home_icon, 'Browse', run_build_btn)
        browse_btn.setDefaultAction(browse_action)

        toolbar.addWidget(project_options_btn)
        toolbar.addSeparator()
        toolbar.addWidget(run_build_btn)
        toolbar.addSeparator()
        toolbar.addWidget(browse_btn)

        project_options_btn.clicked.connect(self._on_open_project_options)
        run_build_btn.clicked.connect(self._on_run_build)

        return toolbar

    def _setup_progress_bar(self):
        """
        Internal function used to setup RigBuilder progress bar widget
        """

        progress_toolbar = self.add_toolbar(name='ProgressToolBar')
        progress_toolbar.setAllowedAreas(Qt.TopToolBarArea | Qt.BottomToolBarArea)
        continue_icon = tpDcc.ResourcesMgr().icon('resume')
        stop_icon = tpDcc.ResourcesMgr().icon('stop')
        self._stop_btn = QToolButton()
        self._stop_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        stop_action = QAction(stop_icon, 'Stop (Hold ESC)', self._stop_btn)
        self._stop_btn.setDefaultAction(stop_action)
        self._stop_btn.setEnabled(False)
        self._continue_btn = QToolButton()
        self._continue_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        continue_action = QAction(continue_icon, 'Continue', self._continue_btn)
        self._continue_btn.setDefaultAction(continue_action)
        self._continue_btn.setEnabled(False)
        progress_widget = QWidget()
        progress_layout = QVBoxLayout()
        progress_layout.setContentsMargins(2, 2, 2, 2)
        progress_layout.setSpacing(2)
        progress_layout.setAlignment(Qt.AlignCenter)
        progress_widget.setLayout(progress_layout)
        self.progress_bar = QProgressBar()
        self._progress_bar_text = QLabel('-')
        progress_layout.addWidget(self.progress_bar)
        progress_layout.addLayout(dividers.DividerLayout())
        progress_text_layout = QHBoxLayout()
        progress_text_layout.setContentsMargins(0, 0, 0, 0)
        progress_text_layout.setSpacing(0)
        progress_text_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        progress_text_layout.addWidget(self._progress_bar_text)
        progress_text_layout.addItem(QSpacerItem(10, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        progress_layout.addLayout(progress_text_layout)

        progress_toolbar.addWidget(self._stop_btn)
        progress_toolbar.addWidget(self._continue_btn)
        progress_toolbar.addSeparator()
        progress_toolbar.addWidget(progress_widget)

        return progress_toolbar

    def _setup_menubar(self):
        """
        Internal function used to setup menubar
        """

        file_menu = QMenu('File')
        for menu in [file_menu]:
            self.menuBar().addMenu(menu)

        go_back_icon = tpDcc.ResourcesMgr().icon('open_door')
        go_back_action = QAction(go_back_icon, 'Go to Projects', file_menu)
        file_menu.addAction(go_back_action)

        go_back_action.triggered.connect(self._on_go_to_projects)

    # def _register_tools(self):
    #     """
    #     Internal function that registers all available tools for tpRigToolkit.tools.rignode
    #     """
    #
    #     if not self._hub_widget.tools_classes:
    #         LOGGER.info('No tools available!')
    #         return
    #
    #     settings = self.settings()
    #     for tool_class in self._hub_widget.tools_classes:
    #         if issubclass(tool_class, tool.DockTool):
    #             tools_menu = qtutils.get_or_create_menu(self.menuBar(), 'Tools')
    #             self.menuBar().addMenu(tools_menu)
    #             show_tool_action = tools_menu.addAction(tool_class.NAME)
    #             icon = tool_class.icon()
    #             if icon:
    #                 show_tool_action.setIcon(icon)
    #             show_tool_action.triggered.connect(partial(self._hub_widget.invoke_dock_tool_by_name, tool_class.NAME))
    #             # show_tool_action.triggered.connect(
    #             #     lambda tool_name=tool_class.NAME: self._hub_widget.invoke_dock_tool_by_name(tool_name))
    #             settings.beginGroup('DockTools')
    #             child_groups = settings.childGroups()
    #             for dock_tool_group_name in child_groups:
    #                 settings.beginGroup(dock_tool_group_name)
    #                 if dock_tool_group_name in [t.unique_name() for t in self._tools]:
    #                     continue
    #                 tool_name = dock_tool_group_name.split('::')[0]
    #                 self._hub_widget.invoke_dock_tool_by_name(tool_name, settings)
    #                 settings.endGroup()
    #             settings.endGroup()

    # ============================================================================================================
    # CALLBACKS
    # ============================================================================================================

    def _on_open_project(self, project=None):
        """
        Internal callback function that is called when a project is selected on
        the ProjectsWidget UI
        :param project: project.Project
        """

        if project:
            self.set_project(project)
        else:
            if not self._project:
                LOGGER.warning('Impossible to retrieve already opened project! Restart the tool please')
                return False

        self._open_project_widget()

        return True

    def _on_go_to_projects(self):
        """
        Internal callback function that is called when the user selects Go to Projects action
        """

        self._open_projects_widget()

    def _on_open_project_options(self):
        """
        Internal callback function that is called when the user selects Project Options tool button
        """

        self._open_project_options()

    def _on_run_build(self):
        print('RUNNING BUILD ...')
