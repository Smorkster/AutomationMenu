"""
Create subprocesses and stream their output back to the application.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


import asyncio
import os
import subprocess
import threading

from typing import Callable

from automation_menu.models.scriptinfo import ScriptInfo


class ProcessExecution:
    """ Wrap subprocess creation together with stdout and stderr monitoring. """

    def __init__( self, script_info: ScriptInfo, python_exe_path: str, on_output: Callable, on_error: Callable, on_completion: Callable ) -> None:
        """ Store process metadata and callbacks used during execution.

        Args:
            script_info (ScriptInfo): Metadata for the script being executed.
            python_exe_path (str): Path to the Python interpreter used for Python
                scripts.
            on_output (Callable): Callback invoked for each stdout line.
            on_error (Callable): Callback invoked for each stderr line.
            on_completion (Callable): Callback invoked when the process exits.
        """

        self._script_info: ScriptInfo = script_info
        self._python_exe_path: str = python_exe_path
        self._process_started: threading.Event = threading.Event()
        self._terminated: bool = False

        self._on_output: Callable = on_output
        self._on_error: Callable = on_error
        self._on_completion: Callable = on_completion


    def _monitor_completion( self ) -> None:
        """ Wait for script process to finish and inform when """

        from automation_menu.utils.localization import _

        self._process_started.wait()
        p: subprocess.Popen = self.current_process

        if not p:

            return

        return_code: int = p.wait()
        self._on_completion( return_code )


    def _read_stderr( self ) -> None:
        """ Monitor standard error output from running process """

        self._process_started.wait()

        if self.current_process is None or not self.current_process.stderr:

            return

        while True:
            try:
                line: str = self.current_process.stderr.readline()

            except:

                break

            if not line:

                break

            line_str: str = line.decode() if isinstance( line, bytes ) else line
            self._on_error( line_str )


    def _read_stdout( self ) -> None:
        """ Monitor standard output from running process """

        self._process_started.wait()

        if self.current_process is None or not self.current_process.stdout:

            return

        while True:
            try:
                line: str = self.current_process.stdout.readline()

            except:

                break

            if not line:

                break

            line_str: str = line.decode() if isinstance( line, bytes ) else line
            self._on_output( line_str.rstrip() )


    def create_process( self, run_input: list[ str ], persistent: bool = False, run_state: str = 'free', monitor_completion: bool = True ) -> subprocess.Popen:
        """ Create and start a process to execute script

        Args:
            run_input (list[str]): Input entered before script start
            persistent (bool): True if this will start a persistent script
            run_state (str): State in which python will run (debug or not)
            monitor_completion (bool): True if completion should be monitored directly (used for persistent scripts)

        Returns:
            (subprocess.Popen): Newly created process
        """

        from automation_menu.utils.localization import _

        args: list[ str ] = []
        current_env: dict[ str, str ] = os.environ.copy()
        flags: int = 0

        if self._script_info.get_attr( 'filename' ).endswith( '.py' ):
            current_env[ 'PYTHONBREAKPOINT' ] = 'pdb.set_trace'
            current_env[ 'PYTHONUNBUFFERED' ] = '1'
            current_env[ 'PYTHONIOENCODING' ] = 'utf-8'

            args.append( self._python_exe_path )

        elif self._script_info.get_attr( 'filename' ).endswith( '.ps1' ):
            args.append( 'powershell.exe' )

            if persistent:
                args.extend( [ '-NoProfile', '-WindowStyle Hidden' ] )

        if persistent:
            flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS | subprocess.CREATE_NO_WINDOW

            if run_state == 'vscode':
                flags = flags | subprocess.CREATE_BREAKAWAY_FROM_JOB

            args[ 0 ] = args[ 0 ].replace( 'python.exe', 'pythonw.exe' )

        args.append( str( self._script_info.get_attr( 'fullpath' ) ) )
        args.extend( run_input )

        threading.Thread( target = self._read_stdout,
                         daemon = True,
                         name = f'{ self._script_info.filename }_stdout' ).start()
        threading.Thread( target = self._read_stderr,
                         daemon = True,
                         name = f'{ self._script_info.filename }_stderr' ).start()

        if monitor_completion:
            threading.Thread( target = self._monitor_completion,
                            daemon = True,
                            name = f'{ self._script_info.filename }_stdmonitor' ).start()

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = subprocess.SW_HIDE

        self.current_process = subprocess.Popen( args = args,
                                                startupinfo = startupinfo,
                                                stdout = asyncio.subprocess.PIPE,
                                                stderr = asyncio.subprocess.PIPE,
                                                stdin = asyncio.subprocess.PIPE,
                                                text = True,
                                                shell = False,
                                                encoding = 'utf-8',
                                                creationflags = flags,
                                                errors = 'replace',
                                                env = current_env )

        self._process_started.set()

        return self.current_process