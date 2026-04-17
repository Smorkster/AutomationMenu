"""
Manager class for handling script files

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-11-26
"""

from __future__ import annotations
from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING

from automation_menu.models.enums import ApplicationRunState
from automation_menu.models.user import User

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.models.application_state import ApplicationState

from automation_menu.filehandling.script_discovery import get_scripts
from automation_menu.models.scriptinfo import ScriptInfo


class ScriptManager:
    def __init__( self, script_dir_path: Path, current_user: User ) -> None:
        """ Manage script discovery and listing

        Args:
            script_dir_path (Path): Path to script directory
            current_user (User): Current user of application
        """

        self.script_dir_path: Path = script_dir_path
        self._current_user: User = current_user

        self._script_list: list[ ScriptInfo ]


    def gather_scripts( self, output_queue: Queue, app_state: ApplicationState, app_run_state: ApplicationRunState ) -> None:
        """ Call to collect available script files

        Args:
            output_queue (Queue): Queue to post info to
            app_state (ApplicationState): Application state container
            app_run_state (ApplicationRunState): In what state is application running
        """

        self._script_list = get_scripts( output_queue = output_queue, app_state = app_state, app_run_state = app_run_state )


    def get_script_info_by_filename( self, filename: str ) -> ScriptInfo:
        """ Retrieve ScriptInfo for script at path

        Args:
            filename (str): Filename to match to

        Returns:
            (ScriptInfo): Found ScriptInfo

        Raises:
            (ValueError): If no ScriptInfo was found with provided filename
        """

        for si in self._script_list:
            if si.filename == filename:

                return si

        from localization import _

        raise ValueError( _( 'No ScriptInfo was found' ) )


    def get_script_info_by_path( self, path: Path | str | None ) -> ScriptInfo:
        """ Retrieve ScriptInfo for script at path

        Args:
            path (Path | str | None): Path to match to

        Returns:
            (ScriptInfo): Found ScriptInfo, or None

        Raises:
            (ValueError): If no ScriptInfo was found with provided name
        """

        for si in self._script_list:
            if si.fullpath == path:

                return si

        from localization import _

        raise ValueError( _( 'No ScriptInfo was found' ) )


    def get_script_list( self ) -> list[ ScriptInfo ]:
        """ Return list of available scripts """

        return self._script_list
