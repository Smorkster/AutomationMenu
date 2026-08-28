"""
Model for startup arguments

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from typing import Required, TypedDict

from automation_menu.models.enums import ApplicationRunState

class StartupArguments( TypedDict, total = False ):
    """ Typed dictionary describing supported application startup arguments.

    Attributes:
        app_run_state: Initial application run state.
        loglevel: Log level to use during startup.
    """

    app_run_state: Required[ ApplicationRunState ]
    loglevel: Required[ str ]
    mini: Required[ bool ]
