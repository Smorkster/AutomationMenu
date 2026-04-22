
"""
Manage application settings loading, UI setup, and persistence.

This module connects the stored settings file, the in-memory ``Settings``
model, and the Tkinter settings tab. It loads saved settings, creates the
settings tab and its widgets, persists changes back to disk, and reports
settings validation issues to the shared output queue.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT

"""

from __future__ import annotations
from pathlib import Path
from tkinter import filedialog
from tkinter.ttk import Frame, Notebook
from typing import TYPE_CHECKING, Callable

from automation_menu.filehandling.settings_handler import read_settingsfile, write_settingsfile
from automation_menu.models.enums import OutputStyleTags
from automation_menu.models.settings import Settings
from automation_menu.models.settings_ui_dict import SettingsUiDict
from automation_menu.ui.settings_tab import build_settings, get_settings_tab


if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext


class SettingsManager:
    """ Coordinate settings loading, UI construction, and persistence """

    def __init__( self, app_context: ApplicationContext ) -> None:
        """ Initialize the settings manager.

        Args:
            app_context (ApplicationContext): Shared application context used
                for logging, output, and access to the main window.
        """

        self._app_context: ApplicationContext = app_context

        self._settings_widgets: SettingsUiDict
        self._settings: Settings
        self._settings_file_path: Path


    def _add_script_folder( self ) -> None:
        """ Open folder dialog to add new script folder

        If folder is already listed, do nothing
        """

        directory: str = filedialog.askdirectory()
        path: Path = Path( directory )

        try:
            self._settings.script_folders.index( path )

        except:
            self._settings_widgets[ 'script_folders_list' ].insert( parent = '',
                                                                   index = 'end',
                                                                   text = str( path )
                                                                   )
            self._settings.script_folders.append( Path( directory ) )


    def _remove_script_folder( self ) -> None:
        """ Remove the selected folder """

        tree = self._settings_widgets[ 'script_folders_list' ]
        selected_item = tree.focus()
        path = tree.item( selected_item )[ 'text' ]
        tree.delete( selected_item )

        self._settings.script_folders.remove( Path( path ) )


    def build_tab_content( self ) -> SettingsUiDict:
        """ Build the settings tab widgets for the current settings.

        Returns:
            SettingsUiDict: Dictionary of created settings-related widgets.
        """

        callbacks = {
            'add_script_folder': self._add_script_folder,
            'remove_script_folder': self._remove_script_folder
        }
        self._settings_widgets = build_settings( tab = self._tab, settings = self._settings, main_self = self._app_context.main_window, bind_callbacks = callbacks )

        return self._settings_widgets


    def create_tab( self, parent_tab: Notebook, translate_store_callback: Callable ) -> Frame:
        """ Create the settings tab container.

        Args:
            parent_tab (Notebook): Notebook that will contain the settings tab.
            translate_store_callback (Callable): Callback used to register
                translatable text for later language updates.

        Returns:
            Frame: The created settings tab frame.
        """

        self._tab = get_settings_tab( tabcontrol = parent_tab, translate_store_callback = translate_store_callback )

        return self._tab


    def read_saved_settings( self, settings_file_path: str ) -> Settings:
        """ Load settings from disk and prepare them for use.

        The loaded data is wrapped in a ``Settings`` instance with
        ``save_settings`` registered as its save callback. Any settings-load
        issues collected during initialization are forwarded to the shared
        output queue as system errors.

        Args:
            settings_file_path (str): Path to the settings file.

        Returns:
            Settings: The initialized settings object.
        """

        saved = read_settingsfile( settings_file_path = settings_file_path, debug_logger = self._app_context.debug_logger )
        self._settings = Settings( settings_dict = saved, save_callback = self.save_settings )
        self._settings_file_path = Path( settings_file_path )

        setting_errors = self._settings.get_setting_errors()

        if len( setting_errors ) > 0:
            from automation_menu.utils.localization import _
            for e in setting_errors:
                self._app_context.OutputQueue.put( {
                    'line': e,
                    'tag': OutputStyleTags.SYSERROR
                } )

        return self._settings


    def save_settings( self, obj: Settings ) -> None:
        """ Persist the current settings object to disk.

        Args:
            obj (Settings): Settings object to write to the configured file.
        """

        write_settingsfile( settings = obj, settings_file_path = str( self._settings_file_path ) )

