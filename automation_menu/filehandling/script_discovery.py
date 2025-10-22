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
from automation_menu.models.enums import OutputStyleTags
from automation_menu.models.scriptmetadata import ScriptMetadata
from automation_menu.utils.docstring_parser import extract_script_metadata
from automation_menu.utils.scriptinfo_block_parser import scriptinfo_block_parser


def _check_breakpoints( script_info: ScriptInfo ) -> ScriptInfo:
    """ Check for uncommented breakpoints

    Args:
        lines (list[ str ]): All lines of the scriptfile
        si (ScriptInfo): Script info gathered from the scripts info block

    Returns:
        si (ScriptInfo): ScriptInfo with possible 'UsingBreakpoint'
    """

    with open( script_info.get_attr( 'fullpath' ), 'r', encoding = 'utf-8' ) as f:
        lines = f.readlines()

    for line in lines:
        stripped = line.lstrip()

        if stripped.startswith( 'breakpoint()' ) or ' breakpoint()' in stripped:

            if not stripped.startswith( '#' ):
                script_info.add_attr( 'using_breakpoint', True )

    return script_info


def _read_scriptfile( file: str, directory: str, current_user: User ) -> ScriptInfo:
    """ Call for script information gathering of specified script file

    Args:
        file (str): File name of the script
        directory (str): Directory path containing the script
        current_user (User): AD object for current user
    """

    from automation_menu.utils.localization import _

    path = os.path.join( directory, file )
    script_info = ScriptInfo( filename = file, fullpath = path )

    try:
        with open( path, 'r', encoding = 'utf-8' ) as f:
            f.read( 1 )

    except FileNotFoundError as e:
        return _( 'File not found: {error}' ).format( error = str( e ) )

    except Exception as e:
        return _( 'Could not read file: {error}' ).format( error = str( e ) )

    metadata, warnings = scriptinfo_block_parser( script_info )

    if not metadata:
        try:
            metadata, warnings = extract_script_metadata( script_info )

        except:
            raise ValueError( _( 'No valid ScriptInfo was found in the script' ) )

    try:
        smd = ScriptMetadata( **metadata )
        script_info.scriptmeta = smd

    except Exception as e:
        raise

    if script_info.scriptmeta.requires_permission_check():
        # Permission logic
        requiredadgroups_ok = (
            len( script_info.get_attr( 'required_ad_groups' ) ) == 0 or
            any( current_user.member_of( g ) for g in script_info.get_attr( 'required_ad_groups' ) )
        )
        allowedusers_ok = (
            not script_info.get_attr( 'allowed_users' ) or
            current_user.UserId in script_info.get_attr( 'allowed_users' ) if len( script_info.get_attr( 'allowed_users' ) ) > 0 else True
        )
        is_author_ok = (
            not script_info.get_attr( 'author' ) or
            current_user.AdObject.name.value == script_info.get_attr( 'author' ).replace( ' (', '(' )
        )
        state_ok = (
            script_info.get_attr( 'state' ) and script_info.State in ( 'Test', 'Prod' )
        )

        permission_ok = ( requiredadgroups_ok and allowedusers_ok and state_ok ) or is_author_ok

    else:
        permission_ok = True

    if permission_ok:
        script_info = _check_breakpoints( script_info )

        return script_info, warnings

    else:
        return None


def get_scripts( app_state: ApplicationState ) -> list[ ScriptInfo ]:
    """ Get script files and parse for any ScriptInfo

    Args:
        app_state (ApplicationState): General state of application

    Returns:
        list[ ScriptInfo ]: A list of available scripts
    """

    from automation_menu.utils.localization import _

    # Setup file pattern
    pattern = r'^(?!(__init__)|(GeneralTestFile)).*\.p((y)|(s1))$'
    indexed_files = []
    scriptswithbreakpoint = []
    script_dir = app_state.secrets.get( 'script_dir_path' )

    for i, filename in enumerate(
        sorted(
            [
                f for f in os.listdir( script_dir )
                if os.path.isfile( os.path.join( script_dir, f ) ) and re.match( pattern = pattern , string = f )
            ],
            key = lambda x: x.lower()
        )
    ):
        try:
            script_info, warnings = _read_scriptfile( file = filename, directory = script_dir, current_user = app_state.current_user )

            if len( warnings[ 'keys' ] ) > 0:
                raise ValueError( _( 'ScriptInfo contained fields that are not valid, or are misspelled: {names}' ).format( names = ', '.join( warnings[ 'keys' ] ) ) )

            if len( warnings[ 'values' ] ) > 0:
                raise ValueError( _( 'ScriptInfo contained values that are not valid, or are misspelled: {names}' ).format( names = ', '.join( warnings[ 'values' ] ) ) )

            if len( warnings[ 'other' ] ) > 0:
                raise ValueError( _( 'Parsing ScriptInfo generated error for these fields: {names}' ).format( names = ', '.join( warnings[ 'other' ] ) ) )

            if script_info:
                #if script_info.get_attr( 'using_breakpoint' ) and ( app_state.current_user.AdObject.name.value != script_info.get_attr( 'Author' ).replace( ' (', '(' ) ):
                if script_info.get_attr( 'using_breakpoint' ):
                    scriptswithbreakpoint.append( script_info )

                else:
                    indexed_files.append( script_info )

        except Exception as e:
            app_state.output_queue.put( { 'line': _( '{filename} not loaded: {e}' ).format( filename = filename, e = repr( e ) ), 'tag': OutputStyleTags.SYSWARNING } )
            continue

    if len( scriptswithbreakpoint ) > 0:
        line = _( 'Some script have an active breakpoint in the code, handling this has not been implemented, so these will not be available:' )
        app_state.output_queue.put( { 'line': '' , 'tag': OutputStyleTags.SYSINFO } )
        app_state.output_queue.put( { 'line': line , 'tag': OutputStyleTags.SYSWARNING } )
        app_state.output_queue.put( { 'line': ', '.join( [ script.get_attr( 'filename' ) for script in scriptswithbreakpoint ] ) , 'tag': OutputStyleTags.SYSWARNING } )

    return indexed_files


if __name__ == '__main__':
    _read_scriptfile(  )