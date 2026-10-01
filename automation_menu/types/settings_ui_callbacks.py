"""
Define typed callback references used by the settings widgets.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass
from typing import Callable


@dataclass
class SettingsUiCallbacks:
    """ Store callbacks used by settings widgets construction and interaction. """

    clear_script_menu: Callable
    gather_script_info: Callable
    get_script_list: Callable
