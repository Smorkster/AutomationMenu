import asyncio
from queue import Queue
import subprocess
import threading

from contextlib import contextmanager
from typing import Callable, Optional

from automation_menu.core.state import ApplicationState
from automation_menu.models import ScriptInfo


class ScriptExecutionManager:
    def __init__( self, output_queue, app_state ):
        self._output_queue = output_queue
        self.app_state = app_state
        self.current_runner: Optional[ 'ScriptRunner' ] = None
        self._lock = threading.Lock()

    @contextmanager
    def create_runner( self ):

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
                'finished': True
            } )
            raise

        finally:
            with self._lock:
                if self.current_runner == runner:
                    self.current_runner = None

    def is_running( self ) -> bool:
        with self._lock:
            return self.current_runner is not None

    def stop_current_script( self ):
        with self._lock:
            if self.current_runner:
                self.current_runner.terminate()

class ScriptRunner:
    def __init__( self, output_queue, app_state, exec_manager ):
        self._output_queue: Queue = output_queue
        self.app_state: ApplicationState = app_state
        self.script_execution_manager: ScriptExecutionManager = exec_manager

        self.current_process: Optional[ subprocess.Popen ] = None
        self._tasks = []
        self._script_info = None
        self._in_breakpoint = False
        self._terminated = False

    def run_script( self, script_info: ScriptInfo, enable_stop_button_callback: Callable ):
        from automation_menu.utils.localization import _

        self._script_info = script_info
        try:
            self.current_process = self._create_process( script_info )

            enable_stop_button_callback()

            self.stdout = threading.Thread( target = self._read_stdout(), daemon = True, name = f'{ script_info.filename }_stdout' ).start()
            self.stderr = threading.Thread( target = self._read_stderr(), daemon = True, name = f'{ script_info.filename }_stderr' ).start()
            self.monitor = threading.Thread( target = self._read_monitor_completion(), daemon = True, name = f'{ script_info.filename }_stdmonitor' ).start()
            self.current_process.wait()

        except subprocess.SubprocessError as e:
            self._output_queue.put( {
                'line': _( 'Subprocess error {error}' ).format( error = str( e ) ),
                'tag': 'suite_error',
                'finished': True
            } )

        except Exception as e:
            self._output_queue.put( {
                'line': _( 'Unexpected error {error}' ).format( error = str( e ) ),
                'tag': 'suite_error',
                'finished': True
            } )

    def _create_process( self, script_info ):
        from automation_menu.utils.localization import _

        line = _( 'Starting \'{file}\'' ).format( file = script_info.Synopsis )
        self._output_queue.put( {
            'line': line,
            'tag': 'suite_sysinfo'
        } )

        if script_info.filename.endswith( '.py' ):
            return subprocess.Popen(
                args = [ 'python', str( script_info.fullpath ) ],
                stdout = asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE,
                stdin = asyncio.subprocess.PIPE,
                text = True
            )

        elif script_info.filename.endswith( '.ps1' ):
            return subprocess.Popen(
                args = [ 'powershell.exe', str( script_info.fullpath ) ],
                stdout = asyncio.subprocess.PIPE,
                stderr = asyncio.subprocess.PIPE,
                stdin = asyncio.subprocess.PIPE,
                text = True
            )

    def terminate( self ):
        if self.current_process:
            from automation_menu.utils.localization import _
            line = ''

            try:
                self._terminated = True
                self._output_queue.put( 'ProcessTerminated' )
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
                    'tag': 'suite_error'
                } )


    def _read_stdout( self ):
        """ """

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
                    'breakpoint': True
                } )
            else:
                self._output_queue.put( {
                    'line': line_str.rstrip(),
                    'tag': 'suite_info'
                } )

    def _read_stderr( self ):
        """ """

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
                'tag': 'suite_error'
            } )

    def _read_monitor_completion( self ):
        """ """

        from automation_menu.utils.localization import _

        return_code = self.current_process.wait()

        if self._terminated:
            self._output_queue.put( {
                'line': _( 'Script terminated' ),
                'tag': 'suite_sysinfo'
            } )

        elif return_code == 0:
            self._output_queue.put( {
                'line': _( 'Script completed successfully' ),
                'tag': 'suite_success'
            } )

        else:
            self._output_queue.put( {
                    'line':_( 'Script failed with exit code {err}' ).format( err = return_code ),
                    'tag': 'suite_error',
                    'finished': True
            } )

    def _is_breakpoint_line( self, line: str ) -> bool:
        """ """

        import re

        return re.search( r'^.*\((.*)\)<module>\(\)', line.lower() ) or re.search( 'At .*:{l}', line )

