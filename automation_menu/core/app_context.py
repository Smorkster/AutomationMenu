"""
Application contaxt management

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from automation_menu.core.script_execution_manager import ScriptExecutionManager
    from automation_menu.ui.main_window import AutomationMenuWindow

import queue

from dataclasses import dataclass
from ldap3.core.connection import Connection
from logging import Logger

from automation_menu.models.startup_arguments import StartupArguments
from automation_menu.services.error_manager import ErrorManager
from automation_menu.ui.history_manager import HistoryManager
from automation_menu.ui.input_manager import InputManager
from automation_menu.ui.sequence_manager import SequenceManager
from automation_menu.utils.language_manager import LanguageManager
from automation_menu.utils.script_manager import ScriptManager


@dataclass
class ApplicationContext:
    """ Hold shared application state and service references """

    def __init__( self, debug_logger: Logger, startup_arguments: StartupArguments ) -> None:
        """ Initialize the application context.

        Args:
            debug_logger (Logger): Logger used for debug output.
            startup_arguments (StartupArguments): Parsed startup arguments for the application.
        """

        self.debug_logger: Logger = debug_logger
        self.startup_arguments: StartupArguments = startup_arguments
        self.ldap_connection: Connection

        self._language_manager: LanguageManager | None = None
        self._error_manager: ErrorManager | None = None
        self._execution_manager: ScriptExecutionManager | None = None
        self._history_manager: HistoryManager | None = None
        self._input_manager: InputManager | None = None
        self._script_manager: ScriptManager | None = None
        self._sequence_manager: SequenceManager | None = None

        self._output_queue: queue.Queue | None = None
        self.main_window: Optional[ AutomationMenuWindow ] = None


    @property
    def ErrorManager( self ) -> ErrorManager:
        """ Get the initialized error manager.

        Returns:
            ErrorManager: The shared error manager instance.

        Raises:
            RuntimeError: If the error manager has not been initialized.
        """

        if self._error_manager is None:
            raise RuntimeError( 'Error manager is not initialized yet' )

        return self._error_manager


    @property
    def ExecutionManager( self ) -> ScriptExecutionManager:
        """ Get the initialized script execution manager.

        Returns:
            ScriptExecutionManager: The shared script execution manager instance.

        Raises:
            RuntimeError: If the script execution manager has not been initialized.
        """

        if self._execution_manager is None:
            raise RuntimeError( 'Script execution manager is not initialized yet' )

        return self._execution_manager


    @property
    def HistoryManager( self ) -> HistoryManager:
        """ Get the initialized history manager.

        Returns:
            HistoryManager: The shared history manager instance.

        Raises:
            RuntimeError: If the history manager has not been initialized.
        """

        if self._history_manager is None:
            raise RuntimeError( 'History manager is not initialized yet' )

        return self._history_manager


    @property
    def InputManager( self ) -> InputManager:
        """ Get the initialized input manager.

        Returns:
            InputManager: The shared input manager instance.

        Raises:
            RuntimeError: If the input manager has not been initialized.
        """

        if self._input_manager is None:
            raise RuntimeError( 'Input manager is not initialized yet' )

        return self._input_manager


    @property
    def LanguageManager( self ) -> LanguageManager:
        """ Get the initialized language manager.

        Returns:
            LanguageManager: The shared language manager instance.

        Raises:
            RuntimeError: If the language manager has not been initialized.
        """

        if self._language_manager is None:
            raise RuntimeError( 'Language manager is not initialized yet' )

        return self._language_manager


    @property
    def ScriptManager( self ) -> ScriptManager:
        """ Get the initialized script manager.

        Returns:
            ScriptManager: The shared script manager instance.

        Raises:
            RuntimeError: If the script manager has not been initialized.
        """

        if self._script_manager is None:
            raise RuntimeError( 'Script manager is not initialized yet' )

        return self._script_manager


    @property
    def SequenceManager( self ) -> SequenceManager:
        """ Get the initialized sequence manager.

        Returns:
            SequenceManager: The shared sequence manager instance.

        Raises:
            RuntimeError: If the sequence manager has not been initialized.
        """

        if self._sequence_manager is None:
            raise RuntimeError( 'Sequence manager is not initialized yet' )

        return self._sequence_manager


    @property
    def OutputQueue( self ) -> queue.Queue:
        """ Get the shared output queue, creating it if needed.

        Returns:
            queue.Queue: The queue used for output messages.
        """

        if self._output_queue is None:
            self._output_queue = queue.Queue()

        return self._output_queue


    def is_ldap_connected( self ) -> bool:
        """ Check whether an LDAP connection has been established.

        Returns:
            bool: True if an LDAP connection has been created, otherwise False.
        """

        return self.ldap_connection != None
