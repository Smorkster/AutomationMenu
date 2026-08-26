"""
A worker module for starting execution of script

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

import asyncio
import os
import psutil
import subprocess
import threading

from pathlib import Path
from queue import Queue
from tkinter import Tk
from typing import TYPE_CHECKING, Callable

from automation_menu.core.process_execution import ProcessExecution

if TYPE_CHECKING:
    from automation_menu.core.script_execution_manager import ScriptExecutionManager

from automation_menu.api.script_api import MESSAGE_END, MESSAGE_START
from automation_menu.models.application_state import ApplicationState
from automation_menu.models.enums import OutputStyleTags, SysInstructions
from automation_menu.models.exechistory import ExecHistory
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.utils.screenshot import take_screenshot


class OneTimeScriptRunner:
    def __init__( self, output_queue: Queue, app_state: ApplicationState, exec_manager: ScriptExecutionManager, error_reporter: Callable ) -> None:
        """" A script runner, managing bootup, process output and termination

        Args:
            output_queue (Queue): Queue for gathering output data
            app_state (ApplicationState): General state of application
            exec_manager (ScriptExecutionManager): Running manager to handle context for script process
            error_reporter (Callable): Function to report if a script fails
        """

        self._output_queue: Queue = output_queue
        self.app_state: ApplicationState = app_state
        self.script_execution_manager: ScriptExecutionManager = exec_manager
        self._error_reporter: Callable = error_reporter

        self.main_window = None
        self.current_process: subprocess.Popen
        self._exec_item: ExecHistory
        self._script_info: ScriptInfo
        self._terminated: bool = False
        self._run_state: str = app_state.run_state


    def _collect_error_info( self, error: str ) -> None:
        """ Gather error info to send to script developer

        Args:
            error (str): Error message
        """

        self._output_queue.put( { 'line': error,
                                 'tag': OutputStyleTags.SYSERROR,
                                 'finished': True,
                                 'exec_item': self._exec_item } )
        ss_path: Path = Path()

        if self.app_state.settings.send_mail_on_error:
            if self.app_state.settings.include_ss_in_error_mail:
                if self.main_window is None:
                    pass

                else:
                    ss_path = take_screenshot( root_window = self.main_window, script_info = self._script_info, file_name_prefix = str( self.app_state.secrets.get( 'error_ss_prefix' ) ) )

            from automation_menu.utils.localization import _

            try:
                self._error_reporter( app_state = self.app_state, error_msg = error, script_info = self._script_info, screenshot = ss_path )

                self._output_queue.put( { 'line': _( 'Mail sent' ),
                                         'tag': OutputStyleTags.SYSINFO,
                                         'exec_item': self._exec_item } )

            except Exception as e:
                self._output_queue.put( { 'line': _( 'Could not send error message to developer {e}' ).format( e = str( e ) ),
                                         'tag': OutputStyleTags.SYSERROR,
                                         'exec_item': self._exec_item } )


    def _is_breakpoint_line( self, line: str ) -> int:
        """ Verify if a line from the output, corresponds with a breakpoint has occured in the running script

        Args:
            line (str): Output line to check

        Returns:
            (bool): True if line corresponds with breakpoint info message
        """

        import re

        if self._script_info.filename.endswith( '.py' ):
            res = re.search( r'^.*\((?P<l>.*?)\)<module>\(\)', line.lower() )

            return int( res.group('l') ) if res else -1

        return re.search( 'At .*:{l}', line ) is not None


    def _on_completion( self, return_code: int | None ) -> None:
        """ Publish the final execution result and reset transient UI state.

        Args:
            return_code (int | None): Exit code from the completed process, or None
                if completion could not be determined.
        """

        if return_code is None:

            return

        from automation_menu.utils.localization import _

        self._exec_item.set_exit_code( exit_code = return_code )

        if self._terminated:
            self._exec_item.set_terminated()
            self._output_queue.put( { 'line': _( 'Script terminated' ),
                                     'tag': OutputStyleTags.SYSINFO,
                                     'finished': True,
                                     'exec_item': self._exec_item } )

        elif return_code == 0:
            self._output_queue.put( { 'line': _( 'Script completed successfully' ),
                                     'tag': OutputStyleTags.SUCCESS,
                                     'finished': True,
                                     'exec_item': self._exec_item } )

        else:
            self._output_queue.put( { 'line':_( 'Script failed with exit code {err}' ).format( err = return_code ),
                                     'tag': OutputStyleTags.SYSERROR,
                                     'finished': True,
                                     'exec_item': self._exec_item } )

        self.api_callbacks[ 'update_progress' ]( 0 )
        self.api_callbacks[ 'hide_progress' ]()
        self.api_callbacks[ 'clear_status' ]()
        self.script_execution_manager._paused = False


    def _on_error( self, line_str: str | None ) -> None:
        """ Route stderr output to the execution output queue.

        Args:
            line_str (str | None): Error output line read from the process.
        """

        from automation_menu.utils.localization import _

        if line_str is None:

            return

        line_nr: int = self._is_breakpoint_line( line_str )
        _in_breakpoint: bool = False
        tag: OutputStyleTags = OutputStyleTags.ERROR

        if line_nr > 0:
            _in_breakpoint = self._run_state != 'vscode' or True

        self._output_queue.put( { 'line': line_str,
                                 'tag': tag,
                                 'breakpoint': _in_breakpoint,
                                 'exec_item': self._exec_item } )


    def _on_output( self, line: str | None ) -> None:
        """ Route stdout output or breakpoint messages to the output queue.

        Args:
            line (str | None): Standard output line read from the process.
        """

        if line is None:

            return

        from automation_menu.utils.localization import _

        line_nr: int = self._is_breakpoint_line( line )
        _in_breakpoint: bool = False
        tag: OutputStyleTags = OutputStyleTags.INFO

        if line_nr > 0:
            _in_breakpoint = self._run_state != 'vscode' or True
            line = _( 'A breakpoint occured in the script at row {line_nr}. Click \'Continue\' to reactivate script.' ).format( line_nr =  line_nr - 1 )
            tag = OutputStyleTags.SYSINFO

        self._output_queue.put( { 'line': line,
                                 'tag': tag,
                                 'breakpoint': _in_breakpoint,
                                 'exec_item': self._exec_item } )


    def get_exec_item( self ) -> ExecHistory:
        """ Return the execution history

        Returns:
            (ExecHistory): Current ExecHistory item
        """

        return self._exec_item


    def get_exit_code( self ) -> int:
        """ Return exit code of process for this runner

        Returns:
            (int): Exit code from process execution
        """

        return self._exec_item.exit_code


    def get_run_state( self ) -> str:
        """ Get the current runstate of application

        Returns:
            (str): Current run state
        """

        return self._run_state


    def run_script( self, script_info: ScriptInfo, main_window: Tk, api_callbacks: dict, enable_stop_button_callback: Callable, enable_pause_button_callback: Callable, stop_pause_button_blinking_callback: Callable, run_input: list[ str ] ) -> None:
        """ Start process to run selected script

        Args:
            script_info (ScriptInfo): Script info gathered from the scripts info block
            main_window (Tk): The main window
            api_callbacks (dict): Dictionary for API callbacks
            enable_stop_button_callback (Callable): A callback function for enabling the stop script button
            enable_pause_button_callback (Callable): A callback function for enabling the pause/resume script button
            stop_pause_button_blinking_callback (Callable): A callback function for stopping any current button blinking
            run_input (list[ str ]): List of input arguments to send the script
        """

        from automation_menu.utils.localization import _

        self._script_info = script_info
        self.main_window = main_window
        self.api_callbacks = api_callbacks
        self.run_input = run_input

        error_line: str = ''

        try:
            self._exec_item = ExecHistory( script_info = self._script_info )
            line: str = _( 'Starting \'{file}\'' ).format( file = self._script_info.get_attr( 'synopsis' ) )
            self._output_queue.put( { 'line': line,
                                     'tag': OutputStyleTags.SYSINFO,
                                     'exec_item': self._exec_item } )

            enable_stop_button_callback()
            enable_pause_button_callback()

            if self._run_state == 'free':

                pass

            elif self._run_state == 'vscode':
                self._output_queue.put( { 'line': _( 'Running in: \'{a}\', application can not handle debugging.' ).format( a = self._run_state ),
                                         'tag': OutputStyleTags.SYSINFO,
                                         'exec_item': self._exec_item } )

            self._process_execution = ProcessExecution( script_info = self._script_info,
                                                       python_exe_path = self.app_state.python_exe_path,
                                                       on_output = self._on_output,
                                                       on_error = self._on_error,
                                                       on_completion = self._on_completion )
            self.current_process = self._process_execution.create_process( run_input = self.run_input,
                                                                          run_state = self._run_state,
                                                                          monitor_completion = False )

            return_code = self.current_process.wait()
            self._on_completion( return_code = return_code )

        except subprocess.SubprocessError as e:
            error_line = _( 'Subprocess error {error}' ).format( error = e )

        except Exception as e:
            error_line = _( 'Unexpected error {error}' ).format( error = e )

        finally:
            stop_pause_button_blinking_callback()

        if len( error_line ) > 0:
            self._collect_error_info( error = error_line )


    def send_api_response( self, response: str ) -> bool:
        """ Send the API response to the script stdin

        Args:
            response (str): String formated response to send

        Returns:
            (bool): True if API response was successful
        """

        if self.current_process is None or self.current_process.stdin is None:

            return False

        msg: str = f'{ MESSAGE_START }{ response }{ MESSAGE_END }\n'

        try:
            self.current_process.stdin.write( msg )
            self.current_process.stdin.flush()

            return True

        except:

            return False


    def terminate( self ) -> None:
        """ Force the running process to terminate """

        def _process_reaper( p: subprocess.Popen ) -> None:
            """ Find and end any child process

            Args:
                p (subprocess.Popen): Process referense to kill
            """

            children: list[ psutil.Process ] = psutil.Process( p.pid ).children( recursive = True )

            for child in children:
                child.kill()

            p.kill()


        if self.current_process:
            from automation_menu.utils.localization import _
            line: str = ''

            try:
                self._terminated = True
                self._output_queue.put( SysInstructions.PROCESSTERMINATED )
                _process_reaper( self.current_process )

            except subprocess.CalledProcessError as e:
                line = _( 'Termination - CalledProcessError: {e}' ).format( e = str( e ) )
                _process_reaper( self.current_process )

            except subprocess.SubprocessError as e:
                line = _( 'Termination - SubprocessError: {e}' ).format( e = str( e ) )
                _process_reaper( self.current_process )

            except Exception as e:
                line = _( 'Termination - Exception: {e}' ).format( e = str( e ) )
                _process_reaper( self.current_process )

            if len( line ) > 0:
                self._output_queue.put( { 'line': line,
                                         'tag': OutputStyleTags.SYSERROR,
                                         'exec_item': self._exec_item } )


    def was_terminated( self ) -> bool:
        """ Was the process manually terminated

        Returns:
            (bool): True if execution was successful
        """

        return self._terminated
