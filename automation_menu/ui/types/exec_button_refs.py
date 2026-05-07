"""
Define widget references for execution-related buttons.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from dataclasses import dataclass
from tkinter import Tk
from tkinter.ttk import Button

@dataclass
class ExecutionButtonRefs:
    """ Store widget references used for execution button control."""

    btn_pause_resume_script: Button

    root: Tk