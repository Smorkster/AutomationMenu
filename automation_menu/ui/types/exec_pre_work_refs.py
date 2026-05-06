"""
Define widget references used for execution pre-work UI handling.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass
from tkinter import Text, Tk
from tkinter.ttk import Notebook

from automation_menu.ui.types.op_buttons_ui import OpButtonsUi
from automation_menu.ui.types.status_ui import StatusUi


@dataclass
class ExecutionPreWorkRefs:
    """ Store UI references used before script or sequence execution starts."""

    op_buttons: OpButtonsUi

    tab_control: Notebook

    status_widgets: StatusUi

    textbox_output: Text

    root: Tk
