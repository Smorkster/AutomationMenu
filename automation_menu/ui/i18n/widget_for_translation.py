"""
Class for holding widget that should be available
for text translation

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
from dataclasses import dataclass
from tkinter import Widget

from automation_menu.models.enums import ScriptState

@dataclass
class WidgetForTranslation:
    """ Store a widget and its translation metadata."""

    widget: AlwaysOnTopToolTip | Widget | None = None

    include_application_test_info: bool = False

    script_state: ScriptState = ScriptState.PROD

    default_text: str | list[ str ] | dict[ str, list[ str | int ] ] | None = None
