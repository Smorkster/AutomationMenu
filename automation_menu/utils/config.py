"""
Manage config files

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import json

from automation_menu.models import Settings


def read_secrets_file( file_path: str ) -> dict:
    """ Read secrets

    Args:
        file_path (str): Path to the secrets file

    Returns:
        (dict): Dict containing secret data
    """

    with open( file_path, mode = 'r', encoding = 'utf-8' ) as f:
        return json.load( f )


def read_settingsfile( settings_file_path: str ) -> dict:
    """ Read settings from a JSON file

    Args:
        settings_file_path (str): Path to settings file

    Returns:
        (dict): Collection of settings from file

    Raises:
        On reading exception, a default settings object is returned
    """

    try:
        with open( settings_file_path, mode = 'r', encoding = 'utf-8' ) as f:
            return json.load( f )

    except Exception as e:
        return { 'on_top' : False, 'minimize_on_running' : False }


def write_settingsfile( settings: Settings, settings_file_path: str ) -> None:
    """ Write settings to JSON file
    
    Args:
        settings (Settings): Settings to write to file
        settingsfile_path (str): Path to file to write

    Raises:
        FileNotFoundError when the path is not valid
    """

    from automation_menu.utils.localization import _

    try:
        with open( settings_file_path, mode = 'w', encoding = 'utf-8' ) as f:
            f.write( settings.to_json() )

    except FileNotFoundError as e:
        raise FileNotFoundError( _( 'Writing settings error; file not found: {file_path}' ).format( file_path = settings_file_path ) ) from e

    except Exception as e:
        raise e
