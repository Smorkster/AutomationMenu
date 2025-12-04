"""
A manager module for executing script with a contextmanager
Use as ScriptExecutionManagare and not ScriptRunner seperately

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-09-25
"""

from __future__ import annotations
from concurrent.futures import thread
from typing import TYPE_CHECKING, Any, Callable, Generator

from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.ui.main_window import AutomationMenuWindow

if TYPE_CHECKING:
    from automation_menu.models.application_state import ApplicationState

import queue
import threading

from contextlib import contextmanager
from psutil import NoSuchProcess

from automation_menu.core.script_runner import ScriptRunner
from automation_menu.models.application_state import ApplicationState
from automation_menu.models.enums import OutputStyleTags


class ScriptExecutionManager:
    def __init__( self, output_queue: queue.Queue, app_state: ApplicationState ) -> None:
        """ Provides a contextmanager for running a script

        Args:
            output_queue (queue.Queue): The queue gathering script output
            app_state (ApplicationState): General state of application
        """

        self._output_queue = output_queue
        self.app_state = app_state
        self.current_runner: ScriptRunner = None
        self._lock = threading.Lock()
        self._paused = False


    @contextmanager
    def create_runner( self ) -> Generator[ Any, Any, Any ]:
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
                'tag': OutputStyleTags.SYSERROR,
                'finished': True,
                'exec_item': runner._exec_item
            } )
            raise

        finally:
            with self._lock:
                if self.current_runner == runner:
                    self.current_runner = None


    def is_paused( self ) -> bool:
        """ Check if current script is paused """

        return self._paused


    def is_running( self ) -> bool:
        """ Verify if a script is running

        Returns:
            (bool): True if a runner is currently executing
        """

        with self._lock:
            return self.current_runner is not None and not self._paused


    def pause_current_script( self ) -> None:
        """ Pause the currently running script """

        import psutil

        try:
            pid = self.current_runner.current_process.pid
            process = psutil.Process( pid )

            print( f'DEBUG: Process status before: { process.status() }')

            process.suspend()

            print( f'DEBUG: Process status after: { process.status() }')

            # Check for children
            children = process.children( recursive = True )
            print( f'DEBUG: Child processes: { len( children ) }')
            for child in children:
                print( f'  - Child PID { child.pid }: { child.name() } - { child.status() }' )
                child.suspend()  # Suspend children too!
                print( f'  - { child.status() }' )

            self._paused = True
            return True

        except NoSuchProcess:
            return False


    def resume_current_script( self ) -> None:
        """ Resume execution of current script """

        import psutil

        try:
            pid = self.current_runner.current_process.pid
            process = psutil.Process( pid )

            print( f'DEBUG: Process status before: { process.status() }')

            process.resume()

            print( f'DEBUG: Process status after: { process.status() }')

            # Check for children
            children = process.children( recursive = True )
            print( f'DEBUG: Child processes: { len( children ) }')
            for child in children:
                print( f'  - Child PID { child.pid }: { child.name() } - { child.status() }' )
                child.resume()  # Resume children too!
                print( f'  - { child.status() }' )

            self._paused = True
            return True

        except NoSuchProcess:
            return False


    def run_script_sync( self, script_info: ScriptInfo, main_window: AutomationMenuWindow, api_callbacks: dict, enable_stop_button_callback: Callable, enable_pause_button_callback: Callable, stop_pause_button_blinking_callback: Callable, run_input: list[ str ] ) -> None:
        """ Launch  """

        with self.create_runner() as runner:
            runner.run_script(
                script_info = script_info,
                main_window = main_window,
                api_callbacks = api_callbacks,
                enable_stop_button_callback = enable_stop_button_callback,
                enable_pause_button_callback = enable_pause_button_callback,
                stop_pause_button_blinking_callback = stop_pause_button_blinking_callback,
                run_input = run_input,
            )

            runner.current_runner.wait()

            exit_code = runner._exec_item.exit_code
            terminated = runner._terminated

        return runner._exec_item, exit_code, terminated


    def run_script_async( self, *, script_info: ScriptInfo, main_window: AutomationMenuWindow, api_callbacks: dict, enable_stop_button_callback: Callable, enable_pause_button_callback: Callable, stop_pause_button_blinking_callback: Callable, run_input: list[ str ], on_finished: Callable = None, ) -> None:
        """ Launch script in async """

        import threading

        def sync_caller() -> None:
            """ Async worker for script execution """

            exec_item, exit_code, terminated = self.run_script_sync( script_info = script_info, main_window = main_window, api_callbacks = api_callbacks, enable_stop_button_callback = enable_stop_button_callback, enable_pause_button_callback = enable_pause_button_callback, stop_pause_button_blinking_callback = stop_pause_button_blinking_callback, run_input = run_input )

            if on_finished:
                on_finished( exec_item, exit_code, terminated )

        threading.Thread( sync_caller, daemon = True ).start()


    def stop_current_script( self ) -> None:
        """ Stop/terminate the currently running script """

        with self._lock:
            if self.current_runner:
                self.current_runner.terminate()
