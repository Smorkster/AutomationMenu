"""
A manager module for executing script with a contextmanager
Use as ScriptExecutionManagare and not ScriptRunner seperately

Author: Smorkster
GitHub:
License: MIT
Version: 1.0.0
Created: 2025-09-25
"""

import asyncio
from queue import Queue
import queue
import subprocess
import threading

from contextlib import contextmanager
from tkinter import Tk
from typing import Callable, Optional

from automation_menu.core.state import ApplicationState
from automation_menu.models import ExecHistory, ScriptInfo, SysInstructions
from automation_menu.utils.email_handler import report_script_error
from automation_menu.utils.screenshot import take_screenshot


class ScriptExecutionManager:
    def __init__( self, output_queue: queue.Queue, app_state: ApplicationState ) -> None:
        """ Provides a contextmanager for running a script

        Args:
            output_queue (queue.Queue): The queue gathering script output
            app_state (ApplicationState): General state of application
        """

        self._output_queue = output_queue
        self.app_state = app_state
        self.current_runner: Optional[ 'ScriptRunner' ] = None
        self._lock = threading.Lock()


    @contextmanager
    def create_runner( self ):
        """ Contextmanager taking care of runner bootup and cleanup """

        with self._lock:
            if self.current_runner is not None:
                raise RuntimeError( 'Another script is running, only one allowed at a time.' )

            runner = ScriptRunner( output_queue = self._output_queue, app_state = self.app_state, exec_manager = self )
            self.current_runner = runner

        try:
            yield runner

        except Exception as e:
            self._output_queue.put( {
                'line': 'Exception ❗: {error}'.format( error = str( e ) ),
                'tag': 'suite_error',
                'finished': True,
                'exec_item': runner._exec_item
            } )
            raise

        finally:
            with self._lock:
                if self.current_runner == runner:
                    self.current_runner = None


    def is_running( self ) -> bool:
        """ Verify if a script is running

        Returns:
            (bool): True if a runner is currently executing
        """

        with self._lock:
            return self.current_runner is not None


    def stop_current_script( self ) -> None:
        """ Stop/terminate the currently running script """

        with self._lock:
            if self.current_runner:
                self.current_runner.terminate()


class ScriptRunner:
    def __init__( self, output_queue, app_state, exec_manager ):
        """" A script runner, managing bootup, process output and termination

        Args:
            output_queue (queue.Queue): Queue for gathering output data
            app_state (ApplicationSate): General state of application
            exec_manager (ScriptExecutionManager): Running manager to handle context for script process
        """

        self._output_queue: Queue = output_queue
        self.app_state: ApplicationState = app_state
        self.script_execution_manager: ScriptExecutionManager = exec_manager
        self.main_window = None

        self.current_process: Optional[ subprocess.Popen ] = None
        self._tasks = []
        self._script_info = None
        self._in_breakpoint = False
        self._terminated = False


    def run_script( self, script_info: ScriptInfo, enable_stop_button_callback: Callable, main_window: Tk ) -> None:
        """ Start process to run selected script

        Args:
            script_info (ScriptInfo): Script info gathered from the scripts info block
            enable_stop_button_callback (Callable): A callback function for enabling the stop script button
            main_window (Tk): The main window
        """

        from automation_menu.utils.localization import _

        self._script_info = script_info
        self.main_window = main_window
        line = ''

        try:
            self.current_process = self._create_process()

            enable_stop_button_callback()

            self.stdout = threading.Thread( target = self._read_stdout(), daemon = True, name = f'{ self._script_info.filename }_stdout' ).start()
            self.stderr = threading.Thread( target = self._read_stderr(), daemon = True, name = f'{ self._script_info.filename }_stderr' ).start()
            self.monitor = threading.Thread( target = self._read_monitor_completion(), daemon = True, name = f'{ self._script_info.filename }_stdmonitor' ).start()
            self.current_process.wait()

        except subprocess.SubprocessError as e:
            line = _( 'Subprocess error {error}' ).format( error = str( e ) )

        except Exception as e:
            line = _( 'Unexpected error {error}' ).format( error = str( e ) )

        if len( line ) > 0:
            self._collect_error_info( error = line )


    def _collect_error_info( self, error: str ) -> None:
        """ Gather error info to send to script developer

        Args:
            error (str): Error message
        """

        self._output_queue.put( {
            'line': error,
            'tag': 'suite_error',
            'finished': True,
            'exec_item': self._exec_item
        } )
        ss_path = ''

        if self.app_state.settings.send_mail_on_error:
            if self.app_state.settings.include_ss_in_error_mail:
                ss_path = take_screenshot( root_window = self.main_window, script = self._script_info, file_name_prefix = self.app_state.secrets.get( 'error_ss_prefix' ) )

            from automation_menu.utils.localization import _

            try:
                report_script_error( app_state = self.app_state, error_msg = error, script_info = self._script_info, screenshot = ss_path )

                self._output_queue.put( {
                    'line': _( 'Mail sent' ),
                    'tag': 'suite_sysinfo',
                    'exec_item': self._exec_item
                } )

            except Exception as e:
                self._output_queue.put( {
                    'line': _( 'Could not send error message to developer {e}' ).format( e = str( e ) ),
                    'tag': 'suite_sysinfo',
                    'exec_item': self._exec_item
                } )


    def _create_process( self ) -> None:
        """ Create and start a process to execute script """

        from automation_menu.utils.localization import _

        self._exec_item = ExecHistory( script_info = self._script_info )
        line = _( 'Starting \'{file}\'' ).format( file = self._script_info.Synopsis )
        self._output_queue.put( {
            'line': line,
            'tag': 'suite_sysinfo',
            'exec_item': self._exec_item
        } )

        if self._script_info.filename.endswith( '.py' ):
            return subprocess.Popen(
                args = [ 'python', str( self._script_info.fullpath ) ],
                stdout = asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE,
                stdin = asyncio.subprocess.PIPE,
                text = True
            )

        elif self._script_info.filename.endswith( '.ps1' ):
            return subprocess.Popen(
                args = [ 'powershell.exe', str( self._script_info.fullpath ) ],
                stdout = asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE,
                stdin = asyncio.subprocess.PIPE,
                text = True
            )


    def terminate( self ) -> None:
        """ Force the running process to terminate """

        if self.current_process:
            from automation_menu.utils.localization import _
            line = ''

            try:
                self._terminated = True
                self._output_queue.put( SysInstructions.PROCESSTERMINATED )
                self.current_process.kill()
                self.current_process.wait()

            except subprocess.SubprocessError as e:
                line = _( 'Termination - SubprocessError: {e}' ).format( e = str( e ) )
                self.current_process.kill()

            except subprocess.CalledProcessError:
                line = _( 'Termination - CalledProcessError: {e}' ).format( e = str( e ) )
                self.current_process.kill()

            except:
                line = _( 'Termination - Exception: {e}' ).format( e = str( e ) )
                self.current_process.kill()

            if len( line ) > 0:
                self._output_queue.put( {
                    'line': line,
                    'tag': 'suite_error',
                    'exec_item': self._exec_item
                } )


    def _read_stdout( self ) -> None:
        """ Monitor standard output from running process """

        from automation_menu.utils.localization import _

        while True:
            try:
                line = self.current_process.stdout.readline()

            except:
                break

            if not line:
                break

            line_str = line.decode() if isinstance( line, bytes ) else line
            line_nr = self._is_breakpoint_line( line_str )

            if line_nr:
                self._in_breakpoint = True
                self._output_queue.put( {
                    'line': _( 'A breakpoint occured in the script at row {line_nr}. Click \'Continue\' to reactivate script.' ).format( line_nr = line_nr ),
                    'tag': 'suite_sysinfo',
                    'breakpoint': True,
                    'exec_item': self._exec_item
                } )
            else:
                self._output_queue.put( {
                    'line': line_str.rstrip(),
                    'tag': 'suite_info',
                    'exec_item': self._exec_item
                } )


    def _read_stderr( self ) -> None:
        """ Monitor standard error output from running process """

        from automation_menu.utils.localization import _

        while True:
            try:
                line = self.current_process.stderr.readline()

            except:
                break

            if not line:
                break

            line_str = line.decode() if isinstance( line, bytes ) else line
            self._output_queue.put( {
                'line': line_str.rstrip(),
                'tag': 'suite_error',
                'exec_item': self._exec_item
            } )


    def _read_monitor_completion( self ) -> None:
        """ Wait for script process to finish and inform when """

        from automation_menu.utils.localization import _

        return_code = self.current_process.wait()

        if return_code == 0:
            self._output_queue.put( {
                'line': _( 'Script completed successfully' ),
                'tag': 'suite_success',
                'finished': True,
                'exec_item': self._exec_item
            } )

        else:
            if self._terminated:
                self._output_queue.put( {
                    'line': _( 'Script terminated' ),
                    'tag': 'suite_sysinfo',
                    'finished': True,
                    'exec_item': self._exec_item
                } )

            else:
                self._output_queue.put( {
                        'line':_( 'Script failed with exit code {err}' ).format( err = return_code ),
                        'tag': 'suite_sysinfo',
                        'finished': True,
                        'exec_item': self._exec_item
                } )


    def _is_breakpoint_line( self, line: str ) -> bool:
        """ Verify if a line from the output, corresponds with a breakpoint has occured in the running script

        Args:
            line (str): Output line to check

        Returns:
            (bool): True if line corresponds with breakpoint info message
        """

        import re

        return re.search( r'^.*\((.*)\)<module>\(\)', line.lower() ) or re.search( 'At .*:{l}', line )
