"""
Object models used in the application

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import json
from pathlib import Path
from typing import Callable
import ldap3
import os
import re

import ldap3.abstract
import ldap3.abstract.entry

class User:
    """ Class to hold user information from Active Directory """
    def __init__( self, ad_object: ldap3.abstract.entry.Entry = None ):
        """ Initialize User with an Active Directory object """

        self.UserId:str = os.getenv( key = 'USERNAME' ,default = 'DefaultUser' )
        self.AdObject: ldap3.abstract.entry.Entry = ad_object

    def member_of( self, group_to_check: str ) -> bool:
        """ Check if the user is a member of a specific group """

        for g in self.AdObject.memberof:
            if re.search( group_to_check , g ):
                return True

        return False

class ScriptInfo:
    """ Class to hold information about a script """
    def __init__( self, filename: str, directory: str ):
        """ Initialize ScriptInfo with filename and directory """

        self.filename = filename
        self.fullpath = directory.joinpath( filename )

    def add_attr( self, attr_name: str, attr_val: any ) -> None:
        """ Add an attribute to the ScriptInfo object """

        setattr( self, attr_name, attr_val )

    def set_attr( self, attr_name: str, attr_val:any, append: bool = False ) -> None:
        """ Append a value to an existing attribute or create it if it doesn't exist """

        if ( not hasattr( self, attr_name ) ):
            self.add_attr( attr_name, attr_val )
        elif append:
            setattr( self, attr_name, getattr( self, attr_name ) + attr_val )
        else:
            setattr( self, attr_name, attr_val )

    def get_attr( self, attr_name: str ) -> any:
        """ Get the value of an attribute if it exists, otherwise return None """

        if hasattr( self, attr_name ):
            return getattr( self, attr_name )
        else:
            None

class Settings:
    """ Class to hold application settings """
    def __init__( self, settings_dict: dict, save_callback: Callable = None ):
        self._save_callback = save_callback
        self._on_top = settings_dict.get( 'on_top', False )
        self._minimize_on_running = settings_dict.get( 'minimize_on_running', False )
        self._send_mail_on_error = settings_dict.get( 'send_mail_on_error', False )
        self._include_ss_in_error_mail = settings_dict.get( 'include_ss_in_error_mail', False )
        self._current_language = settings_dict.get( 'current_language', 'sv_SE' )

    def to_json( self ) -> dict:
        """ Convert settings to a JSON-serializable dictionary """

        d = { k.lstrip( '_' ): v
             for k, v in self.__dict__.items()
             if not callable( self.__dict__[ k ] ) }
        return json.dumps( d, indent = 2 )

    @property
    def current_language( self ):
        """ Property function to get 'current_language' """

        return self.get( 'current_language' )

    @current_language.setter
    def current_language( self, value: bool ):
        """ Property setter function to set 'current_language' """

        self._current_language = value
        if self._save_callback:
            self._save_callback( self )

    @property
    def send_mail_on_error( self ):
        """ Property function to get 'send_mail_on_error'
        """

        return self.get( 'send_mail_on_error' )

    @send_mail_on_error.setter
    def send_mail_on_error( self, value: bool ):
        """ Property setter function to set 'send_mail_on_error'

        Args:
            value (bool): Value to set
        """

        self._send_mail_on_error = value
        if self._save_callback:
            self._save_callback( self )

    @property
    def include_ss_in_error_mail( self ):
        """ Property function to get 'on_top'
        """

        return self.get( 'include_ss_in_error_mail' )

    @include_ss_in_error_mail.setter
    def include_ss_in_error_mail( self, value: bool ):
        """ Property setter function to set 'include_ss_in_error_mail'

        Args:
            value (bool): Value to set
        """

        self._include_ss_in_error_mail = value
        if self._save_callback:
            self._save_callback( self )

    @property
    def minimize_on_running( self ):
        """ Property function to get 'on_top' """

        return self.get( 'minimize_on_running' )

    @minimize_on_running.setter
    def minimize_on_running( self, value: bool ):
        """ Property setter function to set 'minimize_on_running' """

        self._minimize_on_running = value
        if self._save_callback:
            self._save_callback( self )

    @property
    def on_top( self ):
        """ Property function to get 'on_top' """

        return self.get( 'on_top' )

    @on_top.setter
    def on_top( self, value: bool ):
        """ Property setter function to set 'on_top' """

        self._on_top = value
        if self._save_callback:
            self._save_callback( self )

    def get( self, key: str ) -> any:
        """ Get attribute with corrected name

        Args:
            key (str): Key of dict
        """

        return getattr( self, f'_{ key }' )

class Secrets:
    secret_dict = {}

    def __init__( self, new_dict: dict ):
        Secrets.secret_dict[ 'error_ss_prefix' ] = new_dict[ 'error_ss_prefix' ]
        Secrets.secret_dict[ 'ldap_search_base' ] = new_dict[ 'ldap_search_base' ]
        Secrets.secret_dict[ 'ldap_server' ] = new_dict[ 'ldap_server' ]
        Secrets.secret_dict[ 'main_error_mail' ] = new_dict[ 'main_error_mail' ]
        Secrets.secret_dict[ 'mainwindowtitle' ] = new_dict[ 'mainwindowtitle' ]
        Secrets.secret_dict[ 'script_dir_path' ] = Path( __file__ ).resolve().parent.parent / "Script"
        Secrets.secret_dict[ 'settings_file_path' ] = os.path.expanduser( os.path.join( '~', new_dict[ 'settings_file_name' ] ) )
        Secrets.secret_dict[ 'smtprelay' ] = new_dict[ 'smtprelay' ]
        Secrets.secret_dict[ 'domain_name' ] = new_dict[ 'domain_name' ]

    @staticmethod
    def get( key: str ) -> str:
        """ Get dict value
        
        Args:
            key (str): Key of dict
        """

        return Secrets.secret_dict.get( key, "" )