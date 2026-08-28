"""
Run and monitor persistent GUI scripts in background processes.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""



import json
import re
import subprocess

from automation_menu.core.process_execution import ProcessExecution
from automation_menu.models.enums import ExecutionState
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.types.persistent_session_callbacks import PersistentSessionCallbacks
from automation_menu.utils.localization import _


class PersistentScriptRunner:
    """Execute a persistent GUI script and forward its state updates. """

    def __init__( self, script_info: ScriptInfo, entered_input: list[ str ], op_session_callbacks: PersistentSessionCallbacks, python_exe_path: str, run_state: str ) -> None:
        """ Store script execution details and UI callback hooks.

        Args:
            script_info (ScriptInfo): Metadata for the script to run.
            entered_input (list[str]): Input arguments to pass to the script.
            op_session_callbacks (PersistentSessionCallbacks): Callbacks used to push
                output, status, progress, and state updates back to the session.
            python_exe_path (str): Path to the Python interpreter used to launch
                Python scripts.
            run_state (str): Current application run state used when spawning the
                process.
        """

        self._entered_input: list[ str ] = entered_input
        self._op_session_callbacks: PersistentSessionCallbacks = op_session_callbacks
        self._process_execution: ProcessExecution
        self._python_exe_path: str = python_exe_path
        self._run_state: str = run_state
        self._script_info: ScriptInfo = script_info
        self._row_id: str = ''


    @property
    def row_id( self ) -> str:
        """ Return the tree view row id associated with the running script.

        Returns:
            (str): Tree view row identifier used for UI updates.
        """

        return self._row_id


    @row_id.setter
    def row_id( self, value: str ) -> None:
        """ Store the tree view row id used to route UI updates.

        Args:
            value (str): Tree view row identifier for the session.
        """

        self._row_id = value


    def _on_completion( self, exit_code: int ) -> None:
        """ Handle process completion and publish the final state.

        Args:
            exit_code (int): Exit code returned by the process.
        """

        self._op_session_callbacks.update_state( self._row_id, ExecutionState.CLOSED )

        if exit_code != 0:
            self._op_session_callbacks.update_error( self._row_id, _( 'Script ended with exit code: {e}' ).format( e = exit_code ) )


    def _on_error( self, line_str: str ) -> None:
        """ Handler for errors occuring in process

        Args:
            line_str (str): Error line
        """

        self._op_session_callbacks.update_error( self._row_id, line_str )


    def _on_output( self, line_str: str ) -> None:
        """ Handler for output from the process

        Args:
            line_str (str): Output line from the process
        """

        if  '__API_START__' in line_str:
            self._parse_api_message( line = line_str )

        else:
            self._op_session_callbacks.update_output( self._row_id, line_str )


    def _parse_api_message( self, line: str ) -> None:
        """ Parse embedded API messages emitted on standard output.

        Args:
            line (str): Output line that may contain a framed API message.

        Raises:
            json.JSONDecodeError: If the embedded JSON payload is malformed.
        """

        match: re.Match[ str ] | None = re.search( r'__API_START__(.+?)__API_END__', string = line )

        if match is None:

            return

        try:
            api_msg = json.loads( match.group( 1 ) )

            if api_msg[ 'type' ] == 'progress':
                self._op_session_callbacks.update_progress( self._row_id, api_msg.get( 'data' ).get( 'percent' ) )

            elif api_msg[ 'type' ] == 'status':
                self._op_session_callbacks.update_status( self._row_id, api_msg.get( 'data' ).get( 'set' ) )

            elif api_msg[ 'type' ] == 'state':
                state =  api_msg.get( 'data' ).get( 'set' )

                if state.lower() == 'paused':
                    state = state + '_by_script'

                self._op_session_callbacks.update_state( self._row_id, state )


        except json.JSONDecodeError as e:

                pass


    def run_script( self ) -> subprocess.Popen | None:
        """ Start the persistent script process and begin monitoring it.

        Returns:
            (subprocess.Popen): Started process object for the running script.
        """

        self._process_execution = ProcessExecution( script_info = self._script_info,
                                                    python_exe_path = self._python_exe_path,
                                                    on_output = self._on_output,
                                                    on_error = self._on_error,
                                                    on_completion = self._on_completion )

        self.current_process = self._process_execution.create_process( run_input = self._entered_input,
                                                                      persistent = True,
                                                                      run_state = self._run_state,
                                                                      monitor_completion = True )

        return self.current_process
