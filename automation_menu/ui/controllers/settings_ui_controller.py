"""
Control settings-related UI interactions and persistence.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from pathlib import Path
from tkinter import Event, Tk, filedialog
from tkinter.ttk import Combobox
from typing import Callable

from automation_menu.models.settings import Settings
from automation_menu.ui.types.settings_ui import SettingsUi
from automation_menu.utils.decorators import ui_guard_method


class SettingsUiController:
    """ Control settings UI behavior and updates to stored settings."""

    def __init__( self, settings: Settings, root_window: Tk, change_app_language: Callable ) -> None:
        """ Initialize the settings UI controller.

        Args:
            settings (Settings): Settings model to read from and update.
            root_window (Tk): Root application window.
            change_app_language (Callable): Callback used to change the application language.
        """

        self.settings: Settings = settings
        self.settings_ui: SettingsUi
        self.root_window: Tk = root_window
        self.change_app_language = change_app_language


    def bind_ui( self, settings_ui: SettingsUi ) -> None:
        """ Bind settings UI widget references to the controller.

        Args:
            settings_ui (SettingsUi): Settings UI widget collection.
        """

        self.settings_ui = settings_ui


    def add_script_folder( self ) -> None:
        """ Open a folder dialog and add a new script folder if it is not already listed."""

        directory: str = filedialog.askdirectory()
        path: Path = Path( directory )

        try:
            self.settings.script_folders.index( path )

        except:
            if self.settings_ui.script_folders_list is not None:
                self.settings_ui.script_folders_list.insert( parent = '',
                                                            index = 'end',
                                                            text = str( path ),
                                                            tags = 'exists' )
            self.settings.script_folders.append( Path( directory ) )


    def remove_script_folder( self ) -> None:
        """ Remove the currently selected script folder from the UI and settings."""

        if self.settings_ui.script_folders_list is None:

            return

        tree = self.settings_ui.script_folders_list
        selected_item = tree.focus()
        path = tree.item( selected_item )[ 'text' ]
        tree.delete( selected_item )

        self.settings.script_folders.remove( Path( path ) )


    def set_current_language( self, event: Event ) -> None:
        """ Change the current application language.

        Args:
            event (Event): Event that triggered the language change.
        """

        if not event or not isinstance( event.widget, Combobox ):

            return

        self.settings.current_language = event.widget.get()
        self.change_app_language( new_language = event.widget.get() )


    def set_force_focus_post_execution( self, new_value: bool ) -> None:
        """ Set whether the application should force focus after execution.

        Args:
            new_value (bool): New value to save.
        """

        self.settings.force_focus_post_execution = new_value

        if self.settings_ui.chb_force_focus_post_execution:
            if new_value:
                self.settings_ui.chb_force_focus_post_execution.config( state = 'normal' )

            else:
                self.settings_ui.chb_force_focus_post_execution.config( state = 'disabled' )


    def set_include_ss_in_error_mail( self, new_value: bool ) -> None:
        """ Set whether screenshots should be included in error emails.

        Args:
            new_value (bool): New value to save.
        """

        self.settings.include_ss_in_error_mail = new_value


    def set_minimize_on_running( self, new_value: bool ) -> None:
        """ Set whether the application should minimize while scripts are running.

        Args:
            new_value (bool): New value to save.
        """

        self.settings.minimize_on_running = new_value


    @ui_guard_method( when_message = 'Setting window \'on top\'' )
    def set_on_top( self, new_value: bool ) -> None:
        """ Set whether the main window should stay on top and save the setting.

        Args:
            new_value (bool): New value to set and save.
        """

        self.settings.on_top = new_value
        self.root_window.focus_force()
        self.root_window.attributes( '-topmost', new_value )


    def set_send_mail_on_error( self, new_value: bool ) -> None:
        """ Set whether error emails should be sent.

        Args:
            new_value (bool): New value to save.
        """

        self.settings.send_mail_on_error = new_value

        if self.settings_ui.chb_include_ss_in_error_mail:
            if new_value:
                self.settings_ui.chb_include_ss_in_error_mail.config( state = 'normal' )

            else:
                self.settings_ui.chb_include_ss_in_error_mail.config( state = 'disabled' )
