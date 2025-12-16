"""
Application state vault

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass

from automation_menu.core.script_menu_item import ScriptMenuItem


@dataclass
class ApplicationState:
    """ State vault for application data """

    from automation_menu.models import Secrets, Settings, User

    current_user: User = None
    running_automation: ScriptMenuItem = None
    secrets: Secrets = None
    settings: Settings = None
