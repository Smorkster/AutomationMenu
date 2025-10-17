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
from automation_menu.models.script import ScriptInputParameter, ScriptState
from automation_menu.utils.docstring_parser import extract_script_metadata
from automation_menu.utils.scriptinfo_block_parser import scriptinfo_block_parser


def _add_scriptinfo_meta( si: ScriptInfo, metadata: dict ) -> ScriptInfo:
    """ """

    def _parse_list( list_name ):
        """ """
        list_values = metadata.get( list_name, '' )

        if isinstance( list_values, list ):
            return list_values

        else:
            if not list_values:
                return []

            return [ item.strip() for item in re.split( r'[,;]', list_values ) if item.strip() ]

    from automation_menu.utils.localization import _

    si.add_attr( 'Synopsis', metadata.get( 'synopsis', si.filename ) )
    si.add_attr( 'Author', metadata.get( 'author', _( 'Unknown' ) ) )
    si.add_attr( 'Description', metadata.get( 'description', '' ) )

    state_value: str = metadata.get( 'state', 'DEV' )

    try:
        state = ScriptState[ state_value.upper() ]

    except KeyError:
        state = ScriptState.DEV

    si.add_attr( 'State', state )

    si.add_attr( 'RequiredAdGroups', _parse_list( 'required_ad_groups' ) )
    si.add_attr( 'AllowedUsers', _parse_list( 'allowed_users' ) )

    script_input_parameters = _parse_parameters( metadata )

    if len( script_input_parameters ) > 0:
        si.add_attr( 'InputParameters', script_input_parameters )

    return si


def _check_breakpoints( si: ScriptInfo ) -> ScriptInfo:
    """ Check for uncommented breakpoints

    Args:
        lines (list[ str ]): All lines of the scriptfile
        si (ScriptInfo): Script info gathered from the scripts info block

    Returns:
        si (ScriptInfo): ScriptInfo with possible 'UsingBreakpoint'
    """

    with open( si.fullpath, 'r', encoding = 'utf-8' ) as f:
        lines = f.readlines()

    for line in lines:
        stripped = line.lstrip()

        if stripped.startswith( 'breakpoint()' ) or ' breakpoint()' in stripped:

            if not stripped.startswith( '#' ):
                si.add_attr( 'UsingBreakpoint', True )

    return si


def _parse_parameters( metadata: dict ) -> list[ ScriptInputParameter ]:
    """ Extract script input parameters

    Looks for fields like:
    :param name: description
    :param param_with_default: description (default: value)
    :param required_param: description (required)
    """

    parameters = []

    for key, value in metadata.items():
        if key.startswith( 'param ' ):
            param_name = key[ 6 : ].strip()

            default_match = re.search( r'\(default:\s*([^)]+)\)', value, re.IGNORECASE )
            default_value = default_match.group( 1 ).strip() if default_match else None

            required_match = re.search( r'\(required\)', value, re.IGNORECASE ) != None

            description = re.sub( r'\s*\(default:[^)]+\)', '', re.sub( r'\s*\(required\)', '', value.strip() ).strip() )

            parameters.append( ScriptInputParameter(
                name = param_name,
                type = 'str',
                required = required_match,
                default = default_value,
                description = description
            ) )

    return parameters


def _read_scriptfile( file: str, directory: str, current_user: User ) -> ScriptInfo:
    """ Call for script information gathering of specified script file

    Args:
        file (str): File name of the script
        directory (str): Directory path containing the script
        current_user (User): AD object for current user
    """

    from automation_menu.utils.localization import _

    si = ScriptInfo( filename = file, directory = directory )
    path = os.path.join( directory, file )

    try:
        with open( path, 'r', encoding = 'utf-8' ) as f:
            f.read( 1 )

    except FileNotFoundError as e:
        return _( 'File not found: {error}' ).format( error = str( e ) )

    except Exception as e:
        return _( 'Could not read file: {error}' ).format( error = str( e ) )

    metadata = scriptinfo_block_parser( si )

    if not metadata:
        try:
            metadata = extract_script_metadata( si )

        except:
            raise

    si = _add_scriptinfo_meta( si, metadata )

    # Permission logic
    requiredadgroups_ok = (
        len( si.get_attr( 'RequiredAdGroups' ) ) == 0 or
        any( current_user.member_of( g ) for g in si.RequiredAdGroups )
    )
    allowedusers_ok = (
        not hasattr( si, 'AllowedUsers' ) or
        current_user.UserId in si.AllowedUsers if len( si.AllowedUsers ) > 0 else True
    )
    is_author_ok = (
        not hasattr( si, 'Author' ) or
        current_user.AdObject.name.value == si.get_attr( 'Author' ).replace( ' (', '(' )
    )
    state_ok = (
        hasattr( si, 'State' ) and si.State in ( 'Test', 'Prod' )
    )

    if ( requiredadgroups_ok and allowedusers_ok and state_ok ) or is_author_ok:
        si = _check_breakpoints( si )

        return si

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
            si = _read_scriptfile( file = filename, directory = app_state.secrets.get( 'script_dir_path' ), current_user = app_state.current_user )

            if si:
                #if si.get_attr( 'UsingBreakpoint' ) and ( app_state.current_user.AdObject.name.value != si.get_attr( 'Author' ).replace( ' (', '(' ) ):
                if si.get_attr( 'UsingBreakpoint' ):
                    scriptswithbreakpoint.append( si )
                else:
                    indexed_files.append( si )

        except Exception as e:
            app_state.output_queue.put( { 'line': _( '{filename} not loaded: {e}' ).format( filename = filename, e = repr( e ) ), 'tag': 'suite_sysinfo' } )
            continue

    if len( scriptswithbreakpoint ) > 0:
        line = _( 'Some script have an active breakpoint in the code, handling this has not been implemented, so these will not be available:' )
        app_state.output_queue.put( { 'line': line , 'tag': 'suite_sysinfo' } )
        app_state.output_queue.put( { 'line': ', '.join( [ script.get_attr( 'filename' ) for script in scriptswithbreakpoint ] ) , 'tag': 'suite_sysinfo' } )

    return indexed_files


if __name__ == '__main__':
    _read_scriptfile(  )