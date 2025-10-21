"""
Model for defining a parameter used as input for script execution

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-17
"""

from dataclasses import dataclass
from typing import Optional, Union


@dataclass
class ScriptInputParameter:
    """ Represents a single input parameter """

    name: str
    type: Union[ str, int, bool ]
    required: bool = True
    default: Optional[ str ] = None
    description: str = ''


