"""
Window/widget geometry model

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass

@dataclass
class Geometry:
    """ Represent width, height, and position for a Tkinter geometry string. """

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
