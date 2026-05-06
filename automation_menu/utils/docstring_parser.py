"""
Read script file content for any defined meta data

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

import ast
import re

from re import Match

from automation_menu.models.custom_exceptions import MissingDocstringError
from automation_menu.models.enums import ScriptState, ValidScriptInfoFields
from automation_menu.models.scriptinputparameter import ScriptInputParameter

def _parse_fields( lines: list[ str ] ) -> tuple[ dict, dict ]:
    """ Parse metadata fields from docstring lines.

    Args:
        lines (list[str]): List of docstring lines to parse.

    Returns:
        fields (dict), warnings (dict): Parsed metadata fields and collected parsing warnings.
    """

    from automation_menu.utils.localization import _

    current_field: str = ""
    current_value: str = ''
    fields: dict[ str, str | bool | list[ str ] | ScriptState | list[ ScriptInputParameter ] ] = {}
    parameters: list[ ScriptInputParameter ] = []
    warnings: dict[ str, list[ str ] ] = {
        'keys': [],
        'values': [],
        'other': [],
    }
    field_pattern: re.Pattern = re.compile( r'^:([^:]+):\s*(.*)\s*(\[.*\])*$' )

    for line in lines:
        match: Match | None = field_pattern.match( line.strip() )

        if match:

            current_field = match.group( 1 ).strip()
            current_value = match.group( 2 ).strip() if match.group( 2 ).strip() else ''

            if current_field.startswith( 'param ' ):
                param: ScriptInputParameter = _parse_parameter( field = current_field, value = current_value )
                parameters.append( param )

            else:
                try:
                    ValidScriptInfoFields( current_field.lower() )
                    if current_field.lower() == 'state':
                        fields[ current_field ] = ScriptState[ current_value.upper() ]

                    elif current_field.lower() in ( 'required_ad_groups', 'allowed_users' ):
                        fields[ current_field ] = current_value.split( ';' )

                    else:
                        fields[ current_field ] = current_value if len( current_value ) > 0 else True

                except KeyError:
                    warnings[ 'keys' ].append( current_value )

                except ValueError:
                    warnings[ 'values' ].append( current_field )

                except Exception as e:
                    warnings[ 'other' ].append( current_field )

    fields[ 'script_input_parameters' ] = parameters

    return fields, warnings


def _parse_parameter( field: str, value: str ) -> ScriptInputParameter:
    """ Extract script input parameter information from a docstring field.

    Parse fields like:
    `param name: description`
    `param param_with_default: description (default: value)`
    `param required_param: description (required)`

    Args:
        field (str): Field name from the docstring.
        value (str): Field value from the docstring.

    Returns:
        ScriptInputParameter: Parsed script input parameter definition.
    """

    param_name: str = field[ 6 : ].strip()

    default_match: Match | None = re.search( r'\(default:\s*([^)]+)\)', value, re.IGNORECASE )
    default_value: str = default_match.group( 1 ).strip() if default_match else ''

    required_match: bool = re.search( r'\(required\)', value, re.IGNORECASE ) != None

    options_match: Match | None = re.search( r'\[([^]]+)\]', value, re.IGNORECASE )

    if options_match:
        options_text: str = options_match.group( 1 )
        options_list: list[ str ] = [ option.strip().strip( "'" ) for option in options_text.split( ',' ) ]
        options_list.insert( 0, '' )

    else:
        options_list = []

    # Remove options; [ ... ]
    description: str = re.sub( r'\s*\[[^]]+\]', '', value.strip() ).strip()
    # Remove (default: ...)
    description: str = re.sub( r'\s*\(default:[^)]+\)', '', description ).strip()
    # Remove (required)
    description: str = re.sub( r'\s*\(required\)', '', description ).strip()

    return ScriptInputParameter(
        name = param_name,
        type = 'str',
        required = required_match,
        default = default_value,
        alternatives = options_list,
        description = description
    )


def docstring_parser( raw_docstring: str ) -> tuple[ dict, dict ]:
    """ ParsParse docstring text and extract field definitions.

    Args:
        raw_docstring (str): Full text inside the docstring definition.

    Returns:
        parsed_data (dict), warnings (dict): Parsed description and fields from the docstring, and warnings for invalid or misspelled field names.
    """

    docstring_dict: dict = {}

    if not raw_docstring:

        return docstring_dict, {}

    lines: list[ str ] = raw_docstring.strip().split( '\n' )

    fields_start_idx: int = 0
    for i, line in enumerate( lines ):
        if line.strip().startswith( ':' ):
            fields_start_idx = i

            break

    if fields_start_idx:
        description_lines: list[ str ] = lines[ : fields_start_idx ]
        fields_lines: list[ str ] = lines[ fields_start_idx : ]

    else:
        description_lines: list[ str ] = lines
        fields_lines: list[ str ] = []

    fields, warnings = _parse_fields( fields_lines )

    parsed_data = {
        'description': '\n'.join( description_lines ).strip(),
        **fields
    }

    return parsed_data, warnings


def extract_script_metadata( script_fullpath: str ) -> tuple[ dict, dict ]:
    """ Extract metadata from a script file docstring.

    Args:
        script_fullpath (str): Path to the script file.

    Returns:
        parsed_docstring (dict), warnings (dict): Parsed description and fields from the script docstring, and warnings for invalid or misspelled field names.
    """

    from automation_menu.utils.localization import _

    parsed_docstring: dict = {}
    warnings: dict = {}

    try:
        with open( script_fullpath, 'r', encoding = 'utf-8' ) as f:
            tree: ast.Module = ast.parse( f.read() )

        if ( tree.body
            and isinstance( tree.body[ 0 ], ast.Expr )
            and isinstance( tree.body[ 0 ].value, ast.Constant )
            and isinstance( tree.body[ 0 ].value.value, str ) ):

            parsed_docstring, warnings = docstring_parser( tree.body[ 0 ].value.value )

        else:

            raise MissingDocstringError( _( 'File must have docstring at beginning of file' ) )

    except SyntaxError as e:

        raise SyntaxError( _( 'Cannot parse {file}:\n{err}' ).format( file = script_fullpath, err = e ) )

    return parsed_docstring, warnings
