"""
Run saved script sequences step by step using the execution manager.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

import queue
from tkinter import Tk
from typing import Callable

from automation_menu.core.script_execution_manager import ScriptExecutionManager
from automation_menu.core.one_time_script_runner import OneTimeScriptRunner
from automation_menu.models.enums import OutputStyleTags
from automation_menu.models.scriptinfo_not_loaded import ScriptInfoNotLoaded
from automation_menu.models.sequence import Sequence
from automation_menu.utils.build_run_args import build_run_args


def sequence_runner( sequence: Sequence, execution_mgr: ScriptExecutionManager, output_queue: queue.Queue, root: Tk, api_callbacks: dict, enable_stop: Callable, enable_pause: Callable, stop_pause: Callable ) -> None:
    """ Execute all steps in a sequence.

    Args:
        sequence (Sequence): Sequence to execute.
        execution_mgr (ScriptExecutionManager): Manager used to create script runners.
        output_queue (queue.Queue): Queue used to publish execution output and status messages.
        root (Tk): Root Tkinter window passed to script execution.
        api_callbacks (dict): Callback functions available to the running script.
        enable_stop (Callable): Callback used to enable the stop button.
        enable_pause (Callable): Callback used to enable the pause button.
        stop_pause (Callable): Callback used to stop pause-button blinking.
    """

    from automation_menu.utils.localization import _

    for step in sequence.steps:
        stop_sequence: bool = False
        exec_mgr = execution_mgr
        run_args: list[ str ] = build_run_args( pre_set_params = step.pre_set_parameters )
        run_success: int = 0
        runner: OneTimeScriptRunner | None = None
        output_item: dict[ str, object ] = {}

        try:
            if isinstance( step.script_info, ScriptInfoNotLoaded ):

                raise TypeError( _( 'Script not loaded' ) )

            with exec_mgr.create_runner() as runner:
                if runner is None:

                    raise ValueError( _( f'Couldn\'t initiate a runner for sequence ''{s}''' ).format( s = sequence.name ) )

                runner.run_script( script_info = step.script_info,
                                  main_window = root,
                                  api_callbacks = api_callbacks,
                                  enable_stop_button_callback = enable_stop,
                                  enable_pause_button_callback = enable_pause,
                                  stop_pause_button_blinking_callback = stop_pause,
                                  run_input = run_args )

                exit_code: int = runner.get_exit_code()
                terminated: bool = runner.was_terminated()
                effective_stop: bool = step.stop_on_error or sequence.stop_on_error

                if terminated:
                    # Manual stop, abort sequence
                    output_queue.put( { 'line': _( 'Aborted by user at step {i}' ).format( i = step.step_index ),
                                       'tag': OutputStyleTags.SYSINFO,
                                       'exec_item': runner._exec_item, } )

                    run_success = 1
                    stop_sequence = True

                elif exit_code != 0:
                    if effective_stop:
                        output_queue.put( { 'line': _( 'Stopped on error at step {i} (exit code: {e})' ).format( i = step.step_index, e = exit_code ),
                                           'tag': OutputStyleTags.SYSERROR,
                                           'exec_item': runner._exec_item, } )

                        run_success = 2
                        stop_sequence = True

                    else:
                        output_queue.put( { 'line': _( 'Step {i} failed (exit code {e})' ).format( i = step.step_index, e = exit_code ),
                                           'tag': OutputStyleTags.SYSWARNING,
                                           'exec_item': runner._exec_item, } )

                        run_success = 3

        except TypeError as e:

            output_item = { 'line': str( e ),
                           'tag': OutputStyleTags.SYSERROR,
                           'exec_item': getattr( runner, '_exec_item', None ) }

        except Exception as e:

            output_item = { 'line': _( 'Error in script \'{f}\', step {s} of {c}' ).format( f = step.script_info, s = step.step_index + 1, c = len( sequence.steps ) ),
                           'tag': OutputStyleTags.SYSERROR,
                           'exec_item': getattr( runner, '_exec_item', None ) }

        output_queue.put( output_item )

        if sequence.stop_on_error or step.stop_on_error:
            stop_sequence = True

        if stop_sequence:

            if run_success > 0 :
                output_queue.put( { 'line': _( 'Sequence stopped due to individual step error' ),
                                   'tag': OutputStyleTags.SYSWARNING,
                                   'exec_item': None } )

            break
