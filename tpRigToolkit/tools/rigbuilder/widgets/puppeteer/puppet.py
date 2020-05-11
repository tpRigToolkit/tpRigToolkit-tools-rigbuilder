#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains puppeteer widget for RigBuilder
"""

from __future__ import print_function, division, absolute_import

from Qt.QtCore import *
from Qt.QtWidgets import *

import tpDcc as tp
from tpDcc.libs.qt.core import base

from tpRigToolkit.tools.rigbuilder.core import consts, puppet


class PuppetWidget(base.BaseWidget, object):

    puppetCreated = Signal()
    puppetRemoved = Signal()

    def __init__(self, parent=None):
        super(PuppetWidget, self).__init__(parent=parent)

        self._puppet = puppet.Puppet()
        self.refresh()

    @property
    def puppet(self):
        return self._puppet

    def ui(self):
        super(PuppetWidget, self).ui()

        top_buttons_layout = QHBoxLayout()
        self._new_btn = QPushButton('New')
        self._delete_btn = QPushButton('Delete')
        self._delete_btn.setEnabled(False)
        top_buttons_layout.addWidget(self._new_btn)
        top_buttons_layout.addWidget(self._delete_btn)

        self.main_layout.addLayout(top_buttons_layout)

    def setup_signals(self):
        self._new_btn.clicked.connect(self._on_create_new_puppet)
        self._delete_btn.clicked.connect(self._on_delete_puppet)

    def refresh(self):
        """
        Function that updates puppet widget UI
        """

        puppet_exists = self._puppet.exists
        if puppet_exists:
            puppet_name = self._puppet.name

        self._new_btn.setEnabled(not puppet_exists)
        self._delete_btn.setEnabled(puppet_exists)

    def create_puppet(self, name=''):
        """
        Creates a new puppet in current DCC scene
        :param str name: name of the puppet we want to create. If empty, a message box will ask user to type a name
        """

        if tp.Dcc.object_exists(consts.PUPPET_MAIN_GROUP):
            tp.Dcc.warning('Group "{}" already exists!'.format(consts.PUPPET_MAIN_GROUP))
            return False
        if tp.Dcc.object_exists(consts.PUPPET_RIG_GROUP):
            tp.Dcc.warning('Group "{}" already exists!'.format(consts.PUPPET_RIG_GROUP))
            return False
        if tp.Dcc.object_exists(consts.PUPPET_GEO_GROUP):
            tp.Dcc.warning('Group "{}" already exists!'.format(consts.PUPPET_GEO_GROUP))
            return False

        self._puppet.create()
        self.puppetCreated.emit()
        self.refresh()

    def delete_puppet(self):
        """
        Deletes puppet created in current scene
        """

        if not self._puppet or not self._puppet.exists:
            return False

        self._puppet.delete()
        self.puppetRemoved.emit()

    def _on_create_new_puppet(self):
        """
        Internal callback function that is called when create new button is pressed
        """

        return self.create_puppet()

    def _on_delete_puppet(self):
        """
        Internal callback function that is called when delete button is pressed
        """

        return self.delete_puppet()
