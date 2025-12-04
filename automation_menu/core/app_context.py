"""
Application contaxt management

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-11-11
"""

from __future__ import annotations
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from automation_menu.core.script_execution_manager import ScriptExecutionManager
    from automation_menu.ui.main_window import AutomationMenuWindow

from logging import Logger
import queue

from dataclasses import dataclass, field
from ldap3.core.connection import Connection

from automation_menu.ui.history_manager import HistoryManager
from automation_menu.ui.input_manager import InputManager
from automation_menu.ui.sequence_manager import SequenceManager
from automation_menu.utils.language_manager import LanguageManager
from automation_menu.utils.script_manager import ScriptManager


@dataclass
class ApplicationContext:

    history_manager: HistoryManager = None
    input_manager: InputManager = None
    language_manager: LanguageManager = None
    ldap_connection: Connection = None
    output_queue: queue.Queue = field( default_factory = queue.Queue )
    execution_manager: ScriptExecutionManager = None
    sequence_manager: SequenceManager = None
    script_manager: ScriptManager = None
    main_window: AutomationMenuWindow = None

    debug_logger: Logger = None


    def is_ldap_connected( self ) -> bool:
        """ Check if a connection to LDAP server has been established

        Returns:
            (bool): True if a connection has been created
        """

        return self.ldap_connection != None
