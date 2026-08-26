"""
Define grouped execution-related UI reference mappings.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from dataclasses import dataclass

from automation_menu.ui.types.exec_button_refs import ExecutionButtonRefs
from automation_menu.ui.types.exec_min_max_refs import ExecutionMinMaxRefs
from automation_menu.ui.types.exec_post_work_refs import ExecutionPostWorkRefs
from automation_menu.ui.types.exec_pre_work_refs import ExecutionPreWorkRefs
from automation_menu.ui.types.exec_status_refs import ExecutionStatusRefs


@dataclass
class ExecRefs:
    """ Typed dictionary containing grouped execution-related UI reference objects.

    Attributes:
        ExecutionButtonRefs: References used for execution control buttons.
        ExecutionMinMaxRefs: References used for minimize and restore behavior during execution.
        ExecutionPostWorkRefs: References used after execution finishes.
        ExecutionPreWorkRefs: References used before execution starts.
        ExecutionStatusRefs: References used for execution status updates.
    """

    ExecutionButtonRefs: ExecutionButtonRefs
    ExecutionMinMaxRefs: ExecutionMinMaxRefs
    ExecutionPostWorkRefs: ExecutionPostWorkRefs
    ExecutionPreWorkRefs: ExecutionPreWorkRefs
    ExecutionStatusRefs: ExecutionStatusRefs