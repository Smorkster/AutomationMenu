"""
Track state and process control for a persistent GUI script session.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


import datetime
import subprocess


import threading
import time
import psutil
import win32gui
import win32process

from dataclasses import dataclass
from psutil import Process

from automation_menu.core.persistent_script_runner import PersistentScriptRunner
from automation_menu.models.enums import ExecutionState
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.types.persistent_session_callbacks import PersistentSessionCallbacks
from automation_menu.types.persistent_ui_callbacks import PersistentUiCallbacks


@dataclass
class PersistentExecutionSession:
    """ Store runtime state and UI hooks for one persistent script session. """

    def __init__( self, id: str, script_info: ScriptInfo, op_callbacks: PersistentUiCallbacks ) -> None:
        """ Session object to handle script execution.

        Args:
            id (str): Session id for running this persistent script
            script_info (ScriptInfo): ScriptInfo about the persistent script
            op_callbacks (PersistentUiCallbacks): Callbacks invoked by the created buttons
        """

        self._session_id: str = id
        self._script_info: ScriptInfo = script_info

        self._can_pause: bool = True
        self._entered_input: list[ str ]
        self._last_output: str = ''
        self._error_list: list[ str ] = []
        self._output_list: list[ str ] = []
        self._process: subprocess.Popen | None = None
        self._progress: float = 0
        self._psutil_children: list[ Process ] = []
        self._psutil_process: Process | None = None
        self._row_id: str = ''
        self._runner: PersistentScriptRunner | None = None
        self._started_at: datetime.datetime = datetime.datetime.now()
        self._state: ExecutionState = ExecutionState.STARTING
        self._status: str = ''
        self._window_handle: int = 0

        self._session_gui_ops: PersistentUiCallbacks = op_callbacks
        self._session_ops: PersistentSessionCallbacks = PersistentSessionCallbacks( update_error = self.update_error,
                                                                                   update_output = self.update_output,
                                                                                   update_progress = self.update_progress,
                                                                                   update_state = self.update_state,
                                                                                   update_status = self.update_status )


    @property
    def progress( self ) -> float:
        """ Return the latest reported progress value.

        Returns:
            (float): Latest progress value for the session.
        """

        return self._progress


    @progress.setter
    def progress( self, value: float ) -> None:
        """ Store the latest reported progress value.

        Args:
            value (float): Progress value reported by the running script.
        """

        self._progress = value


    @property
    def row_id( self ) -> str:
        """ Return the UI list row id assigned to this session.

        Returns:
            (str): Tree view row id for the session.
        """

        return self._row_id


    @row_id.setter
    def row_id( self, value: str ) -> None:
        """ Store the UI list row id and propagate it to the runner.

        Args:
            value (str): Tree view row identifier for the session.
        """

        self._row_id = value

        if self._runner:
            self._runner.row_id = value


    @property
    def script_info( self ) -> ScriptInfo:
        """ Return metadata for the script backing this session.

        Returns:
            (ScriptInfo): Script metadata associated with the session.
        """

        return self._script_info


    @script_info.setter
    def script_info( self, value: ScriptInfo ) -> None:
        """ Replace the script metadata associated with this session.

        Args:
            value (ScriptInfo): Updated script metadata.
        """

        self._script_info = value


    @property
    def session_id( self ) -> str:
        """ Return the unique identifier for this session.

        Returns:
            (str): Session identifier.
        """

        return self._session_id


    @session_id.setter
    def session_id( self, value: str ) -> None:
        """ Set the unique identifier for this session.

        Args:
            value (str): Session identifier.
        """

        self._session_id = value


    @property
    def state( self ) -> ExecutionState:
        """ Return the current execution state.

        Returns:
            (ExecutionState): Current execution state for the session.
        """

        return self._state


    @state.setter
    def state( self, value: ExecutionState ) -> None:
        """ Update the execution state and notify the UI.

        Args:
            value (ExecutionState): New execution state.
        """

        self._state = value
        self.update_state( self._row_id, value )


    @property
    def status( self ) -> str:
        """ Return the latest human-readable status text.

        Returns:
            (str): Current status text for the session.
        """

        return self._status


    @status.setter
    def status( self, value: str ) -> None:
        """ Update the status text and notify the UI.

        Args:
            value (str): New status text to display.
        """

        self._status = value
        self.update_status( self._row_id, value )


    def _get_process_and_children( self, pid: int ) -> None:
        """ Capture the tracked process and any child processes.

        Args:
            pid (int): Process id for the session's root process.
        """

        self._psutil_process = psutil.Process( pid )

        # Check for children
        self._psutil_children = self._psutil_process.children( recursive = True )


    def _wait_stop( self ) -> None:
        """ Wait briefly for a graceful stop request to complete. """

        if self._runner:
            try:
                self._runner.current_process.wait( timeout = 5 )

                self.update_state( self._row_id, ExecutionState.STOPPED )

            except subprocess.TimeoutExpired:

                self.update_state( self._row_id, ExecutionState.STOP_FAILED )


    def _wait_forced_stop( self ) -> None:
        """ Wait for a forced stop operation to terminate the process tree. """

        if self._runner:
            try:
                self._runner.current_process.wait( timeout = 5 )

                self.update_state( self._row_id, ExecutionState.STOPPED )

            except subprocess.TimeoutExpired:

                self.update_state( self._row_id, ExecutionState.FORCED_STOPPING_FAILED )


    def force_stop_runner( self ) -> None:
        """ Force terminate the process tree for this session. """

        if self._runner:
            self.update_state( self._row_id, ExecutionState.FORCED_STOPPING )
            self._runner.current_process.kill()
            threading.Thread( target = self._wait_forced_stop, daemon = True ).start()


    def get_list_data( self ) -> tuple:
        """ Build the values shown for this session in the tree view.

        Returns:
            (tuple): Tuple of values displayed in the persistent sessions list.
        """

        return ( self._script_info.filename, self._status, self._state, self._progress, self._started_at.strftime( '%H:%M:%S' ) )


    def get_main_window_handle( self, pid: int, timeout: float = 5.0 ) -> int:
        """ Return the native window handle for the script, if found.

        Args:
            pid (int): Process id to search windows for.
            timeout (float): Maximum number of seconds to keep searching.

        Returns:
            (int): Window handle for the script's main window, or 0 if none was found.
        """

        end = time.time() + timeout

        while time.time() < end:
            try:
                root = psutil.Process( pid )
                processes = [root] + root.children( recursive = True )
                pids = { p.pid for p in processes }

            except psutil.Error:

                pids = { pid }

            found: list[ int ] = []

            def callback( hwnd: int, _: object ) -> bool:
                """ Collect top-level windows that belong to the script process.

                Args:
                    hwnd (int): Window handle currently being inspected.
                    _ (object): Unused callback state.

                Returns:
                    (bool): True to continue enumeration, False to stop once a match is found.
                """

                if win32gui.GetParent( hwnd ) != 0:

                    return True

                _, pid = win32process.GetWindowThreadProcessId( hwnd )

                if pid in pids:
                    found.append( hwnd )

                    return False

                return True

            win32gui.EnumWindows( callback, None )

            if found:

                return found[ 0 ]

            time.sleep( 0.1 )

        return 0


    def get_all_error( self ) -> str:
        """ Return all captured stderr output as one string.

        Returns:
            (str): Combined error output for the session.
        """

        return '\n'.join( self._error_list )


    def get_all_output( self ) -> str:
        """ Return all captured stdout output as one string.

        Returns:
            (str): Combined standard output for the session.
        """

        return '\n'.join( self._output_list )


    def initiate_runner( self, entered_input: list[ str ], python_exe_path: str, run_state: str ) -> None:
        """ Create and start the persistent script runner for this session.

        Args:
            entered_input (list[str]): Input arguments to pass to the script.
            python_exe_path (str): Path to the Python interpreter used for Python
                scripts.
            run_state (str): Current application run state used when spawning the
                process.
        """

        self._entered_input = entered_input

        self._runner = PersistentScriptRunner( script_info = self._script_info, entered_input = entered_input, op_session_callbacks = self._session_ops, python_exe_path = python_exe_path, run_state = run_state )

        self._process = self._runner.run_script()


    def resume_runner( self ) -> None:
        """ Resume a paused session by sending a continue signal. """

        if not self._runner:

            return

        if self._psutil_process is None:
            self._get_process_and_children( self._runner.current_process.pid )

        if self._psutil_process is None:

            return

        self._psutil_process.resume()

        # Resume children too
        for child in self._psutil_children:
            child.resume()

        self.update_state( row_id = self._row_id, state = 'running' )


    def pause_runner( self ) -> None:
        """ Pause the session process when the script supports it. """

        if not self._runner:

                return

        self._get_process_and_children( self._runner.current_process.pid )

        if self._psutil_process is None:

            return

        self._psutil_process.suspend()

        # Suspend children too
        for child in self._psutil_children:
            child.suspend()

        self.update_state( row_id = self._row_id, state = 'paused' )


    def show_main_window( self ) -> None:
        """ Bring the script window to the foreground when available. """

        if not self._window_handle or not win32gui.IsWindow( self._window_handle ):

            if self._process and self._process.pid is not None:

                self._window_handle = self.get_main_window_handle( pid = self._process.pid )

        if not self._window_handle:

            return

        if win32gui.IsIconic( self._window_handle ):
            win32gui.ShowWindow( self._window_handle, 9 ) # SW_RESTORE

        else:
            win32gui.ShowWindow( self._window_handle, 5 ) # SW_SHOW

        win32gui.SetForegroundWindow( self._window_handle )


    def stop_runner( self ) -> None:
        """ Request a graceful stop for the running session. """

        if self._runner:
            self.update_state( self._row_id, ExecutionState.STOPPING )
            self._runner.current_process.terminate()
            threading.Thread( target = self._wait_stop, daemon = True ).start()


    def update_error( self, row_id: str, error: str ) -> None:
        """ Append error output and refresh the UI.

        Args:
            row_id (str): Tree view row id for the session being updated.
            error (str): Error text to append.
        """

        formated_error: str = f'[{ datetime.datetime.now().strftime( '%H:%M:%S' ) }] { error }'
        self._error_list.append( formated_error )
        self._session_gui_ops.update_ui( lambda: self._session_gui_ops.update_error( self._row_id, formated_error ) )


    def update_output( self, row_id: str, output: str ) -> None:
        """ Append standard output and refresh the UI.

        Args:
            row_id (str): Tree view row id for the session being updated.
            output (str): Output text to append.
        """

        formated_output: str = f'[{ datetime.datetime.now().strftime( '%H:%M:%S' ) }] { output }\n'
        self._output_list.append( formated_output )
        self._session_gui_ops.update_ui( lambda: self._session_gui_ops.update_output( self._row_id, formated_output ) )


    def update_progress( self, row_id: str, progress: float ) -> None:
        """ Store a progress update and refresh the UI.

        Args:
            row_id (str): Tree view row id for the session being updated.
            progress (float): Progress value reported by the script.
        """

        self._progress = progress
        self._session_gui_ops.update_ui( lambda: self._session_gui_ops.update_progress( self._row_id, progress ) )


    def update_state( self, row_id: str, state: str ) -> None:
        """ Store a state change and refresh the UI.

        Args:
            row_id (str): Tree view row id for the session being updated.
            state (str): New execution state.
        """

        self._state = ExecutionState( state.lower() )
        self._session_gui_ops.update_ui( lambda: self._session_gui_ops.update_state( self._row_id, self._state ) )


    def update_status( self, row_id: str, status: str ) -> None:
        """ Store a status message and refresh the UI.

        Args:
            row_id (str): Tree view row id for the session being updated.
            status (str): New status text.
        """

        self._status = status
        self._session_gui_ops.update_ui( lambda: self._session_gui_ops.update_status( self._row_id, status ) )
