"""
Manager class for handling script files

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

import json
from pathlib import Path
from queue import Queue
from typing import TYPE_CHECKING

from automation_menu.utils.move_file_to_trashcan import recycle

if TYPE_CHECKING:
    from automation_menu.models.application_state import ApplicationState

from automation_menu.filehandling.script_cache_handler import get_menu_cache_path, read_menu_cache, write_menu_cache_file
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
        self._menu_cache_path: Path
        self._output_queue: Queue
        self._app_state: ApplicationState
        self._app_run_state: ApplicationRunState

        self._script_list: list[ ScriptInfo ] = []


    def gather_scripts( self, output_queue: Queue | None = None, app_state: ApplicationState | None = None, app_run_state: ApplicationRunState | None = None, clear_cache: bool = False ) -> None:
        """ Collect available script files.

        Args:
            output_queue (Queue | None): Queue to post progress and output information to.
            app_state (ApplicationState | None): Application state container.
            app_run_state (ApplicationRunState | None): Current application run state.
            clear_cache (bool): True if script infos are re-read.
        """

        if output_queue:
            self._output_queue = output_queue

        if app_state:
            self._app_state = app_state

        if app_run_state:
            self._app_run_state = app_run_state

        self._menu_cache_path = get_menu_cache_path()

        if clear_cache:
            recycle( str( self._menu_cache_path ) )
            self._script_list.clear()

        if self._menu_cache_path.exists():
            menu_cache_from_file: dict = read_menu_cache( self._menu_cache_path )

            for k, d in menu_cache_from_file.items():
                s: ScriptInfo = ScriptInfo.from_dict( d )
                self._script_list.append( s )

            return

        self._script_list = get_scripts( output_queue = self._output_queue,
                                        app_state = self._app_state,
                                        app_run_state = self._app_run_state )

        self.write_menu_cache()


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


    def write_menu_cache( self ) -> None:
        """ Write the menu items to cache """

        menu_as_dict: dict = {}

        for s in self._script_list:
            menu_as_dict[ hash( s.fullpath ) ] = s.to_dict()

        write_menu_cache_file( cache_file_path = self._menu_cache_path, cache_content = json.dumps( menu_as_dict ) )
