"""
Read script file content for any defined meta data

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

import ast
import re

from re import IGNORECASE, Match

from automation_menu.models.custom_exceptions import MissingDocstringError
from automation_menu.models.enums import ScriptState, ValidScriptInfoFields
from automation_menu.models.scriptinputparameter import ScriptInputParameter

# Available, approved parameter flags
_param_flags: list[ str ] = [ 'required' ]
_param_approved_field_names: list[ str ] = [ 'default', 'description', 'options', 'type' ]

# Regex to check for approved parameters
_param_re_check_if_new = re.compile( rf'^\s*({ '|'.join( _param_approved_field_names ) })\s*=', IGNORECASE )
_param_re_iter_splitter = re.compile( rf':\s*(?P<flag>{'|'.join( _param_flags )})|(?P<key>{'|'.join( _param_approved_field_names )})\s*=\s*(?P<value>[^:]+)' )


def _parse_fields( lines: list[ str ] ) -> tuple[ dict, dict ]:
    """ Parse metadata fields from docstring lines.

    Args:
        lines (list[str]): List of docstring lines to parse.

    Returns:
        fields (dict), warnings (dict): Parsed metadata fields and collected parsing warnings.
    """

    from automation_menu.utils.localization import _

    current_field: str = ''
    current_value: str = ''
    fields: dict[ str, str | bool | list[ str ] | ScriptState | list[ ScriptInputParameter ] ] = {}
    parameters: list[ ScriptInputParameter ] = []
    warnings: dict[ str, list[ str ] ] = { 'keys': [],
                                          'values': [],
                                          'other': [], }
    field_pattern: re.Pattern = re.compile( r'^:([^:]+):\s*(.*)\s*(\[.*\])*$' )

    for line in lines:
        match: Match | None = field_pattern.match( line.strip() )

        if match:
            current_field = match.group( 1 ).strip()
            current_value = match.group( 2 ).strip() if match.group( 2 ).strip() else ''

            if current_field.startswith( 'param ' ):
                param: ScriptInputParameter = _parse_parameter( field = current_field, value = current_value )

                if param.type == 'bool' and param.default not in [ 'True', 'False' ]:
                    warnings[ 'values' ].append( _( '{n} has invalid boolean default value: {v}' ).format( n = param.name, v = param.default ) )
                    param.default = 'False'

                elif param.type == 'int':
                    try:
                        int( param.default )

                    except ( TypeError, ValueError ):
                        warnings[ 'values' ].append( _( '{n} has invalid integer default value: {v}' ).format( n = param.name, v = param.default ) )
                        param.default = '0'

                elif param.type == 'float':
                    try:
                        float( param.default )

                    except ( TypeError, ValueError ):
                        warnings[ 'values' ].append( _( '{n} has invalid float default value: {v}' ).format( n = param.name, v = param.default ) )
                        param.default = '0.0'

                parameters.append( param )

            else:
                try:
                    ValidScriptInfoFields( current_field.lower() )

                except ValueError:
                    warnings[ 'keys' ].append( current_field )

                    continue

                if current_field.lower() == 'state':
                    try:
                        fields[ current_field ] = ScriptState[ current_value.upper() ]

                    except KeyError:
                        warnings[ 'values' ].append( current_value )

                        continue

                elif current_field.lower() in ( 'required_ad_groups', 'allowed_users' ):
                    fields[ current_field ] = current_value.split( ';' )

                else:
                    fields[ current_field ] = current_value if len( current_value ) > 0 else True

    fields[ 'script_input_parameters' ] = parameters

    return fields, warnings


def _parse_parameter( field: str, value: str ) -> ScriptInputParameter:
    """ Extract script input parameter information from a docstring field.

    Args:
        field (str): Field name from the docstring.
        value (str): Field value from the docstring.

    Returns:
        ScriptInputParameter: Parsed script input parameter definition.
    """

    param_name: str = field[ 6 : ].strip()

    is_new_format: bool = _param_re_check_if_new.match( value ) is not None

    if is_new_format:

        return _parse_parameter_new_format( param_spec = value, param_name = param_name )

    else:

        return _parse_parameter_old_format( value = value, param_name = param_name )


def _parse_parameter_new_format( param_spec: str, param_name: str ) -> ScriptInputParameter:
    """ Parse parameter definitions in the new format.

    Param new format:
        param <name> : <param options separated by colons> : description = <Description of param>

    Examples:
        param simple_param : description = Description of parameter.
        param required_param : required : description = Description of required parameter.
        param param_with_options : options = A, B, C : description = Description of parameter with options.
            Options will be presented as a readonly combobox
        param param_with_required_type : type = str : description = Description of parameter with type.

    Args:
        param_spec (str): Param definition; everything after 'name: '
        param_name (str): Name given to the parameter
    """

    sip: ScriptInputParameter = ScriptInputParameter( name = param_name, type = 'str' )

    for segment in re.finditer( _param_re_iter_splitter, param_spec ):

        if flag := segment.group( 'flag' ):

            if flag == 'required':
                sip.required = True

                continue

        if not segment.group( 'key' ) or segment.group( 'value' ) is None:

            continue

        segment_key: str = segment.group( 'key' ).lower()
        segment_value: str = segment.group( 'value' ).strip()

        if segment_key == 'default':
            sip.default = segment_value

        elif segment_key == 'type':
            sip.type = segment_value

        elif segment_key == 'options':
            sip.alternatives = [ a.strip() for a in segment_value.split( ',' ) ]

        elif segment_key == 'description':
            sip.description = segment_value

    if sip.type in [ 'int', 'float', 'bool' ] and not sip.default:
        if sip.type == 'bool':
            sip.default = 'False'

        elif sip.type == 'int':
            sip.default = '0'

        else:
            sip.default = '0.0'

    if not sip.description:
        sip.description = param_name

    return sip


def _parse_parameter_old_format( value: str, param_name: str ) -> ScriptInputParameter:
    """ Parse parameter definitions in the old format.

    Param old format:
        param name: description
        param param_with_default: description (default: value)
        param required_param: description (required)
        param param_with_alternatives: Test param [ 'A', 'B' ]
            This will be presented as a readonly combobox

    Args:
        value (str): Parameter definition; everything after 'name: '
        param_name (str): Name given to the parameter
    """

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

    return ScriptInputParameter( name = param_name,
                                type = 'str',
                                required = required_match,
                                default = default_value,
                                alternatives = options_list,
                                description = description )


def docstring_parser( raw_docstring: str ) -> tuple[ dict, dict ]:
    """ Parse docstring text and extract field definitions.

    Args:
        raw_docstring (str): Full text inside the docstring definition.

    Returns:
        parsed_data (dict), warnings (dict): Parsed description and fields from the docstring, and warnings for invalid or misspelled field names (parameter names).
    """

    docstring_dict: dict = {}

    if not raw_docstring:

        return docstring_dict, {}

    lines: list[ str ] = raw_docstring.strip().split( '\n' )

    fields_start_idx: int | None = None

    for i, line in enumerate( lines ):
        if line.strip().startswith( ':' ):
            fields_start_idx = i

            break

    if fields_start_idx is None:
        description_lines: list[ str ] = lines
        fields_lines: list[ str ] = []

    else:
        description_lines: list[ str ] = lines[ : fields_start_idx ]
        fields_lines: list[ str ] = lines[ fields_start_idx : ]

    fields, warnings = _parse_fields( fields_lines )

    parsed_data = { 'description': '\n'.join( description_lines ).strip(),
                   **fields }

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
