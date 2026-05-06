"""
Define widget references used for execution post-work UI handling.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from dataclasses import dataclass
from tkinter import Tk

@dataclass
class ExecutionPostWorkRefs:
    """ Store UI references used after script or sequence execution finishes."""

    root: Tk