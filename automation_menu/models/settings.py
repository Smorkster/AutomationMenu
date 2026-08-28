"""
Definition of a Settings object, with extended function

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

import json

from pathlib import Path
from typing import Callable

from automation_menu.types.keepassshortcut import KeePassShortcut
from automation_menu.types.rawsettings import RawSettings
from automation_menu.utils.app_path_resolver import app_path


class Settings:
    """ Store persisted application settings and normalize their defaults. """

    def __init__( self, save_callback: Callable, settings_dict: RawSettings | None = None ) -> None:
        """ Initialize application settings.

        Args:
            save_callback (Callable): Callback function used to persist settings.
            settings_dict (RawSettings | None): Settings loaded from file.
        """

        from automation_menu.utils.localization import _

        default_script_folder = app_path() / 'Script'
        self._settings_errors: list[ str ] = []
        self._saved_script_folders: list[ str ] = []
        self._script_folders: list[ Path ] = []

        self._current_language: str
        self._force_focus_post_execution: bool
        self._include_ss_in_error_mail: bool
        self._keepass_shortcut: KeePassShortcut
        self._minimize_on_running: bool
        self._on_top: bool
        self._send_mail_on_error: bool
        self._saved_sequences: list[ dict ]

        if settings_dict is None:
            self._current_language = 'sv_SE'
            self._force_focus_post_execution  = False
            self._include_ss_in_error_mail = False
            self._keepass_shortcut = KeePassShortcut( { 'ctrl': False, 'alt': False, 'shift': False, 'key': '' } )
            self._minimize_on_running = False
            self._on_top = False
            self._send_mail_on_error = False
            self._saved_sequences = []


        else:
            self._current_language = settings_dict.get( 'current_language', 'sv_SE' )
            self._force_focus_post_execution = settings_dict.get( 'force_focus_post_execution', False )
            self._include_ss_in_error_mail = settings_dict.get( 'include_ss_in_error_mail', False )
            self._keepass_shortcut = KeePassShortcut( **settings_dict.get( 'keepass_shortcut', { 'ctrl': False, 'alt': False, 'shift': False, 'key': '' } ) )
            self._minimize_on_running = settings_dict.get( 'minimize_on_running', False )
            self._on_top = settings_dict.get( 'on_top', False )
            self._send_mail_on_error = settings_dict.get( 'send_mail_on_error', False )
            self._saved_script_folders = settings_dict.get( 'script_folders', [] )
            self._saved_sequences = settings_dict.get( 'saved_sequences', [] )

        if len( self._saved_script_folders ) == 0:
            self._script_folders.append( default_script_folder )

        else:
            try:
                self._script_folders.index( default_script_folder )

            except:
                self._script_folders.append( default_script_folder )

        for f in self._saved_script_folders:
            p = Path( f )

            try:
                self._script_folders.index( p )

            except:
                self._script_folders.append( p )
                if not p.exists():
                    self._settings_errors.append( _( 'Script folder \'{d}\' is not a valid path' ).format( d = f ) )

        self._save_callback: Callable = save_callback


    @property
    def current_language( self ) -> str:
        """ Get the current language setting.

        Returns:
            (str): Current language tag.
        """

        return self._current_language


    @current_language.setter
    def current_language( self, value: str ) -> None:
        """ Set the current language.

        Args:
            value (str): Language tag string to set.
        """

        self._current_language = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def force_focus_post_execution( self ) -> bool:
        """ Get the post-execution focus setting.

        Returns:
            (bool): Whether focus should be forced after script execution.
        """

        return self._force_focus_post_execution


    @force_focus_post_execution.setter
    def force_focus_post_execution( self, value: bool ) -> None:
        """ Set the post-execution focus setting.

        Args:
            value (bool): Value to set.
        """

        self._force_focus_post_execution = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def include_ss_in_error_mail( self ) -> bool:
        """ Get the error mail screenshot setting.

        Returns:
            (bool): Whether screenshots should be included in error emails.
        """

        return self._include_ss_in_error_mail


    @include_ss_in_error_mail.setter
    def include_ss_in_error_mail( self, value: bool ) -> None:
        """ Set the error mail screenshot setting.

        Args:
            value (bool): Value to set.
        """

        self._include_ss_in_error_mail = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def keepass_shortcut( self ) -> KeePassShortcut:
        """ Get the KeePass shortcut configuration.

        Returns:
            (KeePassShortcut): KeePass shortcut settings.
        """

        return self._keepass_shortcut


    @keepass_shortcut.setter
    def keepass_shortcut( self, value: KeePassShortcut ) -> None:
        """ Set the KeePass shortcut configuration.

        Args:
            value (KeePassShortcut): Value to set.
        """

        self._keepass_shortcut: KeePassShortcut = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def minimize_on_running( self ) -> bool:
        """ Get the minimize-on-run setting.

        Returns:
            (bool): Whether the application should minimize while scripts are running.
        """

        return self._minimize_on_running


    @minimize_on_running.setter
    def minimize_on_running( self, value: bool ) -> None:
        """ Set the minimize-on-run setting.

        Args:
            value (bool): Value to set.
        """

        self._minimize_on_running = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def on_top( self ) -> bool:
        """ Get the always-on-top setting.

        Returns:
            (bool): Whether the application window should stay on top.
        """

        return self._on_top


    @on_top.setter
    def on_top( self, value: bool ) -> None:
        """ Set the always-on-top setting.

        Args:
            value (bool): Value to set.
        """

        self._on_top = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def saved_sequences( self ) -> list[ dict ]:
        """ Get the saved sequence definitions.

        Returns:
            (list[ dict ]): List of saved sequence dictionaries.
        """

        return self._saved_sequences


    @saved_sequences.setter
    def saved_sequences( self, value: list[ dict ] ) -> None:
        """ Set the saved sequence definitions.

        Args:
            value (list[ dict ]): List of sequences to save.
        """

        self._saved_sequences = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def send_mail_on_error( self ) -> bool:
        """ Get the error mail setting.

        Returns:
            (bool): Whether error emails should be sent.
        """

        return self._send_mail_on_error


    @send_mail_on_error.setter
    def send_mail_on_error( self, value: bool ) -> None:
        """ Set the error mail setting.

        Args:
            value (bool): Value to set.
        """

        self._send_mail_on_error = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def script_folders( self ) -> list[ Path ]:
        """ Property function to get 'script_folders'

        Returns:
            list[ Path ]: List of saved script folder paths
        """

        return self._script_folders


    @script_folders.setter
    def script_folders( self, value: list[ Path ] ) -> None:
        """ Set the configured script folders.

        Args:
            value (list[ Path ]): Value to set.
        """

        self._script_folders = value

        if self._save_callback:
            self._save_callback( self )


    def get( self, key: str ) -> bool | str | KeePassShortcut | list[ dict ] | list[ Path ]:
        """ Get a setting value by key.

        Args:
            key (str): Name of the setting to retrieve.

        Returns:
            (bool | str | KeePassDict | list[ dict ] | list[ Path ]): Requested setting value.
        """

        return getattr( self, f'_{ key }' )


    def get_setting_errors( self ) -> list[ str ]:
        """ Get errors collected while loading settings.

        Returns:
            (list[ str ]): List of generated settings errors.
        """

        return self._settings_errors


    def set_keepass_shortcut( self, shortcut_key: str, shortcut_val: bool | str ) -> None:
        """ Set a single KeePass shortcut field.

        Args:
            shortcut_key (str): KeePass shortcut key to set.
            shortcut_val (bool | str): Value to assign to the key.
        """

        self._keepass_shortcut[ shortcut_key ] = shortcut_val

        if self._save_callback:
            self._save_callback( self )


    def to_json( self ) -> str:
        """ Serialize settings to a JSON string.

        Returns:
            (str): JSON-formatted string representation of the settings object.
        """

        d: RawSettings = { 'current_language': self._current_language,
                          'force_focus_post_execution': self._force_focus_post_execution,
                          'include_ss_in_error_mail': self._include_ss_in_error_mail,
                          'minimize_on_running': self._minimize_on_running,
                          'on_top': self._on_top,
                          'send_mail_on_error': self._send_mail_on_error,
                          'keepass_shortcut': self._keepass_shortcut,
                          'script_folders': [ str( f ) for f in self._script_folders ],
                          'saved_sequences': self._saved_sequences, }

        return json.dumps( d, indent = 2 )
