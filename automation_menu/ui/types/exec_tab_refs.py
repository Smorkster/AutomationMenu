"""
Define widget references used for execution-related tab management.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass
from tkinter.ttk import Notebook


@dataclass
class ExecutionTabUiRefs:
    """ Store UI references used for execution tab control."""

    tab_control: Notebook
