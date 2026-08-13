"""
Model for containing execution of a script, its output
and status widgets

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass
from tkinter import Text
from tkinter import DoubleVar, ttk, StringVar
from tkinter.ttk import Frame

from automation_menu.core.script_runner import ScriptRunner


@dataclass
class ExecutionView:
    """ Model for concurrent script execution """

    source_id: str
    runner: ScriptRunner | None
    active_run_id: str | None
    state: ExecutionState

    frame: ttk.Frame
    text: Text
    status_var: StringVar
    progress_var: DoubleVar
