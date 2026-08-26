"""
Define typed callback references used by the persistent GUI widgets.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass
from typing import Callable


@dataclass
class PersistentUiCallbacks:
    """ Store callbacks used by persistent GUI widgets construction and interaction."""

    treeview_click: Callable
    treeview_item_selected: Callable

    force_stop_script: Callable
    pause_script: Callable
    resume_script: Callable
    show_script: Callable
    stop_script: Callable

    update_error: Callable
    update_output: Callable
    update_progress: Callable
    update_state: Callable
    update_status: Callable

    update_ui: Callable
