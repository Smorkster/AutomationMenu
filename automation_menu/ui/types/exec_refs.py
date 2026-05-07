"""
Define grouped execution-related UI reference mappings.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from typing import TypedDict

from automation_menu.ui.types.exec_min_max_refs import ExecutionMinMaxRefs
from automation_menu.ui.types.exec_button_refs import ExecutionButtonRefs
from automation_menu.ui.types.exec_post_work_refs import ExecutionPostWorkRefs
from automation_menu.ui.types.exec_pre_work_refs import ExecutionPreWorkRefs
from automation_menu.ui.types.exec_status_refs import ExecutionStatusRefs


class ExecRefs( TypedDict ):
    """Typed dictionary containing grouped execution-related UI reference objects.

    Attributes:
        ExecutionMinMaxRefs: References used for minimize and restore behavior during execution.
        ExecutionPreWorkRefs: References used before execution starts.
        ExecutionPostWorkRefs: References used after execution finishes.
        ExecutionButtonRefs: References used for execution control buttons.
        ExecutionStatusRefs: References used for execution status updates.
    """

    ExecutionButtonRefs: ExecutionButtonRefs
    ExecutionMinMaxRefs: ExecutionMinMaxRefs
    ExecutionPostWorkRefs: ExecutionPostWorkRefs
    ExecutionPreWorkRefs: ExecutionPreWorkRefs
    ExecutionStatusRefs: ExecutionStatusRefs