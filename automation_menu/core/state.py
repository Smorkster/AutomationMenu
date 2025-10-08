"""
Application state vault

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import queue

from dataclasses import dataclass, field
from ldap3.core.connection import Connection
from typing import Optional

@dataclass
class ApplicationState:
    from automation_menu.models import Secrets, Settings, User

    current_user: Optional[ User ] = None
    ldap_connection: Optional[ Connection ] = None
    output_queue: queue.Queue = field( default_factory = queue.Queue )
    running_automation = None
    secrets: Optional[ Secrets ] = None
    settings: Optional[ Settings ] = None
    script_manager = None


    def is_ldap_connected( self ) -> bool:
        """ Check if a connection to LDAP server has been established

        Returns:
            (bool): True if a connection has been created
        """

        return self.ldap_connection != None