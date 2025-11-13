"""
Application contaxt management

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-11-11
"""

import queue

from dataclasses import dataclass, field
from ldap3.core.connection import Connection

from automation_menu.ui.history_manager import HistoryManager
from automation_menu.ui.input_manager import InputManager


@dataclass
class ApplicationContext:

    history_manager: HistoryManager = None
    input_manager: InputManager = None
    ldap_connection: Connection = None
    output_queue: queue.Queue = field( default_factory = queue.Queue )
    script_manager = None


    def is_ldap_connected( self ) -> bool:
        """ Check if a connection to LDAP server has been established

        Returns:
            (bool): True if a connection has been created
        """

        return self.ldap_connection != None
