#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains main data library functionality
"""

from __future__ import print_function, division, absolute_import

import os

from tpQtLib.widgets.library import library


class DataLibrary(library.Library, object):

    Name = 'Data Library'
    Fields = ['icon', 'name', 'path', 'type', 'folder', 'category']

    def __init__(self, path=None, library_window=None, *args):
        super(DataLibrary, self).__init__(path=path, library_window=library_window, *args)

        self.set_path(path)

    def data_path(self):
        """
        Implements base library.Library data_path function
        Returns path where library data base is located
        :return: str
        """

        return os.path.join(self.path(), 'data.db')
