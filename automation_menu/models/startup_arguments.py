"""
Model for startup arguments

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2026-03-25
"""


from typing import Required, TypedDict

from automation_menu.models.enums import ApplicationRunState

class StartupArguments( TypedDict, total = False ):
    app_run_state: Required[ ApplicationRunState ]
    loglevel: Required[ str ]
