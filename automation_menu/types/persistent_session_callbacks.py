"""
Define typed callback references for session communications.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass
from typing import Callable


@dataclass
class PersistentSessionCallbacks:
    """ Store callbacks used by persistent GUI sessions."""

    update_error: Callable
    update_output: Callable
    update_progress: Callable
    update_state: Callable
    update_status: Callable
