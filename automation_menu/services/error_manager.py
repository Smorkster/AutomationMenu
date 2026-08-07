"""
Manager for error handling

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from ldap3 import Connection
from pathlib import Path

from automation_menu.models.application_state import ApplicationState
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.utils.email_handler import send_error_mail


class ErrorManager:
    def __init__( self, app_state: ApplicationState, ldap_connection: Connection | None ) -> None:
        """ Manage language change and GUI update

        Args:
            app_state (ApplicationState): Current application state container
            ldap_connection (Connection | None): Connection to LDAP server
        """

        self._app_state = app_state
        self._ldap_connection = ldap_connection


    def report_script_error( self, script_info: ScriptInfo, error_msg: str, screenshot: Path ) -> bool:
        """ Send an mail error report

        Args:
            script_info (ScriptInfo): Info about the script that failed
            error_msg (str): Errormessage sent from the script
            screenshot (Path): Path to screenshot of the main window

        Raises:
            ConnectionError: If connection to LDAP server was lost or not established
        """

        from automation_menu.utils.localization import _

        if self._ldap_connection is None:

            raise ConnectionError( _( 'No connection to LDAP server established' ) )

        return send_error_mail( app_state = self._app_state,
                               ldap_connection = self._ldap_connection,
                               script_info = script_info,
                               error_msg = error_msg,
                               screenshot = screenshot, )
