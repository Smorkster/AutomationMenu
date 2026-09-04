"""
Helpers to discover, read and store script menu cache

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


import json
import os
from pathlib import Path

from automation_menu.utils.app_path_resolver import app_path


def get_menu_cache_path() -> Path:
    """ Discover if cache have been created

    Returns:
        (Path): Path to the menu cache file.
    """

    return Path( os.path.expanduser( '~' ) ) / 'AppData' / 'Local' / 'AutomationMenu' / 'menu_cache.json'


def read_menu_cache( cache_file: Path ) -> dict:
    """ Read cache file and return as dict

    Args:
        cache_file (Path): Path of file to read

    Returns:
        (dict): Read cache content.

    Raises:
        json.JSONDecodeError on bad/corrupt JSON formatting
    """

    try:
        with open( cache_file, mode = 'r' ) as f:

            return json.load( f )

    except json.JSONDecodeError as e:

        raise

    except FileNotFoundError:

        raise

    except Exception as e:

        raise


def write_menu_cache_file( cache_file_path: Path, cache_content: str ) -> None:
    """ Write script-menu to file

    Args:
        cache_file_path (Path): Path of where to write file
        cache_content (str): Content as JSON formated string
    """

    try:
        if not cache_file_path.parent.exists():
            cache_file_path.parent.mkdir()

        with open( str( cache_file_path ), mode = 'w' ) as f:
            f.write( cache_content )

    except FileNotFoundError as e:

        from automation_menu.utils.localization import _

        raise FileNotFoundError( _( 'Writing script menu cache; file not found: {file_path}' ).format( file_path = cache_file_path ) ) from e

    except Exception as e:

        raise e
