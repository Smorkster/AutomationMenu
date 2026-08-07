"""
Manager class for handling script files

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.models.application_state import ApplicationState

from automation_menu.filehandling.script_discovery import get_scripts
from automation_menu.models.enums import ApplicationRunState
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.user import User


class ScriptManager:
    """ Manage script discovery and retrieval for available scripts."""

    def __init__( self, script_dir_path: list[ Path ], current_user: User ) -> None:
        """ Initialize the script manager.

        Args:
            script_dir_path (list[Path]): Paths to script directories.
            current_user (User): Current user of the application.
        """

        self.script_dir_path: list[ Path ] = script_dir_path
        self._current_user: User = current_user

        self._script_list: list[ ScriptInfo ]


    def gather_scripts( self, output_queue: Queue, app_state: ApplicationState, app_run_state: ApplicationRunState ) -> None:
        """ Collect available script files.

        Args:
            output_queue (Queue): Queue to post progress and output information to.
            app_state (ApplicationState): Application state container.
            app_run_state (ApplicationRunState): Current application run state.
        """

        self._script_list = get_scripts( output_queue = output_queue,
                                        app_state = app_state,
                                        app_run_state = app_run_state )


    def get_script_info_by_filename( self, filename: str ) -> ScriptInfo:
        """ Retrieve script information for a script by filename.

        Args:
            filename (str): Filename to match.

        Returns:
            si (ScriptInfo): Found script information.

        Raises:
            ValueError: If no ScriptInfo was found with the provided filename.
        """

        for si in self._script_list:
            if si.filename == filename:

                return si

        from automation_menu.utils.localization import _

        raise ValueError( _( 'No ScriptInfo with file name {f} was found' ).format( f = filename ) )


    def get_script_info_by_path( self, path: Path | str | None ) -> ScriptInfo:
        """ Retrieve script information for a script by path.

        Args:
            path (Path | str | None): Path to match.

        Returns:
            si (ScriptInfo): Found script information.

        Raises:
            ValueError: If no ScriptInfo was found with the provided path.
        """

        for si in self._script_list:
            if si.fullpath == str( path ):

                return si

        from automation_menu.utils.localization import _

        raise ValueError( _( 'No ScriptInfo at path {p} was found' ).format( p =  path ) )


    def get_script_list( self ) -> list[ ScriptInfo ]:
        """ Get the list of available scripts.

        Returns:
            (list[ScriptInfo]): Available scripts.
        """

        return self._script_list
