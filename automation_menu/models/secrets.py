import os
from pathlib import Path


class Secrets:
    secret_dict = {}

    def __init__( self, new_dict: dict ):
        """ An enum like class to hold data customizable from a config file """

        Secrets.secret_dict[ 'error_ss_prefix' ] = new_dict[ 'error_ss_prefix' ]
        Secrets.secret_dict[ 'ldap_search_base' ] = new_dict[ 'ldap_search_base' ]
        Secrets.secret_dict[ 'ldap_server' ] = new_dict[ 'ldap_server' ]
        Secrets.secret_dict[ 'main_error_mail' ] = new_dict[ 'main_error_mail' ]
        Secrets.secret_dict[ 'mainwindowtitle' ] = new_dict[ 'mainwindowtitle' ]
        Secrets.secret_dict[ 'script_dir_path' ] = Path( __file__ ).resolve().parent.parent.parent / "Script"
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
