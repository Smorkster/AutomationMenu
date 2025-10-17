import re
from automation_menu.models.scriptinfo import ScriptInfo


def scriptinfo_block_parser( si: ScriptInfo ) -> dict:
    """ Parse the file content and extract script information

    Args:
        lines (list[ str ]): All lines of the scriptfile
        si (ScriptInfo): Script info gathered from the scripts info block

    Returns:
        si (ScriptInfo): Script information specified in the script info block
    """

    with open( si.fullpath, 'r', encoding = 'utf-8' ) as f:
        full_text = f.read()

    match = re.search( r'ScriptInfo\s*(.*?)\s*ScriptInfoEnd', full_text, re.DOTALL )

    if not match:
        return None

    scriptinfo_meta = {}
    # Extract key-value pairs inside ScriptInfo block
    for p, t in re.findall( pattern = r"#\s*(\w+)(?:\s*-\s*(.+))?", string = match.group( 1 ) ):
        value = t.replace( ' ', '' )

        if p == 'RequiredAdGroups':
            p = 'required_ad_groups'
            v = value.split( ';' )

        elif p == 'AllowedUsers':
            #si.add_attr( p, value.split( ';' ) )
            p = 'allowed_users'
            v = value.split( ';' )

        elif t == '':
            #si.add_attr( p , True )
            v = True

        else:
            #si.add_attr( p, t )
            v = t

        scriptinfo_meta [ p.lower() ] = v

    return scriptinfo_meta
