"""
Collect scripts and parse for ScriptInfo-block
and potential breakpoints in the code

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import os
import re

from automation_menu.core.state import ApplicationState
from automation_menu.models import ScriptInfo, User

def _check_breakpoints( lines: list[ str ] , si: ScriptInfo ) -> ScriptInfo:
    """ Check for uncommented breakpoints """

    for line in lines:
        stripped = line.lstrip()
        if stripped.startswith( 'breakpoint()' ) or ' breakpoint()' in stripped:
            if not stripped.startswith( '#' ):
                si.add_attr( 'UsingBreakpoint', True )
    return si

def _extract_scriptinfo( lines: list[ str ] , si: ScriptInfo ) -> ScriptInfo:
    """ Re-read the entire content for block matching """

    from automation_menu.utils.localization import _

    full_text = ''.join( lines )
    match = re.search( r'ScriptInfo\s*(.*?)\s*ScriptInfoEnd', full_text, re.DOTALL )
    if not match:
        si.add_attr( 'NoScriptBlock', True )
        si.add_attr( 'Description', _( 'Script info missing' ) )
        return si

    # Extract key-value pairs inside ScriptInfo block
    for p, t in re.findall( pattern = r"#\s*(\w+)(?:\s*-\s*(.+))?", string = match.group( 1 ) ):
        value = t.replace( ' ', '' )
        if p in ( 'RequiredAdGroups', 'AllowedUsers' ):
            si.add_attr( p, value.split( ';' ) )
        elif t == '':
            si.add_attr( p , True )
        else:
            si.add_attr( p, t )

    return si

def read_scriptfile( file: str, directory: str, current_user: User ) -> ScriptInfo:
    """ Get ScriptInfo from the file """

    from automation_menu.utils.localization import _

    si = ScriptInfo( filename = file, directory = directory )
    path = os.path.join( directory, file )

    try:
        with open( path, encoding = 'utf-8' ) as f:
            lines = f.readlines()
    except FileNotFoundError as e:
        return _( 'File not found: {error}' ).format( error = str( e ) )
    except Exception as e:
        return _( 'Could not read file: {error}' ).format( error = str( e ) )

    si = _check_breakpoints( lines, si )
    si = _extract_scriptinfo( lines, si )

    if not si.get_attr( 'Synopsis' ):
        si.set_attr( 'Synopsis', file )

    # Permission logic
    ad_ok = (
        not hasattr( si, 'RequiredAdGroups' ) or
        any( current_user.member_of( g ) for g in si.RequiredAdGroups )
    )
    user_ok = (
        not hasattr( si, 'AllowedUsers' ) or
        current_user.UserId in si.AllowedUsers
    )
    author_ok = (
        not hasattr( si, 'Author' ) or
        current_user.UserId in si.Author
    )

    return si if ( ad_ok and user_ok ) or author_ok else None

def get_scripts( app_state: ApplicationState ) -> list[ ScriptInfo ]:
    """ Get script files and parse for any ScriptInfo 
    
    Args:
        directory (str): Path to directory containing automation scripts
        current_user (User): User to check permissions for

    Returns:
        list[ScriptInfo]: A list of available scripts
    """

    from automation_menu.utils.localization import _

    # Setup file pattern
    pattern = r'^(?!(__init__)|(GeneralTestFile)).*\.p((y)|(s1))$'
    indexed_files = []

    for i, filename in enumerate(
        sorted(
            [
                f for f in os.listdir( app_state.secrets.get( 'script_dir_path' ) )
                if os.path.isfile( os.path.join( app_state.secrets.get( 'script_dir_path' ), f ) ) and re.match( pattern = pattern , string = f )
            ],
            key = lambda x: x.lower()
        )
    ):
        try:
            si = read_scriptfile( file = filename, directory = app_state.secrets.get( 'script_dir_path' ), current_user = app_state.current_user )
            indexed_files.append( si )
        except Exception as e:
            app_state.output_queue.put( { 'line': _( '{filename} not loaded: {e}' ).format( filename = filename, e = repr( e ) ) } )
            continue
    return indexed_files
