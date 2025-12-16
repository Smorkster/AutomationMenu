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
from typing import TYPE_CHECKING, Any, Callable, Generator

if TYPE_CHECKING:
    from automation_menu.models.application_state import ApplicationState

import queue
import threading

from contextlib import contextmanager
from psutil import NoSuchProcess, Process
from queue import Queue
from threading import Lock

from automation_menu.core.script_runner import ScriptRunner
from automation_menu.models.application_state import ApplicationState
from automation_menu.models.enums import OutputStyleTags
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.ui.main_window import AutomationMenuWindow


class ScriptExecutionManager:
    def __init__( self, output_queue: Queue, app_state: ApplicationState ) -> None:
        """ Provides a contextmanager for running a script

        Args:
            output_queue (Queue): The queue gathering script output
            app_state (ApplicationState): General state of application
        """

        self._output_queue: Queue = output_queue
        self.app_state: ApplicationState = app_state
        self.current_runner: ScriptRunner | None = None
        self._lock: Lock = threading.Lock()
        self._paused: bool = False


    @contextmanager
    def create_runner( self ) -> Generator[ Any, Any, Any ]:
        """ Contextmanager taking care of runner bootup and cleanup """

        with self._lock:
            if self.current_runner is not None:
                raise RuntimeError( 'Another script is running, only one allowed at a time.' )

            runner: ScriptRunner = ScriptRunner( output_queue = self._output_queue, app_state = self.app_state, exec_manager = self )
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
            pid: int = self.current_runner.current_process.pid
            process: Process = psutil.Process( pid )

            print( f'DEBUG: Process status before: { process.status() }')

            process.suspend()

            print( f'DEBUG: Process status after: { process.status() }')

            # Check for children
            children: list[ Process ] = process.children( recursive = True )
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
            pid: int = self.current_runner.current_process.pid
            process: Process = psutil.Process( pid )

            print( f'DEBUG: Process status before: { process.status() }')

            process.resume()

            print( f'DEBUG: Process status after: { process.status() }')

            # Check for children
            children: list[ Process ] = process.children( recursive = True )
            print( f'DEBUG: Child processes: { len( children ) }')

            for child in children:
                print( f'  - Child PID { child.pid }: { child.name() } - { child.status() }' )
                child.resume()  # Resume children too!
                print( f'  - { child.status() }' )

            self._paused = True

            return True

        except NoSuchProcess:

            return False


    def run_script_async( self, *, script_info: ScriptInfo, main_window: AutomationMenuWindow, api_callbacks: dict, enable_stop_button_callback: Callable, enable_pause_button_callback: Callable, stop_pause_button_blinking_callback: Callable, run_input: list[ str ], on_finished: Callable = None, ) -> None:
        """ Launch a script for execution in a background thread.

        This method prepares UI state, spawns a worker thread, and starts the
        execution of a script without blocking the main Tkinter event loop.
        It is intended for script runs initiated directly from the UI.

        The actual execution logic is delegated to the execution manager;
        this method primarily acts as an orchestration layer between UI,
        execution control, and callback handling.

        Args:
            script_info (ScriptInfo):
                Metadata and configuration for the script to execute,
                including file path, parameters, and ScriptInfo-block settings.

            main_window (AutomationMenuWindow):
                Reference to the main application window. Used for UI state
                updates such as minimize-on-run behavior and widget visibility.

            api_callbacks (dict):
                Mapping of API callback names to callables. These callbacks
                are invoked by the output controller when scripts emit
                API messages (e.g. progress updates, status changes).

            enable_stop_button_callback (Callable):
                UI callback used to enable the "Stop script" button once
                execution has started.

            enable_pause_button_callback (Callable):
                UI callback used to enable the "Pause / Resume" button when
                the running script supports pausing or hits a breakpoint.

            stop_pause_button_blinking_callback (Callable):
                UI callback used to stop the blinking animation of the pause
                button when execution resumes or finishes.

            run_input (list[ str ]):
                List of command-line style arguments passed to the script.
                Typically built from user input or pre-set sequence parameters.

            on_finished (Callable):
                Optional callback invoked after the script has completed,
                regardless of success, failure, or manual termination.
                Commonly used to restore UI state.
        """

        import threading

        def sync_caller() -> None:
            """ Async worker for script execution """

            exec_item, exit_code, terminated = self.run_script_sync( script_info = script_info, main_window = main_window, api_callbacks = api_callbacks, enable_stop_button_callback = enable_stop_button_callback, enable_pause_button_callback = enable_pause_button_callback, stop_pause_button_blinking_callback = stop_pause_button_blinking_callback, run_input = run_input )

            if on_finished:
                on_finished( exec_item, exit_code, terminated )

        threading.Thread( sync_caller, daemon = True ).start()


    def run_script_sync( self, script_info: ScriptInfo, main_window: AutomationMenuWindow, api_callbacks: dict, enable_stop_button_callback: Callable, enable_pause_button_callback: Callable, stop_pause_button_blinking_callback: Callable, run_input: list[ str ] ) -> None:
        """ Launch a script and wait until execution completes.

        This method executes a script synchronously in the current thread.
        It starts the script process, sets up output and control callbacks,
        and blocks until the process finishes or is manually terminated.

        This method MUST NOT be called from the Tkinter main thread, as it
        will block until execution completes. It is intended to be used:
        - From a background thread when running a single script
        - Directly from a sequence runner thread for step-by-step execution

        All low-level process handling, output capture, pause/stop control,
        and execution history tracking are handled internally by the
        execution manager and ScriptRunner.

        Args:
            script_info (ScriptInfo):
                Metadata and configuration for the script to execute,
                including file path, ScriptInfo-block settings, and permissions.

            main_window (AutomationMenuWindow):
                Reference to the main application window, used for UI-related
                operations such as minimize-on-run behavior and widget state
                management.

            api_callbacks (dict):
                Mapping of API callback names to callables. These callbacks
                are triggered by the output controller when the running
                script emits API instructions (e.g. progress updates).

            enable_stop_button_callback (Callable):
                Callback used to enable the "Stop script" button once the
                script process has been started.

            enable_pause_button_callback (Callable):
                Callback used to enable the "Pause / Resume" button if the
                running script supports pausing or hits a breakpoint.

            stop_pause_button_blinking_callback (Callable):
                Callback used to stop pause-button blinking when execution
                resumes or finishes.

            run_input (list[str]):
                List of command-line style arguments passed to the script,
                typically collected from user input or sequence presets.
        """

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

            exit_code: int = runner._exec_item.exit_code
            terminated: bool = runner._terminated

        return runner._exec_item, exit_code, terminated


    def stop_current_script( self ) -> None:
        """ Stop/terminate the currently running script """

        with self._lock:
            if self.current_runner:
                self.current_runner.terminate()
