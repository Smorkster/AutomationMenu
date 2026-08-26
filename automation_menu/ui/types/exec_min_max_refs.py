"""
Define widget references used for execution-time window minimize and restore behavior.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass
from tkinter import Tk
from tkinter.ttk import Notebook

from automation_menu.ui.types.menu_buttons_ui import MenuButtonsUi
from automation_menu.ui.types.op_buttons_ui import OpButtonsUi
from automation_menu.ui.types.status_ui import StatusUi


@dataclass
class ExecutionMinMaxRefs:
    """ Store UI references used when minimizing or restoring the window during execution."""

    menu_buttons: MenuButtonsUi

    tab_control: Notebook

    op_buttons: OpButtonsUi

    status_ui: StatusUi

    root: Tk
