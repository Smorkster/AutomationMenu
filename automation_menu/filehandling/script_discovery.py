"""
Collect scripts and parse for ScriptInfo-block
and potential breakpoints in the code

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from __future__ import annotations

import os
import re

from chardet import DetectionDict, UniversalDetector
from operator import attrgetter
from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING

from automation_menu.utils.source_encoding_detector import get_python_source_encoding

if TYPE_CHECKING:
    from automation_menu.models.application_state import ApplicationState

from automation_menu.models import ScriptInfo, User
from automation_menu.models.custom_exceptions import ScriptInfoError
from automation_menu.models.enums import ApplicationRunState, OutputStyleTags, ScriptState
from automation_menu.models.scriptmetadata import ScriptMetadata
from automation_menu.utils.docstring_parser import extract_script_metadata
from automation_menu.utils.scriptinfo_block_parser import scriptinfo_block_parser


def _approve_listing( script_info: ScriptInfo, app_run_state: ApplicationRunState, current_user: User, content: str ) -> int:
    """ Verify that the script is valid to be listed in the menu

    Args:
        script_info (ScriptInfo): Info about the script
        app_run_state (ApplicationRunState): In what state is the application run
        current_user (User): User currently running the application
        content (str): Content of scriptfile

    Returns:
        (int): 0 = valid, 1 = valid, but has active breakpoints (author only), 2 = not valid
    """

    meta: ScriptMetadata = script_info.scriptmeta

    is_author: bool = script_info.is_author( current_user )

    if meta.requires_permission_check():

        required_ad_groups: list[ str ] = script_info.get_attr( 'required_ad_groups' ) or []
        allowed_users: list[ str ] = script_info.get_attr( 'allowed_users' ) or []

        # Is user in at least one required AD group
        in_required_group: bool = (
            len( required_ad_groups ) == 0
            or any( current_user.is_member_of( group_to_check = g )
                   for g in required_ad_groups )
        )

        # Is user explicitly allowed
        in_allowed_users: bool = (
            ( len( allowed_users ) == 0 ) or
            ( current_user.UserId in allowed_users )
        )

        # Author or application run state 'dev' ignore script state
        state: ScriptState = meta.state
        state_ok: bool = (
            ( state in ( ScriptState.TEST, ScriptState.PROD ) ) or
            ( app_run_state == ApplicationRunState.DEV ) or
            is_author
        )

        valid_script_permission: bool = (
            state_ok and
            (
                is_author or
                ( app_run_state == ApplicationRunState.DEV ) or
                ( in_required_group and in_allowed_users )
            )
        )

    else:
        valid_script_permission: bool = True

    if not valid_script_permission:

        return 2

    script_info.using_breakpoint = _check_for_breakpoints( content = content )

    if script_info.using_breakpoint:
        # If script has active breakpoints, only the author may see it
        if is_author:

            return 1  # author sees it, but a warning is shown

        else:

            return 2

    return 0


def _check_for_breakpoints( content: str ) -> bool:
    """ Check for uncommented breakpoints

    Args:
        content (str): Content of script file

    Returns:
        (bool): True if script has any active breakpoints
    """

    for line in content.split( '\n' ):
        stripped_line: str = line.lstrip()

        if stripped_line.startswith( 'breakpoint()' ) or ' breakpoint()' in stripped_line:

            if not stripped_line.startswith( '#' ):

                return True

    return False


def _read_scriptfile( file: os.DirEntry, current_user: User, app_run_state: ApplicationRunState ) -> tuple[ ScriptInfo, dict, int ]:
    """ Call for script information gathering of specified script file

    Args:
        file (os.DirEntry): File name of the script
        current_user (User): AD object for current user
        app_run_state (ApplicationRunState): State the application is running in

    Returns:
        (ScriptInfo, dict, int): Collected script info, warnings of invalid parameters
            and if script is approved for listing
    """

    from automation_menu.utils.localization import _

    encoding_header: str
    encoding_detected: DetectionDict | None = None
    encoding: str

    try:
        encoding_detector = UniversalDetector()
        with open( file.path, 'rb' ) as f:
            for line in f:
                encoding_detector.feed( line )

                if encoding_detector.done:

                    break

        encoding_detected = encoding_detector.close()

        encoding_header = get_python_source_encoding( script_path = file.path, detected_encoding = encoding_detected[ 'encoding' ] or 'utf-8' )
        encoding = ( encoding_header or encoding_detected[ 'encoding' ] if encoding_detected else '' ) or 'utf-8'

        if 'utf-8' not in encoding:

            raise UnicodeError()

        with open( file.path, 'r', encoding = encoding ) as f:
            content = f.read()

    except FileNotFoundError as e:

        raise FileNotFoundError( _( 'File not found' ) )

    except ( UnicodeError, UnicodeDecodeError ):

        raise UnicodeError( """Script file is not saved using encoding UTF-8, and no source encoding is declared.
Python requires UTF-8 by default for .py files.

Fix by either:
1. Saving the file as UTF-8
2. Adding an encoding header, for example:
   # -*- coding: utf-8 -*-""" )

    except Exception as e:

        raise Exception( _( 'Could not read file: {error}' ).format( error = str( e ) ) )

    metadata: dict

    if re.search( r'ScriptInfoEnd *((\"\"\")|(#>))', content ):
        metadata, warnings = scriptinfo_block_parser( full_text = content )

    else:
        try:
            metadata, warnings = extract_script_metadata( script_fullpath = file.path, encoding = encoding )

        except Exception as e:

            raise ScriptInfoError( _( f'No valid ScriptInfo was found in the script: { e }' ) ) from e

    try:
        smd: ScriptMetadata = ScriptMetadata( **metadata )
        script_info: ScriptInfo = ScriptInfo( filename = file.name, fullpath = file.path, scriptmeta = smd )

    except Exception as e:

        raise

    approved: int = _approve_listing( script_info = script_info, app_run_state = app_run_state, current_user = current_user, content = content )

    return script_info, warnings, approved


def get_scripts( output_queue: Queue, app_state: ApplicationState, app_run_state: ApplicationRunState ) -> list[ ScriptInfo ]:
    """ Get script files and parse for any ScriptInfo

    Args:
        output_queue (Queue): Output queue for info output
        app_state (ApplicationState): General state of application
        app_run_state (ApplicationRunState): Is application launched in development state

    Returns:
        list[ ScriptInfo ]: A list of available scripts
    """

    from automation_menu.utils.localization import _

    # Setup file pattern
    pattern: re.Pattern = re.compile( r'^(?!(__init__)|(GeneralTestFile)).*\.p((y)|(s1))$' )
    application_test_files: list[ ScriptInfo ] = []
    indexed_files: list[ ScriptInfo ] = []
    scripts_with_breakpoint: list[ ScriptInfo ] = []
    script_dirs: list[ Path ] = app_state.settings.script_folders

    for dir in script_dirs:

        if not dir.exists():

            continue

        for i, file in enumerate( sorted(
                [ f for f in os.scandir( dir )
                 if f.is_file() and pattern.match( string = f.name ) ],
                key = lambda x: x.name.lower() ) ):
            if file.name.startswith( 'AMTest_' ) and app_run_state == ApplicationRunState.PROD:

                continue

            try:
                script_info, parse_warnings, approved = _read_scriptfile( file = file,
                                                                         current_user = app_state.current_user,
                                                                         app_run_state = app_run_state )

                # Guard against format changes that has not been implemented
                for key in ( 'keys', 'values', 'other' ):
                    if key not in parse_warnings:

                        raise ValueError( _( '\'parse_warnings\' missing key {key}' ).format( key = key ) )

                if len( parse_warnings[ 'keys' ] ) > 0:

                    raise ValueError( _( 'ScriptInfo contained fields that are not valid, or are misspelled: {names}' ).format( names = ', '.join( parse_warnings[ 'keys' ] ) ) )

                if len( parse_warnings[ 'values' ] ) > 0:

                    raise ValueError( _( 'ScriptInfo contained values that are not valid, or are misspelled: {names}' ).format( names = ', '.join( parse_warnings[ 'values' ] ) ) )

                if len( parse_warnings[ 'other' ] ) > 0:

                    raise ValueError( _( 'Parsing ScriptInfo generated error for these fields: {names}' ).format( names = ', '.join( parse_warnings[ 'other' ] ) ) )

                if approved == 2:

                    continue

                else:
                    if approved == 1:
                        scripts_with_breakpoint.append( script_info )

                    if file.name.startswith( 'AMTest_' ):
                        application_test_files.append( script_info )

                    else:
                        indexed_files.append( script_info )

            except ScriptInfoError as e:
                output_queue.put( { 'line': _( '{filename} not loaded: {e}' ).format( filename = file.name, e = repr( e ) ),
                                'tag': OutputStyleTags.SYSERROR } )

            except ValueError as e:
                output_queue.put( { 'line': _( '{filename} not loaded: {e}' ).format( filename = file.name, e = repr( e ) ),
                                'tag': OutputStyleTags.SYSWARNING } )

            except Exception as e:
                output_queue.put( { 'line': _( '{filename} not loaded: {e}' ).format( filename = file.name, e = repr( e ) ),
                                'tag': OutputStyleTags.SYSERROR } )

                continue

    if len( scripts_with_breakpoint ) > 0:
        line: str = _( 'Some scripts have at least one active breakpoint in the code. Handling this has not been fully tested yet:' )
        output_queue.put( { 'line': '' ,
                           'tag': OutputStyleTags.SYSINFO
                           } )
        output_queue.put( { 'line': line,
                           'tag': OutputStyleTags.SYSWARNING
                           } )
        output_queue.put( { 'line': ', '.join( [ script.get_attr( 'filename' ) for script in scripts_with_breakpoint ] ),
                           'tag': OutputStyleTags.SYSWARNING
                           } )

    return sorted( application_test_files, key = attrgetter( 'scriptmeta.synopsis' ) ) + sorted( indexed_files, key = attrgetter( 'scriptmeta.synopsis' ) )
