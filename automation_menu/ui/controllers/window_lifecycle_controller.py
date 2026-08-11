"""
Control main window close behavior and shutdown handling.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

import json

from dynamicinputbox import dynamic_inputbox
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.models.application_state import ApplicationState

from automation_menu.filehandling.settings_handler import write_settingsfile
from automation_menu.ui.types.exec_lifecycle_refs import ExecutionLifecycleRefs
from automation_menu.utils.decorators import ui_guard_method


class ExecutionWindowLifecycleController:
    """ Control application window close flow and shutdown-related actions."""

    def __init__( self, app_context: 'ApplicationContext', app_state: 'ApplicationState', exec_bindings: ExecutionLifecycleRefs ) -> None:
        """ Initialize the window lifecycle controller.

        Args:
            app_context ('ApplicationContext'): Shared application context.
            app_state ('ApplicationState'): Shared application state.
            exec_bindings (ExecutionLifecycleRefs): Widget and controller references used during shutdown.
        """

        self.app_context = app_context
        self.app_state = app_state
        self.lifecycle_bindings = exec_bindings

        self._close_confirmed: bool = False


    def confirm_close_process( self ) -> bool:
        """ Ask whether a running script should be terminated before closing the application.

        Returns:
            answ (bool): True if the running script should be terminated and closing may continue, otherwise False.
        """

        from automation_menu.utils.localization import _

        line: str = _( 'There is a script running. Do you want to terminate the script process before closing the application?' )
        yes_btn = _( 'Yes' )
        no_btn = _( 'No' )
        answ: bool = dynamic_inputbox( title = _( 'Script still runnning' ), message = line, parent = self.lifecycle_bindings.root, buttons = [ yes_btn, no_btn ] ).show().get_dict()[ 'button' ] == yes_btn

        if answ:
            self.lifecycle_bindings.execution_controller.stop_script()

        return answ


    def serialize_setting( self, key: Any ) -> str:
        """ Normalize a settings value to a string.

        Args:
            key (Any): Key name of the setting to normalize.

        Returns:
            str: String representation of the setting value.
        """

        value = self.app_state.settings.get( key )
        if value is None:

            return ""

        if isinstance( value, ( str, int, float, bool ) ):

            return str( value )

        # dict / list / TypedDict / dataclasses / etc.
        try:

            return json.dumps( value, ensure_ascii = False, default = str )

        except TypeError:

            return str( value )


    @ui_guard_method( when_message = 'Closing main window' )
    def on_closing( self ) -> None:
        """ Handle main window close events, including running scripts and settings persistence. """

        from automation_menu.utils.localization import _

        if not self._close_confirmed and self.app_context.ExecutionManager.is_running():
            if not self.confirm_close_process():

                return

        try:
            write_settingsfile( settings = self.app_state.settings, settings_file_path = self.app_state.secrets[ 'settings_file_path' ] )

        except Exception as e:

            dynamic_inputbox( title = _( 'Write settings error' ), message = _( 'Could not save settings to file: {e}' ).format( e = e ) ).show()

            return

        self.lifecycle_bindings.root.destroy()

        if hasattr( self.lifecycle_bindings, 'output_controller' ):
            try:
                self.lifecycle_bindings.output_controller.closedown()

            except Exception as e:
                self.app_context.debug_logger.warning( _( 'Error shutting down output controller: {e}' ).format( e = e ) )
