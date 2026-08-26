"""
Application state vault

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import  Optional

from automation_menu.core.script_menu_item import ScriptMenuItem


@dataclass
class ApplicationState:
    """ State vault for application data """

    from automation_menu.models import Secrets, Settings, User

    secrets: Secrets
    current_user: User
    settings: Settings
    run_state: str

    python_exe_path: str = ''
    running_automation: Optional[ ScriptMenuItem ] = None
