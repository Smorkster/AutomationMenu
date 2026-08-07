"""
Resolves application root folder path

Returns:
    (Path): Root path to where application is running from.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

import sys

from pathlib import Path


def app_path() -> Path:
    """ Resolve application folder.

    Returns:
        (Path): The folder where the application file is running from.
    """

    if getattr( sys, 'frozen', False ):

        return Path( sys.executable ).parent

    return Path( __file__ ).resolve().parent.parent.parent
