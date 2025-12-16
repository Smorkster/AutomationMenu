"""
Window/widget geometry model

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-12-16
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass

@dataclass
class Geometry:

    height: int = 0
    width: int = 0
    x: int = 0
    y: int = 0


    def to_string( self ) -> str:
        """ Format values to tkinter geometry string

        Returns:
            (str): Geometry formated string
        """

        return f'{ self.width }x{ self.height }+{ self.x }+{ self.y }'
