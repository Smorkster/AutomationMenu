"""
Definition of a Secret object, its data is parsed from
a specialized file

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-31
"""

import os
from pathlib import Path


class Secrets:
    _secret_dict: dict[ str, bool | Path | str ] = {}

    def __init__( self, new_dict: dict | None ) -> None:
        """ An enum like class to hold data customizable from a config file

        Args:
            new_dict (dict | None): Saved data dictionary read from file
        """

        Secrets._secret_dict[ 'error_ss_prefix' ] = new_dict.get( 'error_ss_prefix', 'AutoError' )
        Secrets._secret_dict[ 'ldap_search_base' ] = new_dict.get( 'ldap_search_base' )
        Secrets._secret_dict[ 'ldap_server' ] = new_dict[ 'ldap_server' ]
        Secrets._secret_dict[ 'main_error_mail' ] = new_dict[ 'main_error_mail' ]
        Secrets._secret_dict[ 'mainwindowtitle' ] = new_dict.get( 'mainwindowtitle', 'Automation menu' )
        Secrets._secret_dict[ 'script_dir_path' ] = Path( __file__ ).resolve().parent.parent.parent / "Script"
        Secrets._secret_dict[ 'settings_file_path' ] = os.path.expanduser( os.path.join( '~', new_dict.get( 'settings_file_name', 'AutomationMenu_Settings_File_Name.json' ) ) )
        Secrets._secret_dict[ 'smtprelay' ] = new_dict[ 'smtprelay' ]
        Secrets._secret_dict[ 'domain_name' ] = new_dict[ 'domain_name' ]


    @staticmethod
    def get( key: str ) -> str:
        """ Get dict value

        Args:
            key (str): Key of dict
        """

        return Secrets._secret_dict.get( key, "" )
