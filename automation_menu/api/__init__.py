"""
API entries for the automation API communication

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from ..api.script_api import determinate_progress, hide_progress, indeterminate_progress, set_progress, show_progress
from ..api.script_api import clear_status, get_status, set_status

__all__ = [
    'determinate_progress',
    'hide_progress',
    'indeterminate_progress',
    'set_progress',
    'show_progress',

    'clear_status',
    'get_status',
    'set_status'
]