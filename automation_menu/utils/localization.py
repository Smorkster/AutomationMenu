"""
Localization support for the application.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

import gettext
import locale

from gettext import NullTranslations
from pathlib import Path
from typing import Callable

from automation_menu.utils.app_path_resolver import app_path


def change_language( language_code: str ) -> None:
    """ Change the application language at runtime.

    Args:
        language_code (str): Language code such as `'sv_SE'` or `'en_US'`.
    """

    setup_localization( language = language_code )


def find_locales_directory() -> Path:
    """ Find the locales directory relative to this file.

    Returns:
        locale_dir (Path): Path to the locales directory.
    """

    current_file: Path = Path( __file__ )

    # Go up two levels to reach root directory
    project_root: Path = app_path()
    locale_dir: Path = project_root / 'locales'

    if not locale_dir.exists():
        print( f'Creating locales directory at: { locale_dir }' )
        locale_dir.mkdir( exist_ok = True )

    return locale_dir


def get_available_languages() -> list[ str ]:
    """ Get the list of available translation languages.

    Returns:
        languages (list[str]): Available language codes.
    """

    locale_dir: Path = find_locales_directory()
    languages: list[ str ] = []

    try:
        for item in locale_dir.iterdir():
            if item.is_dir() and ( item / 'LC_MESSAGES' / 'messages.mo' ).exists():
                languages.append( item.name )

    except Exception as e:
        print( f'Error scanning for languages: { e }' )

    return sorted( languages )


def get_system_locale() -> str:
    """ Get the system locale with fallback to Swedish.

    Returns:
        system_locale (str): Detected system locale, or the fallback locale.
    """

    default_localization: str = 'sv_SE'

    try:
        system_locale, _ = locale.getdefaultlocale()

        if system_locale is None:

            return default_localization

        # Convert locale format if needed (sv_SE.UTF-8 -> sv_SE)
        if '.' in system_locale:
            system_locale = system_locale.split( '.' )[ 0 ]

        return system_locale

    except ( ValueError, TypeError ):

        return default_localization


def setup_localization( domain: str = 'messages', language: str | None = None ) -> Callable:
    """ Set up localization for the application.

    Args:
        domain (str): Translation domain to load.
        language (str | None): Specific language to load, or None to auto-detect.

    Returns:
        _ (Callable): Translation function to use as `_()`.
    """

    global _

    # Determine which language to use
    if language is None:
        language = get_system_locale()

    # Find locale directory
    locale_dir: Path = find_locales_directory()

    try:
        # Try to load the translation
        translation: NullTranslations = gettext.translation( domain,
                                                            localedir = str( locale_dir ),
                                                            languages = [ language ],
                                                            fallback = True )

        print( f'Loaded localization: { language } from { locale_dir }' )
        _ = translation.gettext

    except Exception as e:
        print( f'Warning: Could not load translation for { language } from { locale_dir }: { e }' )
        print( 'Falling back to English' )
        _ = lambda text: text

    # Return a function that just returns the original string
    return _


def translate( text: str ) -> str:
    """ Translate a string.

    Args:
        text (str): Text to translate.

    Returns:
        tt (str): Translated string.
    """

    global _

    t: str = '{}'.format( text )
    tt: str = _( t )

    return tt


_ = lambda text: text
