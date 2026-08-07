"""
Model for defining a parameter used as input for script execution

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from dataclasses import dataclass


@dataclass
class ScriptInputParameter:
    """ Represents a single input parameter """

    alternatives: list[ str ] | None = None
    default: str = ''
    description: str = ''
    name: str = ''
    required: bool = False
    type: str = ''
