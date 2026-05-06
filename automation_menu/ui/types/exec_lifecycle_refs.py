"""
Define widget and controller references used during window lifecycle handling.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass
from tkinter import Tk
from tkinter.ttk import Notebook

from automation_menu.ui.controllers.async_output_controller import AsyncOutputController
from automation_menu.ui.controllers.execution_ui_controller import ExecutionUiController
from automation_menu.ui.types.op_buttons_ui import OpButtonsUi
from automation_menu.ui.types.status_ui import StatusUi


@dataclass
class ExecutionLifecycleRefs:
    """ Store UI and controller references used for execution lifecycle operations."""

    output_controller: AsyncOutputController

    execution_controller: ExecutionUiController

    tab_control: Notebook

    op_buttons: OpButtonsUi

    status_ui: StatusUi

    root: Tk
