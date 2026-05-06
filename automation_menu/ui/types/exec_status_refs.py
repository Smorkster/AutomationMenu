"""
Define widget references used for execution status display updates.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass
from tkinter import Tk
from tkinter.ttk import Frame, Label, Progressbar, Separator


@dataclass
class ExecutionStatusRefs:
    """ Store UI references used for execution status and progress updates."""

    progress_frame: Frame

    text_status: Label

    progressbar: Progressbar

    separator: Separator

    root: Tk