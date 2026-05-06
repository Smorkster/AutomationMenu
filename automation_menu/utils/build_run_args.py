"""
Build a list of script run arguments

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from automation_menu.models.presetparam import PreSetParam


def build_run_args( params: list[ PreSetParam ] ) -> list[ str ]:
    """ Convert a list of parameters to a list of strings

    Args:
        params (list[PreSetParam]): Parameters to turn into strings
    """

    args: list[ str ] = []

    if not params:

        return args

    for p in params:
        args.append( f'--{ p.name }' )
        args.append( p.set.strip() )

    return args
