"""
Build a list of script run arguments

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from automation_menu.models.presetparam import PreSetParam


def build_run_args( pre_set_params: list[ PreSetParam ] ) -> list[ str ]:
    """ Convert a list of parameters to a list of strings

    Args:
        pre_set_params (list[ PreSetParam ]): Parameters to turn into strings
    """

    args: list[ str ] = []

    if not pre_set_params:

        return args

    for param in pre_set_params:
        args.append( f'--{ param.name }' )
        args.append( str( param.set ).strip() )

    return args
