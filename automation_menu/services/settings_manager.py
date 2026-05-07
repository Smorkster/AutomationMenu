
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
from tkinter.ttk import Frame, Notebook
from typing import TYPE_CHECKING

from automation_menu.types.rawsettings import RawSettings

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext

from automation_menu.filehandling.settings_handler import read_settingsfile, write_settingsfile
from automation_menu.models.enums import OutputStyleTags
from automation_menu.models.settings import Settings
from automation_menu.ui.controllers.settings_ui_controller import SettingsUiController
from automation_menu.ui.tabs.settings_tab import build_settings, create_settings_tab
from automation_menu.ui.types.settings_ui import SettingsUi


class SettingsManager:
    """ Coordinate settings loading, UI construction, and persistence."""

    def __init__( self, app_context: ApplicationContext, settings_file_path: str ) -> None:
        """ Initialize the settings manager.

        Args:
            app_context (ApplicationContext): Shared application context
                used for logging, output, and access to the main window.
            settings_file_path (str): Path to the settings file.
        """

        self._app_context: ApplicationContext = app_context

        self.read_saved_settings( settings_file_path = settings_file_path )

        self.settings: Settings
        self.settings_ui: SettingsUi
        self._settings_file_path: Path
        self.settings_ui_controller: SettingsUiController


    def build_tab_content( self ) -> SettingsUi:
        """ Build the settings tab widgets for the current settings.

        Returns:
            (SettingsUi): Created settings UI widget collection.
        """

        self.settings_ui_controller = SettingsUiController( settings = self.settings,
                                                           root_window = self._app_context.main_window.root,
                                                           change_app_language = self._app_context.LanguageManager.change_app_language )
        self.settings_ui = build_settings( tab = self._tab,
                                          settings = self.settings,
                                          settings_ui_controller = self.settings_ui_controller,
                                          add_translatable = self._app_context.LanguageManager.add_translatable_widget )
        self.settings_ui_controller.bind_ui( settings_ui = self.settings_ui )

        return self.settings_ui


    def create_tab( self, parent_tab: Notebook ) -> Frame:
        """ Create the settings tab container.

        Args:
            parent_tab (Notebook): Notebook that will contain the settings tab.

        Returns:
            (Frame): Created settings tab frame.
        """

        self._tab = create_settings_tab( tab_control = parent_tab,
                                        translate_store_callback = self._app_context.LanguageManager.add_translatable_widget )

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
            (Settings): The initialized settings object.
        """

        saved: RawSettings = read_settingsfile( settings_file_path = settings_file_path,
                                  debug_logger = self._app_context.debug_logger )
        self.settings = Settings( settings_dict = saved,
                                 save_callback = self.save_settings )
        self._settings_file_path = Path( settings_file_path )

        setting_errors = self.settings.get_setting_errors()

        if len( setting_errors ) > 0:
            from automation_menu.utils.localization import _
            for e in setting_errors:
                self._app_context.OutputQueue.put( {
                    'line': e,
                    'tag': OutputStyleTags.SYSERROR
                } )

        return self.settings


    def save_settings( self, obj: Settings ) -> None:
        """ Persist a settings object to disk.

        Args:
            obj (Settings): Settings object to write to the configured file.
        """

        write_settingsfile( settings = obj,
                           settings_file_path = str( self._settings_file_path ) )
