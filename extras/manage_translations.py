"""
Translation management script for the automation menu.
Usage:
    python extras/manage_translations.py extract
    python extras/manage_translations.py init sv_SE
    python extras/manage_translations.py update
    python extras/manage_translations.py compile

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import subprocess
import sys
from pathlib import Path


def get_project_root() -> str:
    """ Get the project root directory (AutomationMenu folder)
    
    Returns:
        (str): Path to root directory
    """

    return Path( __file__ ).parent.parent


def run_command( cmd: str, cwd: str = None ) -> None:
    """ Run a command and handle errors

    Args:
        cmd (str): Command to run
        cwd (str): Directory to set as working directory
    """

    if cwd is None:
        cwd = get_project_root()

    print( f'Running: { ' '.join( cmd ) } (in { cwd })' )
    try:
        result = subprocess.run( cmd, check = True, capture_output = True, text = True, cwd = cwd )
        if result.stdout:
            print( result.stdout )
        return True

    except subprocess.CalledProcessError as e:
        print( f'Error: { e }' )
        if e.stderr:
            print( f'Error output: { e.stderr }' )
        return False


def extract_strings() -> list[ str ]:
    """ Extract translatable strings from source code

    Returns:
        (list[ str ]): List of info strings of files that got extracted
    """

    project_root = get_project_root()

    cmd = [
        'pybabel', 'extract',
        '-F', 'babel.cfg',
        '-k', '_',
        '-o', 'locales/messages.pot',
        '.'
    ]

    return run_command( cmd, cwd = project_root )


def init_language( language ) -> str:
    """ Initialize a new language

    Args:
        language (str): Language code to initialize

    Returns:
        (str): Info which locale was initialized
    """

    project_root = get_project_root()

    cmd = [
        'pybabel', 'init',
        '-i', 'locales/messages.pot',
        '-d', 'locales',
        '-l', language
    ]

    return run_command( cmd, cwd = project_root )


def update_translations() -> list[ str ]:
    """Update existing translations with new strings

    Returns:
        (list[ str ]): Info what catalogs got updated
    """

    project_root = get_project_root()

    cmd = [
        'pybabel', 'update',
        '-i', 'locales/messages.pot',
        '-d', 'locales'
    ]

    import os

    vsc_path = os.path.join( os.getenv( 'LOCALAPPDATA' ), 'Programs\\Microsoft VS Code\\Code.exe' )

    for root, dirs, files in os.walk( os.path.join( project_root , 'locales' ) ):

        for file in files:

            if file.endswith( '.po' ):
                p = os.path.join( root, file )
                subprocess.run( [ vsc_path, p ] )

    return run_command( cmd, cwd = project_root )


def compile_translations():
    """ Compile .po files to .mo files

    Returns:
        (list[ str ]): Info which catalogs got compiled
    """

    project_root = get_project_root()

    cmd = [
        'pybabel', 'compile',
        '-d', 'locales'
    ]

    return run_command( cmd, cwd = project_root )


def check_structure() -> None:
    """ Check if the project structure is correct """

    project_root = get_project_root()

    # Check for babel.cfg
    babel_cfg = project_root / 'babel.cfg'
    if not babel_cfg.exists():
        print( f'Warning: babel.cfg not found at { babel_cfg }' )
        print( 'You may need to create it in the AutomationMenu folder' )

    # Check for locales directory
    locales_dir = project_root / 'locales'
    if not locales_dir.exists():
        print( f'Warning: locales directory not found at { locales_dir }' )
        print( 'Creating locales directory...' )
        locales_dir.mkdir( exist_ok = True )


    print( f'Project root: { project_root }' )
    print( f'Babel config: { babel_cfg } ({ 'exists' if babel_cfg.exists() else 'missing' })' )
    print( f'Locales dir: { locales_dir } ({ 'exists' if locales_dir.exists() else 'missing' })' )


def main():
    """ Main entry point """
    if len( sys.argv ) < 2:
        print( 'Usage:' )
        print( '  extract     - Extract strings from source code' )
        print( '  init <lang> - Initialize new language (e.g., ''en_EN'')' )
        print( '  update      - Update existing translations' )
        print( '  compile     - Compile translations' )
        print( '  check       - Check project structure' )
        print( '  workflow      Display a list of which functions to do in order' )
        sys.exit( 1 )

    command = sys.argv[ 1 ]

    if command == 'check':
        check_structure()
    elif command == 'extract':
        if extract_strings():
            print( '✅ Strings extracted successfully' )
        else:
            print( '❌ Failed to extract strings' )
    elif command == 'init':
        if len( sys.argv ) < 3:
            print( 'Please specify language code (e.g., ''en_EN'')' )
            sys.exit( 1 )
        if init_language( sys.argv[ 2 ] ):
            print( f'✅ Language { sys.argv[ 2 ] } initialized successfully' )
        else:
            print( f'❌ Failed to initialize language { sys.argv[ 2 ] }' )
    elif command == 'update':
        if update_translations():
            print( '✅ Translations updated successfully' )
        else:
            print( '❌ Failed to update translations' )
    elif command == 'compile':
        if compile_translations():
            print( '✅ Translations compiled successfully' )
        else:
            print( '❌ Failed to compile translations' )
    elif command == 'workflow':
        print( 'check\nextract / update\ninit\nEdit po-files\ncompile' )
    else:
        print( f'Unknown command: { command }' )
        sys.exit( 1 )

if __name__ == "__main__":
    main()
