"""
Read script file content for any defined ScriptInfo
This is the old format of script meta data, and should
only be used in PowerShell script files


Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-31
"""

import re

from re import Match

from automation_menu.models.enums import ScriptState, ValidScriptInfoFields


def scriptinfo_block_parser( full_text: str ) -> tuple[ dict, dict ]:
    """ Parse the file content and extract script information

    Args:
        full_text (str): Scriptfile content to parse

    Returns:
        (tuple[ scriptinfo_meta, warnings ]): Script information from the script info block and list of invalid keys and values
    """

    match: Match | None = re.search( r'ScriptInfo\s*(.*?)\s*ScriptInfoEnd', full_text, re.DOTALL )

    if not match:

        return {}, {}

    scriptinfo_meta: dict = {}
    warnings: dict[ str, list[ str ] ] = {
        'keys': [],
        'values': [],
        'other': []
    }

    value_to_use: bool | list[ str ] | str | ScriptState

    # Extract key-value pairs inside ScriptInfo block
    for current_field, current_value in re.findall( pattern = r"#\s*(\w+)(?:\s*-\s*(.+))?", string = match.group( 1 ) ):
        value: str = current_value.replace( ' ', '' )

        if current_field == 'RequiredAdGroups':
            value_to_use = value.split( ';' )

        elif current_field == 'AllowedUsers':
            value_to_use = value.split( ';' )

        elif current_field == 'DisableMinimizeOnRunning':
            value_to_use = True

        elif current_value == '':
            value_to_use = True

        else:
            value_to_use = current_value

        try:
            ValidScriptInfoFields[ current_field.upper() ]
            if current_field == 'RequiredAdGroups':
                current_field = 'required_ad_groups'

            elif current_field == 'AllowedUsers':
                current_field = 'allowed_users'

            elif current_field == 'DisableMinimizeOnRunning':
                current_field = 'disable_minimize_on_running'

            if current_field.lower() == 'state':
                value_to_use = ScriptState[ str( value_to_use ).upper() ]

            scriptinfo_meta[ current_field.lower() ] = value_to_use

        except KeyError:
            warnings[ 'keys' ].append( str( value_to_use ) )

        except ValueError:
            warnings[ 'values' ].append( current_field )

        except Exception as e:
            warnings[ 'other' ].append( current_field )

    return scriptinfo_meta, warnings
