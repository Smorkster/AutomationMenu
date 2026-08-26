"""
Define typed callback references to persistent GUI manager.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass
from typing import Callable


@dataclass
class PersistentManagerCallbacks:
    """ Store callbacks to call persistent GUI manager."""

    get_session_by_row_id: Callable
