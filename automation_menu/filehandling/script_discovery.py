"""
Collect scripts and parse for ScriptInfo-block
and potential breakpoints in the code

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.models.application_state import ApplicationState

import os
import re

from queue import Queue

from automation_menu.models import ScriptInfo, User
from automation_menu.models.enums import OutputStyleTags, ScriptState
from automation_menu.models.scriptmetadata import ScriptMetadata
from automation_menu.utils.docstring_parser import extract_script_metadata
from automation_menu.utils.scriptinfo_block_parser import scriptinfo_block_parser


def _approve_listing( script_info: ScriptInfo, dev_state: bool, current_user: User ) -> int:
    """ Verify that the script is valid to be listed in the menu

    Args:
        script_info (ScriptInfo): Info about the script
        dev_state (bool): In what state is the application run
        current_user (User): User currently running the application

    Returns:
        (int): 0 = valid, 1 = valid, but has active breakpoints (author only), 2 = not valid
    """

    meta = script_info.scriptmeta

    is_author = script_info.is_author( current_user )

    if meta.requires_permission_check():

        required_ad_groups = script_info.get_attr( 'required_ad_groups' ) or []
        allowed_users = script_info.get_attr( 'allowed_users' ) or []

        # Is user in at least one required AD group
        in_required_group = (
            len( required_ad_groups ) == 0
            or any(
                current_user.is_member_of( group_to_check = g )
                for g in required_ad_groups
            )
        )

        # Is user explicitly allowed
        in_allowed_users = (
            len( allowed_users ) == 0
            or current_user.UserId in allowed_users
        )

        # Author or application dev_state ignore script state
        state = meta.state
        state_ok = (
            state in ( ScriptState.TEST, ScriptState.PROD )
            or dev_state
            or is_author
        )

        valid_script_permission = (
            state_ok
            and (
                is_author
                or dev_state
                or in_required_group
                or in_allowed_users
            )
        )

    else:
        valid_script_permission = True

    if not valid_script_permission:

        return 2

    script_info = _check_breakpoints( script_info )
    using_breakpoint = script_info.get_attr( 'using_breakpoint' )

    if using_breakpoint:
        # If script has active breakpoints, only the author may see it
        if is_author:

            return 1  # author sees it, but we can show a warning

        else:

            return 2

    return 0


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
                break

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

    return script_info, warnings


def get_scripts( output_queue: Queue, app_state: ApplicationState, dev_state: bool ) -> list[ ScriptInfo ]:
    """ Get script files and parse for any ScriptInfo

    Args:
        output_queue (Queue): Output queue for info output
        app_state (ApplicationState): General state of application
        dev_state (bool): Is application launched in development state

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
            script_info, parse_warnings = _read_scriptfile( file = filename, directory = script_dir, current_user = app_state.current_user )

            if len( parse_warnings[ 'keys' ] ) > 0:
                raise ValueError( _( 'ScriptInfo contained fields that are not valid, or are misspelled: {names}' ).format( names = ', '.join( parse_warnings[ 'keys' ] ) ) )

            if len( parse_warnings[ 'values' ] ) > 0:
                raise ValueError( _( 'ScriptInfo contained values that are not valid, or are misspelled: {names}' ).format( names = ', '.join( parse_warnings[ 'values' ] ) ) )

            if len( parse_warnings[ 'other' ] ) > 0:
                raise ValueError( _( 'Parsing ScriptInfo generated error for these fields: {names}' ).format( names = ', '.join( parse_warnings[ 'other' ] ) ) )

            approved: int = _approve_listing( script_info = script_info, dev_state = dev_state, current_user = app_state.current_user )

            if approved == 2:
                continue

            else:
                if approved == 1:
                    scriptswithbreakpoint.append( script_info )

                indexed_files.append( script_info )


        except Exception as e:
            output_queue.put( { 'line': _( '{filename} not loaded: {e}' ).format( filename = filename, e = repr( e ) ), 'tag': OutputStyleTags.SYSWARNING } )
            continue

    if len( scriptswithbreakpoint ) > 0:
        line = _( 'Some script have an active breakpoint in the code, handling this has not been implemented, so these will not be available:' )
        output_queue.put( { 'line': '' , 'tag': OutputStyleTags.SYSINFO } )
        output_queue.put( { 'line': line , 'tag': OutputStyleTags.SYSWARNING } )
        output_queue.put( { 'line': ', '.join( [ script.get_attr( 'filename' ) for script in scriptswithbreakpoint ] ) , 'tag': OutputStyleTags.SYSWARNING } )

    return indexed_files


if __name__ == '__main__':
    _read_scriptfile(  )
