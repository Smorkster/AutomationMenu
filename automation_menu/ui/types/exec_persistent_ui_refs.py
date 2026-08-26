"""
Typed references for widgets used by the persistent execution UI.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from dataclasses import dataclass
from tkinter.ttk import Treeview

from automation_menu.ui.types.op_persistent_buttons_ui import OpPersistentButtonsUi


@dataclass
class ExecutionPersistentUiRefs:
    """ Bundle tree view and button references for persistent execution widgets. """

    persistent_scripts_list: Treeview

    persistent_ui_buttons: OpPersistentButtonsUi
