"""
Manager class for handling script files

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-11-26
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.models.application_state import ApplicationState

from automation_menu.filehandling.script_discovery import get_scripts
from automation_menu.models.scriptinfo import ScriptInfo


class ScriptManager:
    def __init__( self, app_state: ApplicationState, app_context: ApplicationContext ) -> None:
        """ Manage script discovery and listing """

        self._app_context = app_context
        self._app_state = app_state

        self._script_list = None

        self.gather_scripts()


    def gather_scripts( self ) -> None:
        """ Call to collect available script files """

        self._script_list = get_scripts( output_queue = self._app_context.output_queue, app_state = self._app_state )


    def get_script_info_by_filename( self, filename: str ) -> ScriptInfo:
        """ Retrieve ScriptInfo for script at path """

        for si in self._script_list:
            if si.filename == filename:

                return si

        return None


    def get_script_info_by_path( self, path: str ) -> ScriptInfo:
        """ Retrieve ScriptInfo for script at path """

        for si in self._script_list:
            if si.fullpath == path:

                return si

        return None


    def get_script_list( self ) -> list[ ScriptInfo ]:
        """ Return list of available scripts """

        return self._script_list
