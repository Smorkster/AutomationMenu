"""
Manage settings config files

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

import json

from logging import Logger

from automation_menu.models import Settings
from automation_menu.types.rawsettings import RawSettings


def read_settingsfile( settings_file_path: str, debug_logger: Logger ) -> RawSettings:
    """ Read settings from a JSON file.

    Args:
        settings_file_path (str): Path to the settings file.
        debug_logger (Logger): Logger used to report file read errors.

    Returns:
        dict: Collection of settings loaded from the file.

    Raises:
        On reading exception, a default settings object is returned.
    """

    try:
        with open( settings_file_path, mode = 'r', encoding = 'utf-8' ) as f:

            loaded_settings: RawSettings = json.load( f )

            if isinstance( loaded_settings, dict ):

                return loaded_settings

            else:
                return {}

    except Exception as e:
        debug_logger.error( msg = f'Error reading settings file:\n{ e }' )

        return {}


def write_settingsfile( settings: Settings, settings_file_path: str ) -> None:
    """ Write settings to a JSON file.

    Args:
        settings (Settings): Settings to write to the file.
        settings_file_path (str): Path to the file to write.

    Raises:
        FileNotFoundError: If the path is not valid.
    """

    from automation_menu.utils.localization import _

    try:
        with open( settings_file_path, mode = 'w', encoding = 'utf-8' ) as f:
            f.write( settings.to_json() )

    except FileNotFoundError as e:

        raise FileNotFoundError( _( 'Writing settings error; file not found: {file_path}' ).format( file_path = settings_file_path ) ) from e

    except Exception as e:

        raise e
