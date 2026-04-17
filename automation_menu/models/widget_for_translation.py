"""
Class for holding widget that should be available
for text translation

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-31
"""

from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
from dataclasses import dataclass
from tkinter import Widget

from automation_menu.models.enums import ScriptState

@dataclass
class WidgetForTranslation:
    """ Holder for a widget that can have its text translated """

    widget: AlwaysOnTopToolTip | Widget | None = None
    default_text: str | list[ str ] | dict[ str, list[ str | int ] ] | None = None
    script_state: ScriptState = ScriptState.PROD
    include_application_test_info: bool = False