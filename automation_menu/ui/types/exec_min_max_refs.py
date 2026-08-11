"""
Define widget references used for execution-time window minimize and restore behavior.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass
from tkinter import Tk
from tkinter.ttk import Notebook

from automation_menu.ui.types.op_buttons_ui import OpButtonsUi
from automation_menu.ui.types.status_ui import StatusUi


@dataclass
class ExecutionMinMaxRefs:
    """ Store UI references used when minimizing or restoring the window during execution."""

    tab_control: Notebook

    op_buttons: OpButtonsUi

    status_ui: StatusUi

    root: Tk

    win_minimized_width: int = 400
    win_minimized_height: int = 200
    win_min_size_width: int = 620
    win_min_size_height: int = 600
