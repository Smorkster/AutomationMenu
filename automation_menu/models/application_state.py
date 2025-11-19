"""
Application state vault

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from dataclasses import dataclass


@dataclass
class ApplicationState:
    """ State vault for application data """

    from automation_menu.models import Secrets, Settings, User

    current_user: User = None
    running_automation = None
    secrets: Secrets = None
    settings: Settings = None
