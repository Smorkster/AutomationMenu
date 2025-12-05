"""
A worker module for starting execution of script

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-09-25
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from automation_menu.core.script_execution_manager import ScriptExecutionManager

import asyncio
import psutil
import subprocess
import sys
import threading

from queue import Queue
from tkinter import Tk

from automation_menu.api.script_api import MESSAGE_END, MESSAGE_START
from automation_menu.models.application_state import ApplicationState
from automation_menu.models.enums import OutputStyleTags, SysInstructions
from automation_menu.models.exechistory import ExecHistory
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.utils.email_handler import report_script_error
from automation_menu.utils.screenshot import take_screenshot


class ScriptRunner:
    def __init__( self, output_queue: Queue, app_state: ApplicationState, exec_manager: ScriptExecutionManager ) -> None:
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


    def _collect_error_info( self, error: str ) -> None:
        """ Gather error info to send to script developer

        Args:
            error (str): Error message
        """

        self._output_queue.put( {
            'line': error,
            'tag': OutputStyleTags.SYSERROR,
            'finished': True,
            'exec_item': self._exec_item
        } )
        ss_path = ''

        if self.app_state.settings.send_mail_on_error:
            if self.app_state.settings.include_ss_in_error_mail:
                ss_path = take_screenshot( root_window = self.main_window, script_info = self._script_info, file_name_prefix = self.app_state.secrets.get( 'error_ss_prefix' ) )

            from automation_menu.utils.localization import _

            try:
                report_script_error( app_state = self.app_state, error_msg = error, script_info = self._script_info, screenshot = ss_path )

                self._output_queue.put( {
                    'line': _( 'Mail sent' ),
                    'tag': OutputStyleTags.SYSINFO,
                    'exec_item': self._exec_item
                } )

            except Exception as e:
                self._output_queue.put( {
                    'line': _( 'Could not send error message to developer {e}' ).format( e = str( e ) ),
                    'tag': OutputStyleTags.SYSERROR,
                    'exec_item': self._exec_item
                } )


    def _create_process( self ) -> None:
        """ Create and start a process to execute script """

        from automation_menu.utils.localization import _

        self._exec_item = ExecHistory( script_info = self._script_info )
        line = _( 'Starting \'{file}\'' ).format( file = self._script_info.get_attr( 'synopsis' ) )
        self._output_queue.put( {
            'line': line,
            'tag': OutputStyleTags.SYSINFO,
            'exec_item': self._exec_item
        } )

        exec_string = ''

        if self._script_info.get_attr( 'filename' ).endswith( '.py' ):
            exec_string = sys.executable

        elif self._script_info.get_attr( 'filename' ).endswith( '.ps1' ):
            exec_string = 'powershell.exe'

        return subprocess.Popen(
            args = [ exec_string, str( self._script_info.get_attr( 'fullpath' ) ) ] + self.run_input,
            stdout = asyncio.subprocess.PIPE,
            stderr = asyncio.subprocess.PIPE,
            stdin = asyncio.subprocess.PIPE,
            text = True,
            encoding = 'utf-8',
            errors = 'replace'
        )


    def _is_breakpoint_line( self, line: str ) -> bool:
        """ Verify if a line from the output, corresponds with a breakpoint has occured in the running script

        Args:
            line (str): Output line to check

        Returns:
            (bool): True if line corresponds with breakpoint info message
        """

        import re

        return re.search( r'^.*\((.*)\)<module>\(\)', line.lower() ) or re.search( 'At .*:{l}', line )


    def _read_monitor_completion( self ) -> None:
        """ Wait for script process to finish and inform when """

        from automation_menu.utils.localization import _

        return_code = self.current_process.wait()
        self._exec_item.set_exit_code( exit_code = return_code )

        if self._terminated:
            self._exec_item.set_terminated()
            self._output_queue.put( {
                'line': _( 'Script terminated' ),
                'tag': OutputStyleTags.SYSINFO,
                'finished': True,
                'exec_item': self._exec_item
            } )

        elif return_code == 0:
            self._output_queue.put( {
                'line': _( 'Script completed successfully' ),
                'tag': OutputStyleTags.SUCCESS,
                'finished': True,
                'exec_item': self._exec_item
            } )

        else:
            self._output_queue.put( {
                    'line':_( 'Script failed with exit code {err}' ).format( err = return_code ),
                    'tag': OutputStyleTags.SYSERROR,
                    'finished': True,
                    'exec_item': self._exec_item
            } )

        self.api_callbacks[ 'update_progress' ]( 0 )
        self.api_callbacks[ 'hide_progress' ]()
        self.api_callbacks[ 'clear_status' ]()
        self.script_execution_manager._paused = False


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
                'tag': OutputStyleTags.ERROR,
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
                    'tag': OutputStyleTags.SYSINFO,
                    'breakpoint': True,
                    'exec_item': self._exec_item
                } )
            else:
                self._output_queue.put( {
                    'line': line_str.rstrip(),
                    'tag': OutputStyleTags.INFO,
                    'exec_item': self._exec_item
                } )


    def run_script( self,
                    script_info: ScriptInfo,
                    main_window: Tk,
                    api_callbacks: dict,
                    enable_stop_button_callback: Callable,
                    enable_pause_button_callback: Callable,
                    stop_pause_button_blinking_callback: Callable,
                    run_input: list[ str ]
                  ) -> None:
        """ Start process to run selected script

        Args:
            script_info (ScriptInfo): Script info gathered from the scripts info block
            main_window (Tk): The main window
            api_callbacks (dict): Dictionary for API callbacks
            enable_stop_button_callback (Callable): A callback function for enabling the stop script button
            enable_pause_button_callback (Callable): A callback function for enabling the pause/resume script button
            stop_pause_button_blinking_callback (Callable): A callback function for stopping any current button blinking
        """

        from automation_menu.utils.localization import _

        self._script_info = script_info
        self.main_window = main_window
        self.api_callbacks = api_callbacks
        self.run_input = run_input
        line = ''

        try:
            self.current_process = self._create_process()

            enable_stop_button_callback()
            enable_pause_button_callback()

            self.stdout = threading.Thread( target = self._read_stdout(), daemon = True, name = f'{ self._script_info.filename }_stdout' ).start()
            self.stderr = threading.Thread( target = self._read_stderr(), daemon = True, name = f'{ self._script_info.filename }_stderr' ).start()
            self.monitor = threading.Thread( target = self._read_monitor_completion(), daemon = True, name = f'{ self._script_info.filename }_stdmonitor' ).start()

        except subprocess.SubprocessError as e:
            line = _( 'Subprocess error {error}' ).format( error = str( e ) )

        except Exception as e:
            line = _( 'Unexpected error {error}' ).format( error = str( e ) )

        finally:
            stop_pause_button_blinking_callback()

        if len( line ) > 0:
            self._collect_error_info( error = line )


    def send_api_response( self, response: str ) -> None:
        """ Send the API response the script stdin

        Args:
            response (str): String formated response to send
        """

        msg = f'{ MESSAGE_START }{ response }{ MESSAGE_END }\n'

        try:
            self.current_process.stdin.write( msg )
            self.current_process.stdin.flush()

        except:
            pass


    def terminate( self ) -> None:
        """ Force the running process to terminate """

        def _process_reaper( p: subprocess.Popen ) -> None:
            """ Find and end any child process """

            children = psutil.Process( p.pid ).children( recursive = True )

            for child in children:
                child.kill()

            p.kill()


        if self.current_process:
            from automation_menu.utils.localization import _
            line = ''

            try:
                self._terminated = True
                self._output_queue.put( SysInstructions.PROCESSTERMINATED )
                _process_reaper( self.current_process )

            except subprocess.SubprocessError as e:
                line = _( 'Termination - SubprocessError: {e}' ).format( e = str( e ) )
                _process_reaper( self.current_process )

            except subprocess.CalledProcessError:
                line = _( 'Termination - CalledProcessError: {e}' ).format( e = str( e ) )
                _process_reaper( self.current_process )

            except Exception as e:
                line = _( 'Termination - Exception: {e}' ).format( e = str( e ) )
                _process_reaper( self.current_process )

            if len( line ) > 0:
                self._output_queue.put( {
                    'line': line,
                    'tag': OutputStyleTags.SYSERROR,
                    'exec_item': self._exec_item
                } )
