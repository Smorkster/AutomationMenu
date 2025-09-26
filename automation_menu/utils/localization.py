"""
Localization support for the application.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import gettext
import locale
import os
from pathlib import Path

def get_system_locale():
    """ Get the system locale, with fallback to English """

    default_localization = 'sv_SE'
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

def find_locales_directory():
    """ Find the locales directory relative to this file """

    current_file = Path( __file__ )

    # Go up two levels to reach root directory
    project_root = current_file.parent.parent.parent
    locale_dir = project_root / 'locales'

    if not locale_dir.exists():
        print( f'Creating locales directory at: { locale_dir }' )
        locale_dir.mkdir( exist_ok = True )

    return locale_dir

def setup_localization( domain = 'messages', language = None ):
    """
    Set up localization for the application.

    Args:
        domain: The translation domain (usually 'messages')
        language: Force a specific language (e.g., 'sv_SE'), or None for auto-detect

    Returns:
        Translation function to use as _()
    """

    global _

    # Determine which language to use
    if language is None:
        language = get_system_locale()

    # Find locale directory
    locale_dir = find_locales_directory()

    try:
        # Try to load the translation
        translation = gettext.translation(
            domain,
            localedir = str( locale_dir ),
            languages = [ language ],
            fallback = True
        )

        print( f'Loaded localization: { language } from { locale_dir }' )
        _ = translation.gettext

    except Exception as e:
        print( f'Warning: Could not load translation for { language } from { locale_dir }: { e }' )
        print( 'Falling back to English' )

        # Return a function that just returns the original string
        return lambda text: text

_ = setup_localization()

def change_language( language_code: str ):
    """
    Change the application language at runtime.

    Args:
        language_code (str): Language code like 'sv_SE' or 'en_US'

    Returns:
        New translation function
    """

    setup_localization( language = language_code )

def get_available_languages():
    """ Get list of available translation languages
    
    Returns:
        languages (List[str]): A list of available languages
    """

    locale_dir = find_locales_directory()
    languages = []

    try:
        for item in locale_dir.iterdir():
            if item.is_dir() and ( item / 'LC_MESSAGES' / 'messages.mo' ).exists():
                languages.append( item.name )

    except Exception as e:
        print( f'Error scanning for languages: { e }' )

    return sorted( languages )
