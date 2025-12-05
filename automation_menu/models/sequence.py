"""
Definition of a predefined, automatic, run sequence

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-11-20
"""

from __future__ import annotations

from dataclasses import dataclass
from automation_menu.models.sequencestep import SequenceStep


@dataclass
class Sequence:
    """ Define an automatic run sequence """

    description: str
    name: str
    steps: list[ SequenceStep ]
    stop_on_error: bool
