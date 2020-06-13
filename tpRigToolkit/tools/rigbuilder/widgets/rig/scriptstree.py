#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module that contains widget to show scripts tree
"""

from __future__ import print_function, division, absolute_import

import logging

from Qt.QtCore import *
from Qt.QtWidgets import *
from Qt.QtGui import *

import tpDcc as tp
from tpDcc.core import scripts
from tpDcc.libs.python import osplatform, timers, fileio, path as path_utils
from tpDcc.libs.qt.core import qtutils

from tpRigToolkit.tools.rigbuilder.core import utils
from tpRigToolkit.tools.rigbuilder.items import script
from tpRigToolkit.tools.rigbuilder.widgets.base import basetree

LOGGER = logging.getLogger('tpRigToolkit')


class ScriptTree(basetree.BaseTree, object):

    HEADER_LABELS = ['Scripts']
    ITEM_WIDGET = script.ScriptItem
    NEW_ITEM_NAME = 'new_script'

    itemSignalsConnected = False
    itemAdded = Signal(object)
    scriptOpened = Signal(object, bool, bool)
    scriptOpenedInExternal = Signal()

    def __init__(self, settings=None, parent=None):

        self.python_icon = tp.ResourcesMgr().icon('python')
        self.python_expand_icon = tp.ResourcesMgr().icon('python_expand')
        self.python_no_expand_icon = tp.ResourcesMgr().icon('python_no_expand')

        super(ScriptTree, self).__init__(settings=settings, parent=parent)

        self.setDragDropMode(self.InternalMove)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setAcceptDrops(False)
        self.setDragEnabled(False)
        self.setDropIndicatorShown(False)
        self.setAutoScroll(True)
        self.setAlternatingRowColors(True)

        # self.setVerticalScrollMode(self.ScrollPerPixel)
        # self.setTabKeyNavigation(True)
        # self.setSelectionBehavior(self.SelectItems)

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

    def dropEvent(self, event):

        is_dropped = self._is_item_dropped(event, strict=True)
        if not self._hierarchy:
            is_dropped = False

        event.accept()

        if is_dropped:
            self._add_drop(event)
        else:
            self._insert_drop(event)

        self.update_scripts_manifest()

    def refresh(self, sync=False, scripts_and_states=[]):
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

    def _create_item(self, filename, state=False):
        """
        Internal function that creates a new script tree item
        :param filename: str
        :param state: bool
        :return: script.ScriptItem
        """

        item = self.ITEM_WIDGET()
        item.set_text(filename)
        self._setup_item(item, state)

        return item

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

        skip_emit = kwargs.get('skip_emit', False)
        if not skip_emit:
            self.itemAdded.emit(item)

        return item

    def _add_items(self, files, item=None):
        """
        Overrides base BuildTree _add_items function
        Internal function used to add new scripts file to the given script item
        :param files: list(str)
        :param item: ScriptItem
        """

        scripts, states = files
        script_count = len(scripts)
        found_false = False

        order_scripts = dict()
        order_of_scripts = list()
        ordered_scripts = list()
        parents = dict()
        built_parents = dict()

        for i in range(script_count):
            script_full = scripts[i]
            script_name = script_full.split('.')[0]
            slash_count = script_name.count('/')
            if slash_count not in order_scripts:
                order_scripts[slash_count] = list()
                order_of_scripts.append(slash_count)
            parents[script_name] = None
            order_scripts[slash_count].append([script_name, script_full, states[i]])

        for count in order_of_scripts:
            ordered_scripts += order_scripts[count]

        for i in range(script_count):
            script_name, script_full, state = ordered_scripts[i]
            basename = path_utils.get_basename(script_full)
            dir_name = path_utils.get_dirname(script_full)
            current_parent = False
            if dir_name in built_parents:
                current_parent = built_parents[dir_name]
            item = self._add_item('...temp...', state, parent=current_parent, update_manifest=False, skip_emit=True)
            if script_name in parents:
                built_parents[script_name] = item
            if current_parent:
                current_parent.addChild(item)
                item.set_text(basename)
            if not dir_name:
                self.addTopLevelItem(item)
                item.set_text(basename)
            if not state:
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

        current_object = self.object()
        if not current_object:
            LOGGER.debug('Impossible to get script files because object is not defined!')
            return

        if scripts is None:
            scripts = list()
        if states is None:
            states = list()

        if not scripts:
            scripts, states = current_object.get_scripts_manifest()
        if not scripts:
            LOGGER.debug('Current object has no scripts!')
            return

        code_folders = current_object.get_code_folders()
        found_scripts = list()
        found_states = list()

        for i in range(len(scripts)):
            script_name = fileio.remove_extension(scripts[i])
            if script_name not in code_folders:
                continue
            script_path = current_object.get_code_file(script_name)
            if not script_path or not path_utils.is_file(script_path):
                continue

            found_scripts.append(scripts[i])
            found_states.append(states[i])

        return [found_scripts, found_states]

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

        if not self.itemSignalsConnected and hasattr(item, 'scriptSignals'):
            item.scriptSignals.createPythonCode.connect(self._on_create_python_code)
            item.scriptSignals.runCode.connect(self._on_run_current_item)
            item.scriptSignals.runCodeGroup.connect(self._on_run_current_group)
            item.scriptSignals.renameCode.connect(self._on_rename_current_item)
            item.scriptSignals.duplicateCode.connect(self._on_duplicate_current_item)
            item.scriptSignals.deleteCode.connect(self._on_delete_current_item)
            item.scriptSignals.setStartPoint.connect(self._on_set_start_point)
            item.scriptSignals.cancelStartPoint.connect(self._on_cancel_start_point)
            item.scriptSignals.setBreakPoint.connect(self._on_set_break_point)
            item.scriptSignals.cancelBreakPoint.connect(self._on_cancel_break_point)
            item.scriptSignals.browseCode.connect(self._on_browse_code)

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
        after_name = self._handle_item_reparent(old_name, new_name, item)
        basename = path_utils.get_basename(after_name)
        script_extension = item.get_object().SCRIPT_EXTENSION
        if not script_extension.startswith('.'):
            script_extension = '.{}'.format(script_extension)
        item.set_text(basename + script_extension)
        self.itemRenamed.emit(old_name, after_name)

    def _create_actions(self, context_menu):
        """
        Overrides base BuildTree _create_new_actions function
        Internal function that creates actions for the creation of new items
        :param context_menu: QMenu
        :return: list(QAction)
        """

        python_icon = tp.ResourcesMgr().icon('python')
        import_icon = tp.ResourcesMgr().icon('import')
        browse_icon = tp.ResourcesMgr().icon('open')
        refresh_icon = tp.ResourcesMgr().icon('refresh')

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

    def _handle_item_reparent(self, old_name, new_name, item):
        """
        Overrides base _handle_item_reparent function
        Internal function that handles the parenting of script tree script items
        :param old_name: str
        :param new_name: str
        :param item: str
        :return: str
        """

        if old_name == new_name:
            return old_name

        current_object = self.object()
        if not current_object:
            LOGGER.warning('Impossible to handle item reparent because object is not defined!')
            return

        current_object.set_directory(self._directory)

        new_name = current_object.move_code(old_name, new_name)

        return new_name

    # ================================================================================================
    # ======================== BASE
    # ================================================================================================

    def create_python_code(self):
        """
        Creates a new Python code file in current project directory
        """

        current_object = self.object()
        if not current_object:
            LOGGER.warning('Impossible to create new python code because build object is not defined!')
            return

        parent_item = None
        code_name = 'code'
        items = self.selectedItems()
        if items:
            parent_item = items[0]
            code_path = self._get_item_path_name(parent_item, keep_extension=False)
            if code_path:
                code_name = '{}/{}'.format(code_path, current_object.CODE_FOLDER)

        code_path = current_object.create_code(code_name, scripts.ScriptTypes.Python, unique_name=True)
        if not code_path:
            LOGGER.error('Impossible to create new code!')
            return

        code_name = path_utils.get_basename(code_path)
        item = self._add_item(file_name=code_name, state=False, parent=parent_item)
        item.setCheckState(0, Qt.Checked)
        # self._reparent_item(code_name, item, parent_item)
        self.scrollToItem(item)
        self.setItemSelected(item, True)
        self.setCurrentItem(item)

        self.update_scripts_manifest()
        self._activate_rename()

        # self.itemCreated.emit(item)

    def create_data_import(self, data_name=None, data_extension=None):
        """
        Creates a new data import file in current project directory
        :param data_name: str
        :param data_extension: str
        """

        raise NotImplementedError('Not implemented functionality yet!')

        # current_object = self.object()
        # if not current_object:
        #     LOGGER.warning('Impossible to create new data import code because object is not defined!')
        #     return
        # current_object.set_directory(self._directory)
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
        # code_path = current_object.create_code(
        #     name='import_{}'.format(data_name), data_type=scripts.ScriptTypes.Python,
        #     unique_name=True, import_data=import_data)
        # basename = path_utils.get_basename(code_path)
        # item = self._add_item(basename, False)
        # item.setCheckState(0, Qt.Checked)
        # self._reparent_item('import_{}'.format(data_name), item, parent_item)
        # self.scrollToItem(item)
        # self.setItemSelected(item, True)
        # self.setCurrentItem(item)

    def run_current_item(self, external_code_library=None, group_only=False):
        """
        Executes current selected item in the tree
        :param external_code_library: str
        :param group_only: bool
        """

        current_object = self.object()
        if not current_object:
            LOGGER.warning('Impossible to run script because object is not defined!')
            return

        osplatform.set_env_var('RIGBUILDER_RUN', True)
        osplatform.set_env_var('RIGBULIDER_STOP', False)

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
            current_object.set_external_code_library(external_code_library)

        last_name = items[-1].text(0)
        last_path = self.get_item_path(items[-1])
        if last_path:
            last_name = path_utils.join_path(last_path, last_name)

        set_end_states = False
        for i in range(len(scripts)):
            if osplatform.get_env_var('RIGBUILDER_RUN') == 'True':
                if osplatform.get_env_var('RIGBULIDER_STOP') == 'True':
                    break
                if set_end_states:
                    item = self._get_item_by_name(scripts[i])
                    if item:
                        item.set_state(-1)
                for item in items:
                    script_name = item.text(0)
                    script_path = self.get_item_path(item)
                    if script_path:
                        script_name = path_utils.join_path(script_path, script_name)
                    if script_name == scripts[i]:
                        run_children = False
                        if group_only:
                            run_children = True
                        self._run_item(item, current_object, run_children)
                        if group_only:
                            break
                        if script_name == last_name:
                            set_end_states = True

        osplatform.set_env_var('RIGBUILDER_RUN', False)
        osplatform.set_env_var('RIGBULIDER_STOP', False)

        minutes, seconds = watch.stop()
        if minutes:
            LOGGER.info('Rig Scripts run in {} minutes and {} seconds'.format(minutes, seconds))
        else:
            LOGGER.info('Rig Scripts run in {} seconds'.format(seconds))

    def rename_current_item(self):
        """
        Renames current selected item from the the tree
        """

        self._activate_rename()

    def duplicate_current_item(self):
        """
        Duplicates current selected item from the tree
        """

        current_object = self.object()
        if not current_object:
            LOGGER.warning('Impossible to duplicate script because object is not defined!')
            return
        current_object.set_directory(self._directory)

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

    def delete_current_item(self, force=False):
        """
        Removes current item selected from the tree
        :param force: bool
        """

        current_object = self.object()
        if not current_object:
            LOGGER.warning('Impossible to delete script/s because object is not defined!')
            return
        current_object.set_directory(self._directory)

        items = self.selectedItems()
        delete_state = False if not force else True
        if len(items) > 1 and not force:
            delete_state = utils.show_question_dialog(
                'Deleting scripts', 'Are you sure you want to delete selected scripts?')
            if not delete_state or delete_state in (QMessageBox.No, QMessageBox.Cancel):
                return

        for item in items:
            script_name = self._get_item_path_name(item)
            if len(items) == 1 and not force:
                delete_state = utils.show_question_dialog('Deleting {} script?'.format(script_name),
                    'Are you sure you want to delete {} script?'.format(script_name))
                if not delete_state or delete_state in (QMessageBox.No, QMessageBox.Cancel):
                    return

            script_path = current_object.get_code_file(script_name)
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

            self.itemRemoved.emit(script_path)

    def browse_code(self):
        """
        Opens current system explorer window where code folder is located
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

    # ================================================================================================
    # ======================== MANIFEST
    # ================================================================================================

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

    def _run_item(self, item, object=None, run_children=False):
        """
        Internal function that launches given ScripItem with given rig
        :param item: ScriptItem
        :param object: object
        :param run_children: bool
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
        log = osplatform.get_env_var('RIGBUILDER_LAST_TEMP_LOG')
        item.set_log(log)

        if status == 'Success':
            item.set_state(1)
        else:
            item.set_state(0)

        if log.find('Warning') > -1 or log.find('WARNING') > -1 or log.find('warning') > -1:
            item.set_state(2)

        item.setBackground(0, orig_background)

        if run_children:
            self._run_children(item, object, recursive=True)

    def _run_children(self, item, object, recursive=True):
        """
        Internal function that executes children scripts of a given item. It can be recursively or not
        :param item: ScriptItem
        :param object: object
        :param recursive: bool
        """

        child_count = item.childCount()
        if not child_count:
            return

        item.setExpanded(True)

        if child_count:
            for i in range(child_count):
                child_item = item.child(i)
                child_item.set_state(-1)
            for i in range(child_count):
                child_item = item.child(i)
                self._run_item(child_item, object, run_children=recursive)

    def _add_drop(self, event):
        """
        Internal callback function that is called when an item is added to another one after a drop action
        :param event: QDropEvent
        """

        remove_items = list()
        moved_items = list()

        entered_item = self._get_entered_item(event)
        from_list = event.source()

        for item in from_list.selectedItems():
            parent = item.parent()
            if not parent:
                parent = self.invisibleRootItem()
            remove_items.append([item, parent])
            children = item.takeChildren()
            name = item.get_text()
            state = item.get_state()
            entered_item.setExpanded(True)
            new_item = self._create_item(name, state)
            for child in children:
                child.set_state(-1)
                new_item.addChild(child)
            entered_item.addChild(new_item)
            entered_item.setExpanded(True)
            old_name = self._get_item_path_name(item)
            new_name = self._get_item_path_name(new_item)
            moved_items.append([old_name, new_name, new_item])

            self._update_item(item)

        for item in remove_items:
            item[1].removeChild(item[0])

        for moved_item in moved_items:
            old_name, new_name, item = moved_item
            self._move_item(old_name, new_name, item)

    def _insert_drop(self, event):

        remove_items = list()
        moved_items = list()
        insert_index = 0

        from_list = event.source()
        entered_item = self._get_entered_item(event)
        entered_parent = entered_item.parent()
        entered_item.text(0)
        if entered_parent:
            entered_parent.text(0)

        added_items = list()

        for item in from_list.selectedItems():
            children = item.takeChildren()
            filename = item.get_text()
            state = item.get_state()
            new_item = self._create_item(filename, state)
            for child in children:
                new_item.addChild(child)
                child.set_state(-1)
            parent = item.parent()
            if not parent:
                parent = self.invisibleRootItem()
            remove_items.append([item, parent])
            added_items.append(new_item)

            insert_row = self.indexFromItem(entered_item, column=0).row()
            if self._drop_indicator_position == self.BelowItem:
                insert_row += 1
                insert_row = insert_row + insert_index

            if entered_parent:
                entered_parent.insertChild(insert_row, new_item)
            else:
                if insert_row == -1:
                    insert_row = self.topLevelItemCount()
                if not entered_item:
                    self.insertTopLevelItem(insert_row, new_item)
                else:
                    if entered_item.text(0) == parent.text(0):
                        entered_item.insertChild(entered_item.childCount() - 1, new_item)
                    else:
                        self.insertTopLevelItem(insert_row, new_item)

            insert_index += 1

            entered_parent_name = None
            if entered_parent:
                entered_parent_name = entered_parent.text(0)
            if entered_parent_name != parent.text(0):
                old_name = self._get_item_path_name(item)
                new_name = self._get_item_path_name(new_item)
                moved_items.append([old_name, new_name, new_item])

        for item in remove_items:
            item[1].removeChild(item[0])

        for moved_item in moved_items:
            old_name, new_name, item = moved_item
            self._move_item(old_name, new_name, item)

        for new_item in added_items:
            self._update_item(new_item)

    def _update_item(self, item):
        """
        Internal function that can be used to update internal data of the item after add/insert operations
        Can be override in sub classes
        :param item:
        :return:
        """

        pass

    # ================================================================================================
    # ======================== CALLBACKS
    # ================================================================================================

    def _on_create_python_code(self):
        """
        Internal callback function that is triggered when New Python Code action is selected
        Creates a new Python Script
        """

        self.create_python_code()


    def _on_create_data_import(self, data_name=None, data_extension=None):
        """
        Internal callback function that is triggered when New Import Data action is selected
        :param data_name: str
        :param data_extension: str
        """

        self.create_data_import(data_name=data_name, data_extension=data_extension)

    def _on_run_current_item(self, external_code_library=None, group_only=False):
        """
        Internal function that executes current item
        :param external_code_library: str
        :param group_only: bool
        """

        self.run_current_item(external_code_library=external_code_library, group_only=group_only)

    def _on_run_current_group(self):
        """
        Internal callback function that is triggered when the Run Group action is clicked
        """

        self.run_current_item(group_only=True)

    def _on_rename_current_item(self):
        """
        Internal callback function that is triggered when the Rename action is clicked
        :return:
        """

        self.rename_current_item()

    def _on_duplicate_current_item(self):
        """
        Internal callback function that is triggered when the Duplicate Item action is clicked
        """

        self.duplicate_current_item()

    def _on_delete_current_item(self, force=False):
        """
        Internal callback funtion that is triggerd when delete item action is clicked
        """

        self.delete_current_item(force=force)

    def _on_set_start_point(self, item=None):
        """
        Internal callback function that is called when Set Start Point action is clicked
        :param item:
        """

        self.set_start_point(item=item)

    def _on_cancel_start_point(self):
        """
        Internal callback function that is called when Cancel Start Point action is clicked
        """

        self.cancel_start_point()

    def _on_set_break_point(self, item=None):
        """
        Internal callback function that is called when Set Break Point is clicked
        :param item:
        """

        self.set_break_point(item=item)

    def _on_cancel_break_point(self):
        """
        Internal callback function that is called when Cancel Break Point is called
        """

        self.cancel_break_point()

    def _on_browse_code(self):
        """
        Internal callback function that is triggered when the user selects Browse Code in script item
        """

        self.browse_code()

    def _on_refresh(self):
        """
        Internal callback function that is triggered when the user selects Refresh action
        """

        self.refresh(sync=True)
