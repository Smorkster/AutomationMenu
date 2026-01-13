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

    match: Match = re.search( r'ScriptInfo\s*(.*?)\s*ScriptInfoEnd', full_text, re.DOTALL )

    if not match:

        return None, []

    scriptinfo_meta: dict = {}
    warnings: dict[ list[ str ], list[ str ], list[ str ]] = {
        'keys': [],
        'values': [],
        'other': []
    }

    # Extract key-value pairs inside ScriptInfo block
    for current_field, current_value in re.findall( pattern = r"#\s*(\w+)(?:\s*-\s*(.+))?", string = match.group( 1 ) ):
        value: str = current_value.replace( ' ', '' )

        if current_field == 'RequiredAdGroups':
            value_to_use: list[ str ] = value.split( ';' )

        elif current_field == 'AllowedUsers':
            value_to_use: list[ str ] = value.split( ';' )

        elif current_field == 'DisableMinimizeOnRunning':
            value_to_use: bool = True

        elif current_value == '':
            value_to_use: bool = True

        else:
            value_to_use: str = current_value

        try:
            ValidScriptInfoFields[ current_field.upper() ]
            if current_field == 'RequiredAdGroups':
                current_field: str = 'required_ad_groups'

            elif current_field == 'AllowedUsers':
                current_field : str= 'allowed_users'

            elif current_field == 'DisableMinimizeOnRunning':
                current_field: str = 'disable_minimize_on_running'

            if current_field.lower() == 'state':
                value_to_use: ScriptState = ScriptState[ value_to_use.upper() ]

            scriptinfo_meta[ current_field.lower() ] = value_to_use

        except KeyError:
            warnings[ 'keys' ].append( value_to_use )

        except ValueError:
            warnings[ 'values' ].append( current_field )

        except Exception as e:
            warnings[ 'other' ].append( current_field )


    return scriptinfo_meta, warnings
