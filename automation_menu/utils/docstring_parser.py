import ast
import enum
import re

from automation_menu.models.scriptinfo import ScriptInfo

def extract_script_metadata( scriptinfo: ScriptInfo ) -> ScriptInfo:
    """ """

    try:
        with open( scriptinfo.fullpath, 'r', encoding = 'utf-8' ) as f:
            tree = ast.parse( f.read() )

        if ( tree.body
            and isinstance( tree.body[ 0 ], ast.Expr )
            and isinstance( tree.body[ 0 ].value, ast.Constant )
            and isinstance( tree.body[ 0 ].value.value, str ) ):

            parsed_docstring = docstring_parser( tree.body[ 0 ].value.value )

            return parsed_docstring

    except SyntaxError as e:
        from automation_menu.utils.localization import _

        raise ValueError( _( f'Cannot parse {f}:\n{e}' ) ).format( f = scriptinfo.fullpath, e = e )


def docstring_parser( raw_docstring: str ) -> dict:
    """ """

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

    fields = _parse_fields( fields_lines )

    parsed_data = {
        'description': '\n'.join( description_lines ).strip(),
        **fields
    }

    return parsed_data

def _parse_fields( lines ):
    """ """

    fields = {}
    current_field = None
    current_value = []
    field_pattern = re.compile( r'^:([^:]+):\s*(.*)$' )

    for line in lines:
        match = field_pattern.match( line.strip() )

        if match:
            if current_field:
                fields[ current_field ] = '\n'.join( current_value ).strip()

            current_field = match.group( 1 ).strip()
            current_value = [ match.group( 2 ).strip() ] if match.group( 2 ).strip() else []

        elif current_field and line.strip():
            current_value.append( line.strip() )

    if current_field:
        fields[ current_field ] = '\n'.join( current_value ).strip()

    return fields
