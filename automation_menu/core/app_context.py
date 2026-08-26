"""
Manage shared application context and service references.

This module defines ``ApplicationContext``, a central container for startup
arguments, shared runtime state, UI references, lazily assigned manager
instances, and the shared output queue used across the application.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

import queue

from dataclasses import dataclass
from ldap3.core.connection import Connection
from logging import Logger
from typing import TYPE_CHECKING

from automation_menu.services.persistent_gui_manager import PersistentGuiManager

if TYPE_CHECKING:
    from automation_menu.core.script_execution_manager import ScriptExecutionManager
    from automation_menu.ui.windows.main_window import AutomationMenuWindow

from automation_menu.models.startup_arguments import StartupArguments
from automation_menu.services.error_manager import ErrorManager
from automation_menu.services.history_manager import HistoryManager
from automation_menu.services.script_manager import ScriptManager
from automation_menu.services.sequence_manager import SequenceManager
from automation_menu.services.settings_manager import SettingsManager
from automation_menu.ui.controllers.input_manager import InputManager
from automation_menu.ui.i18n.language_manager import LanguageManager


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
        self._persistent_gui_manager: PersistentGuiManager | None = None
        self._script_manager: ScriptManager | None = None
        self._sequence_manager: SequenceManager | None = None
        self._settings_manager: SettingsManager | None =None

        self._output_queue: queue.Queue | None = None
        self.main_window: AutomationMenuWindow


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


    @ErrorManager.setter
    def ErrorManager( self, value: ErrorManager ) -> None:
        """ Set the shared error manager instance

        Args:
            value (ErrorManager): Error manager instance to store in the shared context.
        """

        self._error_manager = value


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


    @ExecutionManager.setter
    def ExecutionManager( self, value: ScriptExecutionManager ) -> None:
        """ Set the shared script execution manager instance

        Args:
            value (ScriptExecutionManager): Script execution manager instance to store in the shared context.
        """

        self._execution_manager = value


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


    @HistoryManager.setter
    def HistoryManager( self, value: HistoryManager ) -> None:
        """ Set the shared history manager instance

        Args:
            value (HistoryManager): History manager instance to store in the shared context.
        """

        self._history_manager = value


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


    @InputManager.setter
    def InputManager( self, value: InputManager ) -> None:
        """ Set the shared input manager instance

        Args:
            value (InputManager): Input manager instance to store in the shared context.
        """

        self._input_manager = value


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


    @LanguageManager.setter
    def LanguageManager( self, value: LanguageManager ) -> None:
        """ Set the shared language manager instance

        Args:
            value (LanguageManager): Language manager instance to store in the shared context.
        """

        self._language_manager = value


    @property
    def PersistentGuiManager( self ) -> PersistentGuiManager:
        """ Get the initialized manager for persistent GUI scripts

        Returns:
            PersistentGuiManager: The shared manager instance.

        Raises:
            RuntimeError: If the persistent GUI script manager has not been initialized.
        """

        if self._persistent_gui_manager is None:

            raise RuntimeError( 'Persistent GUI manager is not initialized yet' )

        return self._persistent_gui_manager


    @PersistentGuiManager.setter
    def PersistentGuiManager( self, value: PersistentGuiManager) -> None:
        """ Set the persistent GUI manager instance

        Args:
            value (PersistentGuiManager): Persistent GUI manager instance to store.
        """

        self._persistent_gui_manager = value


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


    @ScriptManager.setter
    def ScriptManager( self, value: ScriptManager ) -> None:
        """ Set the shared script manager instance

        Args:
            value (ScriptManager): Script manager instance to store in the shared context.
        """

        self._script_manager = value


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


    @SequenceManager.setter
    def SequenceManager( self, value: SequenceManager ) -> None:
        """ Set the shared sequence manager instance

        Args:
            value (SequenceManager): Sequence manager instance to store in the shared context.
        """

        self._sequence_manager = value


    @property
    def SettingsManager( self ) -> SettingsManager:
        """ Get the initialized settings manager.

        Returns:
            SettingsManager: The shared settings manager instance.

        Raises:
            RuntimeError: If the settings manager has not been initialized.
        """

        if self._settings_manager is None:

            raise RuntimeError( 'Settings manager is not initialized yet' )

        return self._settings_manager


    @SettingsManager.setter
    def SettingsManager( self, value: SettingsManager ) -> None:
        """ Set the shared settings manager instance

        Args:
            value (SettingsManager): Settings manager instance to store in the shared context.
        """

        self._settings_manager = value


    @property
    def OutputQueue( self ) -> queue.Queue:
        """ Get the shared output queue, creating it if needed.

        Returns:
            queue.Queue: The queue used for output messages.
        """

        if self._output_queue is None:
            self._output_queue = queue.Queue()

        return self._output_queue


    @OutputQueue.setter
    def OutputQueue( self, value: queue.Queue ) -> None:
        """ Set the shared output queue instance

        Args:
            value (queue.Queue): Output queue instance to store in the shared context.
        """

        self._output_queue = value


    def is_ldap_connected( self ) -> bool:
        """ Check whether an LDAP connection has been established.

        Returns:
            bool: True if an LDAP connection has been created, otherwise False.
        """

        return self.ldap_connection != None
