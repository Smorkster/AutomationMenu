"""
Definition of a Settings object, with extended function

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-31
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, TypedDict

from automation_menu.models.sequence import Sequence


class KeePassDict( TypedDict ):
    """ Defined dict for KeePass shortcut definition """

    alt: bool
    ctrl: bool
    shift: bool
    key: str


class Settings:
    def __init__( self, save_callback: Callable, settings_dict: dict | None = None ) -> None:
        """ Class to hold application settings

        Args:
            save_callback (Callable): Callback function for saving to file
            settings_dict (dict | None): Settings read from file
        """

        from automation_menu.utils.localization import _

        default_script_folder = Path( __file__ ).resolve().parent.parent.parent / 'Script'
        self._settings_errors = []
        self._saved_script_folders: list[ str ] = []
        self._script_folders: list[ Path ] = []

        if settings_dict is None:
            self._current_language: str = 'sv_SE'
            self._force_focus_post_execution: bool = False
            self._include_ss_in_error_mail: bool = False
            self._keepass_shortcut: KeePassDict = KeePassDict( { 'ctrl': False, 'alt': False, 'shift': False, 'key': '' } )
            self._minimize_on_running: bool = False
            self._on_top: bool = False
            self._send_mail_on_error: bool = False
            self._saved_sequences: list[ Sequence ] = []


        else:
            self._current_language: str = settings_dict.get( 'current_language', 'sv_SE' )
            self._force_focus_post_execution: bool = settings_dict.get( 'force_focus_post_execution', False )
            self._include_ss_in_error_mail: bool = settings_dict.get( 'include_ss_in_error_mail', False )
            self._keepass_shortcut: KeePassDict = KeePassDict( **settings_dict.get( 'keepass_shortcut', { 'ctrl': False, 'alt': False, 'shift': False, 'key': '' } ) )
            self._minimize_on_running: bool = settings_dict.get( 'minimize_on_running', False )
            self._on_top: bool = settings_dict.get( 'on_top', False )
            self._send_mail_on_error: bool = settings_dict.get( 'send_mail_on_error', False )
            self._saved_script_folders = settings_dict.get( 'script_folders', [] )
            self._saved_sequences: list[ Sequence ] = settings_dict.get( 'saved_sequences', [] )

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
        """ Property function to get 'current_language' """

        return self._current_language


    @current_language.setter
    def current_language( self, value: str ) -> None:
        """ Property setter function to set 'current_language'

        Args:
            value (str): Language tag string to set
        """

        self._current_language = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def force_focus_post_execution( self ) -> bool:
        """ Property function to get 'force_focus_post_execution' """

        return self._force_focus_post_execution


    @force_focus_post_execution.setter
    def force_focus_post_execution( self, value: bool ) -> None:
        """ Property setter function to set 'force_focus_post_execution'

        Args:
            value (bool): Value to set
        """

        self._force_focus_post_execution = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def include_ss_in_error_mail( self ) -> bool:
        """ Property function to get 'on_top' """

        return self._include_ss_in_error_mail


    @include_ss_in_error_mail.setter
    def include_ss_in_error_mail( self, value: bool ) -> None:
        """ Property setter function to set 'include_ss_in_error_mail'

        Args:
            value (bool): Value to set
        """

        self._include_ss_in_error_mail = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def keepass_shortcut( self ) -> KeePassDict:
        """ Property function to get 'keepass_shortcut' """

        return self._keepass_shortcut


    @keepass_shortcut.setter
    def keepass_shortcut( self, value: KeePassDict ) -> None:
        """ Property setter function to set 'keepass_shortcut'

        Args:
            value (KeePassDict): Value to set
        """

        self._keepass_shortcut: KeePassDict = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def minimize_on_running( self ) -> bool:
        """ Property function to get 'on_top' """

        return self._minimize_on_running


    @minimize_on_running.setter
    def minimize_on_running( self, value: bool ) -> None:
        """ Property setter function to set 'minimize_on_running'

        Args:
            value (bool): Value to set
        """

        self._minimize_on_running = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def on_top( self ) -> bool:
        """ Property function to get 'on_top' """

        return self._on_top


    @on_top.setter
    def on_top( self, value: bool ) -> None:
        """ Property setter function to set 'on_top'

        Args:
            value (bool): Value to set
        """

        self._on_top = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def saved_sequences( self ) -> list[ Sequence ]:
        """ Property function to get 'saved_sequences'

        Returns:
            (list[ Sequence ]): List of available sequences
        """

        return self._saved_sequences


    @saved_sequences.setter
    def saved_sequences( self, value: list[ Sequence ] ) -> None:
        """ Property setter function to set 'saved_sequences'

        Args:
            value (list[ Sequence ]): List of sequences to save
        """

        self._saved_sequences = value

        if self._save_callback:
            self._save_callback( self )


    @property
    def send_mail_on_error( self ) -> bool:
        """ Property function to get 'send_mail_on_error' """

        return self._send_mail_on_error


    @send_mail_on_error.setter
    def send_mail_on_error( self, value: bool ) -> None:
        """ Property setter function to set 'send_mail_on_error'

        Args:
            value (bool): Value to set
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
        """ Property setter function to set 'script_folders'

        Args:
            value (list[ Path ]): Value to set
        """

        self._script_folders = value

        if self._save_callback:
            self._save_callback( self )


    def get( self, key: str ) -> bool | str | KeePassDict | list[ Sequence ] | list[ Path ]:
        """ Get attribute with requested name

        Args:
            key (str): Key of dict

        Returns:
            bool | str | KeePassDict | list[ Sequence ] | list[ Path ]: The requested setting
        """

        return getattr( self, f'_{ key }' )


    def get_setting_errors( self ) -> list[ str ]:
        """ Get errors from loading settings

        Returns:
            list[ str ]: List of generated errors
        """

        return self._settings_errors


    def set_keepass_shortcut( self, shortcut_key: str, shortcut_val: bool | str ) -> None:
        """ Set value of 'keepass_shortcut'

        Args:
            shortcut_key (str): KeePassDict key to set
            shortcut_val (bool | str): Value to set for the key
        """

        self._keepass_shortcut[ shortcut_key ] = shortcut_val

        if self._save_callback:
            self._save_callback( self )


    def to_json( self ) -> str:
        """ Convert settings to a JSON-serializable dictionary

        Returns:
            (dict): Json formated dict of setting object
        """

        d: dict[ str, bool | KeePassDict | list | str ] = {
            'current_language': self._current_language,
            'force_focus_post_execution': self._force_focus_post_execution,
            'include_ss_in_error_mail': self._include_ss_in_error_mail,
            'minimize_on_running': self._minimize_on_running,
            'on_top': self._on_top,
            'send_mail_on_error': self._send_mail_on_error,
            'keepass_shortcut': self._keepass_shortcut,
            'script_folders': [],
            'saved_sequences': self._saved_sequences,
        }

        sf = []
        for f in self._script_folders:
            sf.append( str( f ) )
        d[ 'script_folders' ] = sf

        return json.dumps( d, indent = 2 )
