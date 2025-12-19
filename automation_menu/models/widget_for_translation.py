"""
Class for holding widget that should be available
for text translation

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-31
"""

from dataclasses import dataclass
from tkinter import Widget

from automation_menu.models.enums import ScriptState

@dataclass
class WidgetForTranslation:
    """ Holder for a widget that can have it text translated """

    widget: Widget | None = None
    default_text: str | None = None
    script_state: ScriptState = ScriptState.PROD
    include_application_test_info: bool = False