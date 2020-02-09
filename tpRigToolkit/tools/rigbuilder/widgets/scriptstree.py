#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget to show scripts tree
"""

from __future__ import print_function, division, absolute_import

import os
import logging

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDccLib as tp
from tpDccLib.core import scripts
from tpPyUtils import osplatform, timers, fileio, path as path_utils
from tpQtLib.core import qtutils

from tpRigToolkit.core import resource
from tpRigToolkit.tools.rigbuilder.core import utils
from tpRigToolkit.tools.rigbuilder.widgets import buildtree

LOGGER = logging.getLogger('tpRigToolkit')


class ScriptItemSignals(QObject, object):

    createPythonCode = Signal()
    createData = Signal()
    runCode = Signal()
    renameCode = Signal()
    duplicateCode = Signal()
    deleteCode = Signal()
    browseCode = Signal()


class ScriptItem(buildtree.BuildItem, object):

    scriptSignals = ScriptItemSignals()

    def __init__(self, parent=None):

        self.handle_manifest = False

        super(ScriptItem, self).__init__(parent)

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def setData(self, column, role, value):
        """
        Overrides base QTreeWidgetItem setData function
        :param column: int
        :param role: QRole
        :param value: variant
        """

        super(ScriptItem, self).setData(column, role, value)

        if value == 0:
            check_state = Qt.Unchecked
        elif value == 2:
            check_state = Qt.Checked

        if role == Qt.CheckStateRole:
            if self.handle_manifest:
                tree = self.treeWidget()
                tree.update_scripts_manifest()
                if tree._shift_activate:
                    child_count = self.childCount()
                    for i in range(child_count):
                        child = self.child(i)
                        child.setCheckedState(column, check_state)
                        children = tree._get_ancestors(child)
                        for child in children:
                            child.setCheckedState(column, check_state)

    def _create_context_menu(self):
        """
        Overrides base BuildItem create_context_menu function
        Creates context menu for this item
        :return: QMenu
        """

        self._context_menu = QMenu()

        python_icon = resource.ResourceManager().icon('python')
        import_icon = resource.ResourceManager().icon('import')
        play_icon = resource.ResourceManager().icon('play')
        rename_icon = resource.ResourceManager().icon('rename')
        duplicate_icon = resource.ResourceManager().icon('clone')
        delete_icon = resource.ResourceManager().icon('delete')
        browse_icon = resource.ResourceManager().icon('open')
        external_icon = resource.ResourceManager().icon('external')
        new_window_icon = resource.ResourceManager().icon('new_window')

        new_python_action = self._context_menu.addAction(python_icon, 'New Python Code')
        new_data_import_action = self._context_menu.addAction(import_icon, 'New Data Import')
        self._context_menu.addSeparator()
        run_action = self._context_menu.addAction(play_icon, 'Run')
        rename_action = self._context_menu.addAction(rename_icon, 'Rename')
        duplicate_action = self._context_menu.addAction(duplicate_icon, 'Duplicate')
        delete_action = self._context_menu.addAction(delete_icon, 'Delete')
        self._context_menu.addSeparator()
        browse_action = self._context_menu.addAction(browse_icon, 'Browse')
        external_window_action = self._context_menu.addAction(external_icon, 'Open in External')
        new_window_action = self._context_menu.addAction(new_window_icon, 'Open in New Window')

        new_python_action.triggered.connect(self.scriptSignals.createPythonCode.emit)
        run_action.triggered.connect(self.scriptSignals.runCode.emit)
        rename_action.triggered.connect(self.scriptSignals.renameCode.emit)
        duplicate_action.triggered.connect(self.scriptSignals.duplicateCode.emit)
        delete_action.triggered.connect(self.scriptSignals.deleteCode.emit)
        browse_action.triggered.connect(self.scriptSignals.browseCode.emit)
        external_window_action.triggered.connect(self._on_open_in_external)
        new_window_action.triggered.connect(self._on_open_in_window)

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def get_code_name(self, remove_extension=False):
        """
        Returns item code path
        :return: str
        """

        script_name = path_utils.get_basename(self.get_text(), with_extension=False)
        script_path = self.get_path()
        if script_path:
            script_name = path_utils.join_path(script_path, script_name)

        if remove_extension:
            return fileio.remove_extension(script_name)

        return script_name

    # ================================================================================================
    # ======================== CALLBACKS
    # ================================================================================================

    def _on_open_in_external(self):
        """
        Internal callback function that opens script in external editor
        :param item: ScripItem
        :return:
        """

        current_object = self.get_object()
        if not current_object:
            LOGGER.warning('Impossible to open script because object is not defined!')
            return

        code_name = self.get_code_name(remove_extension=True)
        code_file = current_object.get_code_file(code_name)
        if not code_file or not os.path.isfile(code_file):
            LOGGER.warning('Impossible to open script "{}" because it does not exists!'.format(code_file))
            return

        # TODO: Add support for custom external editors
        # external_editor = self._settings.get('external_directory')
        # if external_editor:
        #     p = subprocess.Popen([external_editor, code_file])

        fileio.open_browser(code_file)

    def _on_open_in_window(self, item=None):
        """
        Internal callback function that opens script in script editor
        :param item: ScripItem
        :return:
        """

        current_object = self.get_object()
        if not current_object:
            LOGGER.warning('Impossible to open script because object is not defined!')
            return

        code_name = self.get_code_name(remove_extension=True)
        code_file = current_object.get_code_file(code_name)
        if not code_file or not os.path.isfile(code_file):
            LOGGER.warning('Impossible to open script "{}" because it does not exists!'.format(code_file))
            return

        raise NotImplementedError('open in new window functionality is not implemented yet!')


class ScriptTree(buildtree.BuildTree, object):

    HEADER_LABELS = ['Scripts']
    ITEM_WIDGET = ScriptItem
    NEW_ITEM_NAME = 'new_script'

    itemSignalsConnected = False
    scriptOpened = Signal(object, bool, bool)
    scriptOpenedInExternal = Signal()

    python_icon = resource.ResourceManager().icon('python')
    python_expand_icon = resource.ResourceManager().icon('python_expand')
    python_no_expand_icon = resource.ResourceManager().icon('python_no_expand')

    def __init__(self, settings=None, parent=None):
        super(ScriptTree, self).__init__(settings=settings, parent=parent)

        self._allow_scripts_manifest_update = True

    # ================================================================================================
    # ======================== OVERRIDES
    # ================================================================================================

    def drawBranches(self, painter, rect, index):
        """
        Overrides base treewidgets.FileTreeWidget drawBranches function
        Draws custom icons for scripts tree items
        :param painter: QPainter
        :param rect: QRect
        :param index: QModelIndex
        """

        if index:
            item = self.itemFromIndex(index)
            item_text = item.get_text()
            if item_text.endswith('.py'):
                if item.childCount() <= 0:
                    self.python_icon.paint(painter, rect)
                else:
                    if item.isExpanded():
                        self.python_expand_icon.paint(painter, rect)
                    else:
                        self.python_no_expand_icon.paint(painter, rect)
            else:
                super(ScriptTree, self).drawBranches(painter, rect, index)
        else:
            super(ScriptTree, self).drawBranches(painter, rect, index)

    def mouseDoubleClickEvent(self, event):
        item = None
        items = self.selectedItems()
        if items:
            item = items[0]
        if not item:
            return

        settings = self.settings()
        if not settings:
            self.scriptOpened.emit(item, False, False)
            return

        settings.beginGroup('Code')
        double_click_option = settings.get('script_double_click')
        if double_click_option:
            if double_click_option == 'open_tab':
                self.scriptOpened.emit(item, False, False)
            elif double_click_option == 'open_new':
                self._on_open_in_window(item)
            elif double_click_option == 'open_external':
                self._on_open_in_external(item)
        else:
            self.scriptOpened.emit(item, False, False)
        settings.endGroup()

    def _get_invalid_code_names(self):
        """
        Overrides base BuildTree _get_invalid_code_names function
        Internal function that returns a list not valid code names
        :return: list(str)
        """

        return ['manifest', 'manifest.py']

    def _add_item(self, file_name, state, parent=None, **kwargs):
        """
        Overrides base BuildTree _add_item function
        Internal function that adds a new item to the script tree
        :param file_name: str
        :param state: int
        :param parent: ScriptItem
        :return: ScriptItem
        """

        item = super(ScriptTree, self)._add_item(file_name=file_name, state=state, parent=parent, **kwargs)

        update_manifest = kwargs.get('update_manifest', False)
        if update_manifest:
            self.update_scripts_manifest()

        return item

    def _add_items(self, files, item=None):
        """
        Overrides base BuildTree _add_items function
        Internal function used to add new scripts file to the given script item
        :param files: list(str)
        :param item: ScriptItem
        """

        scripts, states, parents = files
        script_count = len(scripts)
        found_false = False
        built_parents = dict()

        for i in range(script_count):
            script_name = scripts[i].split('.')[0]
            basename = path_utils.get_basename(scripts[i])
            dir_name = path_utils.get_dirname(scripts[i])
            current_parent = None
            if dir_name in parents and dir_name in built_parents:
                current_parent = built_parents[dir_name]
            item = self._add_item('...temp...', states[i], parent=current_parent, update_manifest=False)
            if script_name in parents:
                built_parents[script_name] = item
            if dir_name in parents and dir_name in built_parents:
                item.set_text(basename)
            if not dir_name:
                self.addTopLevelItem(item)
                item.set_text(basename)

            if not states[i]:
                found_false = True

        orig_update_checkbox = self._update_checkbox
        self._update_checkbox = False
        if found_false:
            self._checkbox.setChecked(False)
        else:
            self._checkbox.setChecked(True)
        self._update_checkbox = orig_update_checkbox

    def _get_files(self, scripts=None, states=None):
        """
        Overrides base BuildTree _get_files function
        Internal function that returns all scripts and its states located in the current scripts tree directory
        :param scripts: list(str)
        :param states: list(str)
        :return: list(list, list)
        """

        if scripts is None:
            scripts = list()
        if states is None:
            states = list()

        current_object = self.object()
        if not current_object:
            LOGGER.debug('Impossible to get script files because object is not defined!')
            return

        if not scripts:
            scripts, states = current_object.get_scripts_manifest()
        if not scripts:
            LOGGER.debug('Current object has no scripts!')
            return

        code_folders = current_object.get_code_folders()
        found_scripts = list()
        found_states = list()
        parents = dict()

        for i in range(len(scripts)):
            script_name = fileio.remove_extension(scripts[i])
            if not script_name in code_folders:
                continue
            script_path = current_object.get_code_file(script_name)
            if not script_path or not path_utils.is_file(script_path):
                continue

            if script_name.count('/') > 0:
                dir_name = path_utils.get_dirname(script_name)
                parents[dir_name] = scripts[i]

            found_scripts.append(scripts[i])
            found_states.append(states[i])

        return [found_scripts, found_states, parents]

    def _setup_item(self, item, state):
        """
        Overrides base BuildTree _setup_item function
        Internal function that is called before adding an item into the tree
        It is used to set item before adding it
        :param item: ScriptManifestItem
        :param state: bool
        :return:
        """

        super(ScriptTree, self)._setup_item(item=item, state=state)

        if not self.itemSignalsConnected:
            item.scriptSignals.createPythonCode.connect(self._on_create_python_code)
            item.scriptSignals.runCode.connect(self._on_run_current_item)
            item.scriptSignals.renameCode.connect(self._on_rename_current_item)
            item.scriptSignals.duplicateCode.connect(self._on_duplicate_current_item)
            item.scriptSignals.deleteCode.connect(self._on_delete_current_item)
            item.scriptSignals.browseCode.connect(self._on_browse_code)

        # Used to avoid script manifest update when check states of ScriptManifestItem is changed programatically
        if hasattr(item, 'handle_manifest'):
            item.handle_manifest = True

        self.itemSignalsConnected = True

    def _rename_item(self, item, new_name):
        """
        Overrides base BuildTree _rename_item function
        Internal function that renames with script item
        :param item: ScriptItem
        :param new_name: str
        """

        super(ScriptTree, self)._rename_item(item=item, new_name=new_name)

        self.update_scripts_manifest()

    def _move_item(self, old_name, new_name, item):
        """
        Overrides base BuildTree _move_item function
        Internal function that handles the move of an item in the file system
        :param old_name: str
        :param new_name: str
        :param item: ScriptItem
        """
        after_name = self._handle_item_reparent(old_name, new_name)
        basename = path_utils.get_basename(after_name)
        item.set_text(basename + '.py')
        self.itemRenamed.emit(old_name, after_name)

    def _create_actions(self, context_menu):
        """
        Overrides base BuildTree _create_new_actions function
        Internal function that creates actions for the creation of new items
        :param context_menu: QMenu
        :return: list(QAction)
        """

        python_icon = resource.ResourceManager().icon('python')
        import_icon = resource.ResourceManager().icon('import')
        browse_icon = resource.ResourceManager().icon('open')
        refresh_icon = resource.ResourceManager().icon('refresh')

        new_python_action = context_menu.addAction(python_icon, 'New Python Code')
        new_data_import_action = context_menu.addAction(import_icon, 'New Data Import')
        context_menu.addSeparator()
        browse_action = context_menu.addAction(browse_icon, 'Browse')
        context_menu.addSeparator()
        refresh_action = self._context_menu.addAction(refresh_icon, 'Refresh')

        new_python_action.triggered.connect(self._on_create_python_code)
        new_data_import_action.triggered.connect(self._on_create_data_import)
        browse_action.triggered.connect(self._on_browse_code)
        refresh_action.triggered.connect(self._on_refresh)

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def refresh(self, sync=False, scripts_and_states=list()):
        """
        Overrides base treewidgets.FileTreeWidget refresh function
        """

        if self._break_item:
            break_item_path = self._get_item_path_name(self._break_item, keep_extension=True)
        if self._start_item:
            start_item_path = self._get_item_path_name(self._start_item, keep_extension=True)

        if sync:
            self._sync_scripts()

        orig_scripts_manifest_update = self._allow_scripts_manifest_update
        self._allow_scripts_manifest_update = False
        if scripts_and_states:
            self._custom_refresh(scripts_and_states[0], scripts_and_states[1])
        else:
            super(ScriptTree, self).refresh()
        self._allow_scripts_manifest_update = orig_scripts_manifest_update

        if self._start_item:
            item = self._get_item_by_name(start_item_path)
            if item:
                self.set_start_point(item)

        if self._break_item:
            item = self._get_item_by_name(break_item_path)
            if item:
                self.set_break_point(item)

    # ================================================================================================
    # ======================== MANIFEST
    # ================================================================================================

    def get_current_scripts_manifest(self):
        """
        Returns the current script manifest of the rig
        :return:
        """

        scripts = list()
        states = list()

        items = self._get_all_items()
        for item in items:
            item_name = item.get_text()
            item_path = self.get_item_path(item)
            if item_path:
                item_name = path_utils.join_path(item_path, item_name)

            state = item.checkState(0)
            if state == 0:
                state = False
            elif state == 2:
                state = True

            scripts.append(item_name)
            states.append(state)

        return scripts, states

    def update_scripts_manifest(self):
        """
        Forces the update (if allowed) of the scripts manifest
        """

        if not self._allow_scripts_manifest_update:
            return

        current_object = self.object()
        if not current_object:
            LOGGER.debug('Impossible to get object files because script object is not defined!')
            return

        scripts, states = self.get_current_scripts_manifest()
        current_object.set_scripts_manifest(scripts, states)

    # ================================================================================================
    # ======================== INTERNAL
    # ================================================================================================

    def _handle_item_reparent(self, old_name, new_name):
        """
        Internal function that handles the parenting of script tree script items
        :param old_name: str
        :param new_name: str
        :return: str
        """

        if old_name == new_name:
            return old_name

        current_object = self.object()
        if not current_object:
            LOGGER.warning('Impossible to handle item reparent because object is not defined!')
            return

        new_name = current_object.move_code(old_name, new_name)

        return new_name

    def _activate_rename(self):
        """
        Function that allows the user to type a new name script name
        """

        # current_library = self.library()
        # if not current_library:
        #     LOGGER.warning('Impossible to rename current item because data library is not defined!')
        #     return

        items = self.selectedItems()
        if not items:
            return
        item = items[0]

        self._old_name = str(item.get_text())
        new_name = utils.show_rename_dialog('Rename item', 'Rename the current item to:', self._old_name)
        if new_name == self._old_name:
            return True
        if not new_name:
            return

        if new_name == 'manifest' or new_name == 'manifest.py':
            qtutils.warning_message('Manifest name is reserved. Name your script something else', parent=self)
            return

        self._rename_item(item, new_name)

        return True

    def _run_item(self, item, object=None):
        """
        Internal function that launches given ScripItem with given rig
        :param item: ScriptItem
        :param object: object
        """

        if object is None:
            object = self.object()
        if not object:
            LOGGER.warning('Impossible to run script/s because rig is not defined!')
            return

        self.scrollToItem(item)
        item.set_state(4)
        item.setExpanded(True)

        background = item.background(0)
        orig_background = background
        color = QColor(1, 0, 0)
        background.setColor(color)
        item.setBackground(0, background)

        script_name = self._get_item_path_name(item)
        code_file = object.get_code_file(script_name)

        status = object.run_script(code_file, False)

        if status == 'Success':
            item.set_state(1)
            log = osplatform.get_env_var('RIGBUILDER_LAST_TEMP_LOG')
            if log:
                if log.find('Warning') > -1 or log.find('WARNING') > -1 or log.find('warning') > -1:
                    item.set_state(2)
        else:
            item.set_state(0)

        item.setBackground(0, orig_background)

    # ================================================================================================
    # ======================== CALLBACKS
    # ================================================================================================

    def _on_create_python_code(self):
        """
        Internal callback function that is triggered when New Python Code action is selected
        Creates a new Python Script
        """

        current_object = self.object()
        if not current_object:
            LOGGER.warning('Impossible to create new python code because build object is not defined!')
            return

        code_name = self._get_code_name()
        if not code_name:
            return

        code_path = current_object.create_code(code_name, scripts.ScriptTypes.Python, unique_name=True)
        if not code_path:
            LOGGER.error('Impossible to create new code!')
            return

        code_name = path_utils.get_basename(code_path)
        parent_item = None
        items = self.selectedItems()
        if items:
            parent_item = items[0]
        item = self._add_item(code_name, False)
        item.setCheckState(0, Qt.Checked)
        self._reparent_item(code_name, item, parent_item)
        self.scrollToItem(item)
        self.setItemSelected(item, True)
        self.setCurrentItem(item)

        self.itemCreated.emit(item)

    def _on_create_data_import(self, data_name=None, data_extension=None):
        """
        Internal callback function that is triggered when New Import Data action is selected
        """

        print('creating data ...')

        # from tpRigTask.widgets import data
        #
        # current_rig = self.rig()
        # if not current_rig:
        #     tpRigBuilder.logger.warning('Impossible to create new data import code because rig is not defined!')
        #     return
        #
        # parent_item = None
        # items = self.selectedItems()
        # if items:
        #     parent_item = items[0]
        #
        # if not data_name:
        #     raise NotImplementedError('Creating data from scratch is not supported yet!')
        #     # data_picker = data.PickerDataWidget()
        #     # data_picker.exec_()
        #     # data_picked = data_picker.selected_data
        #     # if not data_picked:
        #     #     rigtask.logger.warning('Selected Data {} is not valid!'.format(data_picked))
        #     #     return
        #     # data_name = data_picked.file_name_line.text()
        #
        # import_data = data_name if data_extension is None else '{}{}'.format(data_name, data_extension)
        # code_path = current_rig.create_code(name='import_{}'.format(data_name), data_type=scripts.ScriptTypes.Python, unique_name=True, import_data=import_data)
        # basename = path.get_basename(code_path)
        # item = self._add_item(basename, False)
        # item.setCheckState(0, Qt.Checked)
        # self._reparent_item('import_{}'.format(data_name), item, parent_item)
        # self.scrollToItem(item)
        # self.setItemSelected(item, True)
        # self.setCurrentItem(item)

    def _on_run_current_item(self, external_code_library=None):
        """
        Internal function that executes current item
        :param external_code_library:

        """

        current_object = self.object()
        if not current_object:
            LOGGER.warning('Impossible to run script because object is not defined!')
            return

        osplatform.set_env_var('__SCRIPT_RUN__', True)
        osplatform.set_env_var('__SCRIPT_STOP__', False)

        scripts, states = current_object.get_scripts_manifest()
        items = self.selectedItems()
        if len(items) > 1:
            value = qtutils.get_permission('Start a new scene', parent=self)
            if value:
                tp.Dcc.new_scene(force=True, do_save=False)
            else:
                return

        watch = timers.StopWatch()
        watch.start(feedback=False)

        for item in items:
            item.set_state(-1)

        if external_code_library:
            current_rig.set_external_code_library(external_code_library)

        last_name = items[-1].text(0)
        last_path = self.get_item_path(items[-1])
        if last_path:
            last_name = path_utils.join_path(last_path, last_name)

        set_end_states = False
        for i in range(len(scripts)):
            if osplatform.get_env_var('__SCRIPT_RUN__') == 'True':
                if osplatform.get_env_var('__SCRIPT_STOP__') == 'True':
                    break

                if set_end_states:
                    item = self._get_item_by_name(scripts[i])
                    if item:
                        item.set_state(-1)
                for item in items:
                    script_name = item.text(0)
                    script_path = self.get_item_path(item)
                    if script_path:
                        script_name = path.join_path(script_path, script_name)
                    if script_name == scripts[i]:
                        self._run_item(item, current_object)
                        if not item.isExpanded():
                            child_count = item.childCount()
                            if child_count:
                                item.setExpanded(True)
                                for i in range(child_count):
                                    child_item = item.child(i)
                                    child_item.set_state(-1)
                                for i in range(child_count):
                                    child_item = item.child(i)
                                    self._run_item(child_item, current_object)
                                item.setExpanded(False)

                        if script_name == last_name:
                            set_end_states = True

        osplatform.set_env_var('__SCRIPT_RUN__', False)
        osplatform.set_env_var('__SCRIPT_STOP__', False)

        minutes, seconds = watch.stop()
        if minutes:
            LOGGER.info('Rig Scripts run in {} minutes and {} seconds'.format(minutes, seconds))
        else:
            LOGGER.info('Rig Scripts run in {} seconds'.format(seconds))

    def _on_rename_current_item(self):
        """
        Internal callback function that is triggered when the Rename action is clicked
        :return:
        """

        self._activate_rename()

    def _on_duplicate_current_item(self):
        """
        Internal callback function that is triggered when the Duplicate Item action is clicked
        """

        current_object = self.object()
        if not current_object:
            LOGGER.warning('Impossible to duplicate script because object is not defined!')
            return

        self.setFocus(Qt.ActiveWindowFocusReason)
        items = self.selectedItems()
        item = items[0]
        script_name = self._get_item_path_name(item)
        code_file = current_object.get_code_file(script_name)
        parent_item = item.parent()
        code_path = current_object.create_code(script_name, scripts.ScriptTypes.Python, unique_name=True)
        file_lines = fileio.get_file_lines(code_file)
        fileio.write_lines(code_path, file_lines, append=True)
        path_name = path_utils.get_basename(code_path)
        item = self._add_item(path_name, False)
        item.setCheckState(0, Qt.Checked)
        self._reparent_item(path_name, item, parent_item)
        self.itemDuplicated.emit()
        valid_rename = self._activate_rename()
        if not valid_rename:
            self._on_delete_current_item(force=True)
        self.scrollToItem(item)
        self.setItemSelected(item, True)
        self.setCurrentItem(item)

        return item

    def _on_delete_current_item(self, force=False):
        """
        Internal callback funtion that is triggerd when delete item action is clicked
        """

        current_object = self.object()
        if not current_object:
            LOGGER.warning('Impossible to delete script/s because object is not defined!')
            return

        items = self.selectedItems()
        delete_state = False if not force else True
        if len(items) > 1 and not force:
            delete_state = utils.show_question_dialog(
                'Deleting scripts', 'Are you sure you want to delete selected scripts?')
            if not delete_state or delete_state in (QMessageBox.No, QMessageBox.Cancel):
                return

        items_paths = list()
        for item in items:
            script_name = self._get_item_path_name(item)
            if len(items) == 1 and not force:
                delete_state = utils.show_question_dialog('Deleting {} script?'.format(script_name),
                    'Are you sure you want to delete {} script?'.format(script_name))
                if not delete_state or delete_state in (QMessageBox.No, QMessageBox.Cancel):
                    return

            script_path = current_object.get_code_file(script_name)
            items_paths.append(script_path)
            if delete_state:
                index = self.indexFromItem(item)
                parent = item.parent()
                if parent:
                    parent.removeChild(item)
                else:
                    self.takeTopLevelItem(index.row())

                current_object.delete_code(script_name)
                self.update_scripts_manifest()
            else:
                return

        self.itemRemoved.emit(items_paths)

    def _on_browse_code(self):
        """
        Internal callback function that is triggered when the user selects Browse Code in script item
        """

        current_object = self.object()
        if not current_object:
            LOGGER.warning('Impossible to browse code because object is not defined!')
            return

        items = self.selectedItems()
        if items:
            item = items[0]
            code_name = self._get_item_path_name(item)
            code_path = current_object.get_code_folder(code_name)
            fileio.open_browser(code_path)
        else:
            code_path = current_object.get_code_path()
            fileio.open_browser(code_path)

    def _on_refresh(self):
        """
        Internal callback function that is triggered when the user selects Refresh action
        """

        self.refresh(sync=True)
