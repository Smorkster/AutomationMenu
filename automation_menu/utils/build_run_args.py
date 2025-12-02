"""
Build a list of script run arguments

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-12-01
"""


def build_run_args( params: list[ dict[ str, str ] ] = [] ) -> list[ str ]:
    """ Convert a list of parameters to a list of strings """

    args: list[ str ] = []

    if not params:

        return args

    for p in params:
        args.append( f'--{ p[ 'name' ] }' )
        args.append( p[ 'set' ].strip() )

    return args