"""
Definition of a step for an automatic sequence

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-11-20
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SequenceStep:
    """ Definition of a sequence step """

    script_file: str = None
    pre_set_parameters: dict[ str, str ] = None
    stop_on_error: bool = False
    step_index: int = 0
    script_info: str = None
