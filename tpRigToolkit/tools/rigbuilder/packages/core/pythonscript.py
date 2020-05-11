#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains build node implementation for scripts
"""

from __future__ import print_function, division, absolute_import

import os

import tpDcc
from tpDcc.libs.python import fileio, path as path_utils

from tpRigToolkit.tools.rigbuilder.objects import build


class PythonScript(build.BuildObject, object):

    COLOR = [125, 125, 0]
    SHORT_NAME = 'PYTHON'
    DESCRIPTION = 'Launches a Python script'
    ICON = 'python'

    def __init__(self, name=None):
        super(PythonScript, self).__init__(name=name)

    def run(self, **kwargs):
        self._create_python_file()
        python_file = self.get_python_file()

        return self.run_script(python_file, **kwargs)

    def get_python_file(self):
        """
        Returns path where Python file should be located
        :return: str
        """

        return path_utils.clean_path(os.path.join(self.get_path(), '{}.py'.format(self.get_name().split('/')[-1])))

    def setup_context_menu(self, menu):
        external_icon = tpDcc.ResourcesMgr().icon('external')
        new_window_icon = tpDcc.ResourcesMgr().icon('new_window')

        external_window_action = menu.addAction(external_icon, 'Open in External')
        new_window_action = menu.addAction(new_window_icon, 'Open in New Window')

        external_window_action.triggered.connect(self._on_open_external)
        new_window_action.triggered.connect(self._on_open_new_window)

    def setup_options(self):
        self._create_python_file()
        return super(PythonScript, self).setup_options()

    def _create_python_file(self):
        """
        Internal function that creates Python file if it does not already exists
        """

        python_file = self.get_python_file()
        if not os.path.isfile(python_file):
            with open(python_file, 'w') as f:
                f.write('def main():\n    pass\n')

    def _on_open_external(self):
        self._create_python_file()

        fileio.open_browser(self.get_python_file())

    def _on_open_new_window(self):
        self._create_python_file()

        raise NotImplementedError('open in new window functionality is not implemented yet!')