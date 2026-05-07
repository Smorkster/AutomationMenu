"""
Definition of a Secret object, its data is parsed from
a specialized file

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

import os

from pathlib import Path
from typing import Any, TypedDict


class Secrets:
    class secret_dict( TypedDict, total = False ):
        error_ss_prefix: str
        ldap_search_base: str
        ldap_server: str
        main_error_mail: str
        mainwindowtitle: str
        settings_file_path: str
        smtprelay: str
        domain_name: str

    _secret_dict: secret_dict = {}


    def __init__( self, new_dict: dict ) -> None:
        """ An enum like class to hold data customizable from a config file

        Args:
            new_dict (dict): Saved data dictionary read from file
        """

        Secrets._secret_dict[ 'error_ss_prefix' ] = new_dict.get( 'error_ss_prefix', 'AutoError' )
        Secrets._secret_dict[ 'ldap_search_base' ] = new_dict.get( 'ldap_search_base', '' )
        Secrets._secret_dict[ 'ldap_server' ] = new_dict.get( 'ldap_server', '' )
        Secrets._secret_dict[ 'main_error_mail' ] = new_dict.get( 'main_error_mail', '' )
        Secrets._secret_dict[ 'mainwindowtitle' ] = new_dict.get( 'mainwindowtitle', 'Automation menu' )
        Secrets._secret_dict[ 'settings_file_path' ] = os.path.expanduser( os.path.join( '~', new_dict.get( 'settings_file_name', 'AutomationMenu_Settings_File_Name.json' ) ) )
        Secrets._secret_dict[ 'smtprelay' ] = new_dict[ 'smtprelay' ]
        Secrets._secret_dict[ 'domain_name' ] = new_dict[ 'domain_name' ]


    def __getitem__( self, v: str ) -> Any:
        """ Return the specified secret value

        Args:
            v (str): Name of secret to return
        """

        return Secrets._secret_dict[ v ]


    @staticmethod
    def get( key: str ) -> bool | Path | str:
        """ Get dict value

        Args:
            key (str): Key of dict
        """

        return Secrets._secret_dict.get( key, "" )
