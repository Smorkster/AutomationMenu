import ast
import re

from automation_menu.models.enums import ScriptState, ValidScriptInfoFields
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.scriptinputparameter import ScriptInputParameter

def extract_script_metadata( script_info: ScriptInfo ) -> tuple[ dict, dict ]:
    """ Extract the docstring for script

    Args:
        scriptinfo (ScriptInfo): ScriptInfo object for found script file

    Returns:
        parsed_data (dict): Description and fields, including script input parameters,
            specified in the docstring
        warnings (list[ str ]): List of specified fieldnames that does not correspond
            to valid field names or are misspelled
    """

    try:
        with open( script_info.get_attr( 'fullpath' ), 'r', encoding = 'utf-8' ) as f:
            tree = ast.parse( f.read() )

        if ( tree.body
            and isinstance( tree.body[ 0 ], ast.Expr )
            and isinstance( tree.body[ 0 ].value, ast.Constant )
            and isinstance( tree.body[ 0 ].value.value, str ) ):

            parsed_docstring, warnings = docstring_parser( tree.body[ 0 ].value.value )

            return parsed_docstring, warnings

    except SyntaxError as e:
        from automation_menu.utils.localization import _

        raise ValueError( _( f'Cannot parse {f}:\n{e}' ) ).format( f = script_info.get_attr( 'fullpath' ), e = e )


def docstring_parser( raw_docstring: str ) -> tuple[ dict, dict ]:
    """ Parse docstring text and extract teh rows with field definitions

    Args:
        raw_docstring (str): The full text inside the docstring definition

    Returns:
        parsed_data (dict): Description and fields, including script input parameters,
            specified in the docstring
        warnings (list[ str ]): List of specified fieldnames that does not correspond
            to valid field names or are misspelled
    """

    docstring_dict = {}

    if not raw_docstring:
        return docstring_dict

    lines = raw_docstring.strip().split( '\n' )

    fields_start_idx = None
    for i, line in enumerate( lines ):
        if line.strip().startswith( ':' ):
            fields_start_idx = i
            break

    if fields_start_idx:
        description_lines = lines[ : fields_start_idx ]
        fields_lines = lines[ fields_start_idx : ]

    else:
        description_lines = lines
        fields_lines = []

    fields, warnings = _parse_fields( fields_lines )

    parsed_data = {
        'description': '\n'.join( description_lines ).strip(),
        **fields
    }

    return parsed_data, warnings


def _parse_fields( lines ) -> tuple[ dict, dict ]:
    """ Parse metadata fields

    Args:
        lines (list[ str ]): List of rows
    """

    from automation_menu.utils.localization import _

    current_field = None
    current_value = []
    fields = {}
    parameters = []
    warnings = {
        'keys': [],
        'values': [],
        'other': [],
    }
    field_pattern = re.compile( r'^:([^:]+):\s*(.*)$' )

    for line in lines:
        match = field_pattern.match( line.strip() )

        if match:

            current_field = match.group( 1 ).strip()
            current_value = match.group( 2 ).strip() if match.group( 2 ).strip() else ''

            if current_field.startswith( 'param ' ):
                param = _parse_parameters( field = current_field, value = current_value )
                parameters.append( param )

            else:
                try:
                    ValidScriptInfoFields( current_field.lower() )
                    if current_field.lower() == 'state':
                        current_value = ScriptState[ current_value.upper() ]

                    fields[ current_field ] = current_value

                except KeyError:
                    warnings[ 'keys' ].append( current_value )

                except ValueError:
                    warnings[ 'values' ].append( current_field )

                except Exception as e:
                    warnings[ 'other' ].append( current_field )

    fields[ 'script_input_parameters' ] = parameters

    return fields, warnings


def _parse_parameters( field: str, value: str ) -> ScriptInputParameter:
    """ Extract script input parameters info

    Parse fields like:
    param name: description
    param param_with_default: description (default: value)
    param required_param: description (required)

    Args:
        field (str): Field name from docstring
        value (str): Field value from docstring
    """

    param_name = field[ 6 : ].strip()

    default_match = re.search( r'\(default:\s*([^)]+)\)', value, re.IGNORECASE )
    default_value = default_match.group( 1 ).strip() if default_match else None

    required_match = re.search( r'\(required\)', value, re.IGNORECASE ) != None

    description = re.sub( r'\s*\(default:[^)]+\)', '', re.sub( r'\s*\(required\)', '', value.strip() ).strip() )

    return ScriptInputParameter(
        name = param_name,
        type = 'str',
        required = required_match,
        default = default_value,
        description = description
    )
