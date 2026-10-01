"""
Test cases for PersistentExecutionSession

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


import datetime
import subprocess
import time
from typing import Callable, cast

import psutil
import pytest

from pathlib import Path
from psutil import NoSuchProcess, Process
from unittest.mock import Mock, patch

from automation_menu.models.enums import ExecutionState
from automation_menu.models.persistent_execution_session import PersistentExecutionSession
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.scriptmetadata import ScriptMetadata


class TestCreation:

    def test_create_new_session( self ) -> None:
        """ Verify that a session is created """

        smd: dict = { 'synopsis': 'S', 'author': 'a', 'description': 'D', 'state': 'Prod' }
        used_attributes = { 'fullpath': 'C:\\file_path.py', 'filename': 'file_path.py', 'scriptmeta': smd }
        script_info: ScriptInfo = ScriptInfo.from_dict( used_attributes )

        pes: PersistentExecutionSession = PersistentExecutionSession( id = 'temp', script_info = script_info, op_callbacks = Mock() )

        assert pes is not None


class TestUsage:

    @pytest.mark.parametrize( ( 'attr', 'val', 'no_runner' ),
                             [ pytest.param( 'progress', float( 1 ), False ),
                               pytest.param( 'progress', float( 1 ), True ),
                               pytest.param( 'row_id', 'r_id', False ),
                               pytest.param( 'row_id', 'r_id', True ),
                               pytest.param( 'session_id', 's_id', False ),
                               pytest.param( 'session_id', 's_id', True ),
                               pytest.param( 'script_info', ScriptInfo( filename = 'filename.py', fullpath = Path( 'C:\\path\\filename.py' ), scriptmeta = ScriptMetadata( synopsis = 'syn', author = 'auth' ) ), False ),
                               pytest.param( 'script_info', ScriptInfo( filename = 'filename.py', fullpath = Path( 'C:\\path\\filename.py' ), scriptmeta = ScriptMetadata( synopsis = 'syn', author = 'auth' ) ), True ),
                               pytest.param( 'state', ExecutionState.RUNNING, False ),
                               pytest.param( 'state', ExecutionState.RUNNING, True ),
                               pytest.param( 'status', 'status', False ),
                               pytest.param( 'status', 'status', True ) ], )
    def test_properties_set_and_report( self, attr: str, val: float | ExecutionState | ScriptInfo | str, no_runner: bool ) -> None:
        """ Test if property is correctly set and reported

        Args:
            attr (str): Name of attribute to test
            val (float|ExecutionState|ScriptInfo|str): Value to set
            no_runner (bool): Should a script runner be simulated
        """

        pes: PersistentExecutionSession = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._runner = None if no_runner else Mock()
        pes._row_id = 'row-1'

        with ( patch.object( pes, 'update_state' ) as update_state, patch.object( pes, 'update_status' ) as update_status ):

            pes.__setattr__( f'_{ attr }', val )

            assert getattr( pes, f'_{ attr }') == val

            setattr( pes, attr, val )

            assert getattr( pes, attr ) == val

            if attr == 'state':
                update_state.assert_called_once_with( 'row-1', val )

            else:
                update_state.assert_not_called()

            if attr == 'status':
                update_status.assert_called_once_with( 'row-1', val )

            else:
                update_status.assert_not_called()


    def test_getting_process_and_its_children( self ) -> None:
        """ Is psutil_process set, with associated children """

        pes: PersistentExecutionSession = PersistentExecutionSession.__new__( PersistentExecutionSession )
        process: Mock = Mock()
        children_list: list[ Mock ] = [ Mock(), Mock() ]

        process.children.return_value = children_list

        with patch( 'automation_menu.models.persistent_execution_session.Process',
                   return_value = process ) as process_class:
            pes._get_process_and_children( 123 )

            process_class.assert_called_once_with( 123 )
            process.children.assert_called_once_with( recursive = True )

            assert pes._psutil_process is process
            assert pes._psutil_children is children_list


    @pytest.mark.parametrize( ( 'times_out', 'expected_state', 'no_process' ),
                             [ ( False, ExecutionState.STOPPED, False ),
                              ( False, ExecutionState.STOPPED, True ),
                              ( True, ExecutionState.STOP_FAILED, False ),
                              ( True, ExecutionState.STOP_FAILED, True ) ] )
    def test_wait_for_process_to_quit( self, times_out: bool, expected_state: ExecutionState, no_process: bool ) -> None:
        """ Test that process will quit by itself

        Args:
            times_out (bool): True if wait should timeout
            expected_state (ExecutionState): Expected state after process quit
            no_process (bool): Should process be simulated
        """

        pes: PersistentExecutionSession = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._row_id = 'row-1'
        current_process = Mock()
        pes._runner = Mock()
        pes._runner.current_process = None if no_process else current_process

        if times_out:
            current_process.wait.side_effect = subprocess.TimeoutExpired( cmd = 'test.py',
                                                                         timeout = 5 )

        else:
            current_process.wait.return_value = 0

        with patch.object( pes, 'update_state' ) as update_state:
            pes._wait_stop()

            if no_process:
                current_process.assert_not_called()
                update_state.assert_not_called()

            else:
                current_process.wait.assert_called_once_with( timeout = 5 )
                update_state.assert_called_once_with( 'row-1', expected_state )


    @pytest.mark.parametrize( ( 'times_out', 'expected_state', 'no_process' ),
                             [ ( False, ExecutionState.STOPPED, False ),
                              ( False, ExecutionState.STOPPED, True ),
                              ( True, ExecutionState.FORCED_STOPPING_FAILED, False ),
                              ( True, ExecutionState.FORCED_STOPPING_FAILED, True ) ] )
    def test_wait_for_process_to_be_forced_to_stop( self, times_out: bool, expected_state: ExecutionState, no_process: bool ) -> None:
        """ Test that process will quit by itself

        Args:
            times_out (bool): True if wait should timeout
            expected_state (ExecutionState): Expected state after process quit
            no_process (bool): Should process be simulated
        """

        pes: PersistentExecutionSession = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._row_id = 'row-1'
        current_process = Mock()
        pes._runner = Mock()
        pes._runner.current_process = None if no_process else current_process

        if times_out:
            current_process.wait.side_effect = subprocess.TimeoutExpired( cmd = 'test.py',
                                                                         timeout = 5 )

        else:
            current_process.wait.return_value = 0

        with patch.object( pes, 'update_state' ) as update_state:
            pes._wait_forced_stop()

            if no_process:
                current_process.assert_not_called()
                update_state.assert_not_called()

            else:
                current_process.wait.assert_called_once_with( timeout = 5 )
                update_state.assert_called_once_with( 'row-1', expected_state )


    @pytest.mark.parametrize( 'no_process', [ True, False ] )
    def test_stopping_runner( self, no_process: bool ) -> None:
        """ Test that stopping a runner actually works

        Args:
            no_process (bool): True to test without a process registered
        """

        pes: PersistentExecutionSession = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._row_id = 'row-1'
        current_process = Mock()
        pes._runner = Mock()
        pes._runner.current_process = None if no_process else current_process

        with ( patch( 'automation_menu.models.persistent_execution_session.threading.Thread' ) as thread,
              patch.object( pes, 'update_state' ) as update_state ):
            pes.stop_runner()

            if no_process:
                thread.assert_not_called()
                current_process.terminate.assert_not_called()
                update_state.assert_not_called()

            else:
                thread.assert_called_once()
                assert thread.call_args.kwargs[ 'daemon' ] is True
                thread.return_value.start.assert_called_once_with()
                current_process.terminate.assert_called_once_with()
                update_state.assert_called_once_with( pes._row_id, ExecutionState.STOPPING )


    @pytest.mark.parametrize( 'no_process', [ True, False ] )
    def test_forced_stopping_runner( self, no_process: bool ) -> None:
        """ Test that forced stopping a runner actually works
        
        Args:
            no_process (bool): True to test without process registered
        """

        pes: PersistentExecutionSession = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._row_id = 'row-1'
        current_process = Mock()
        pes._runner = Mock()
        pes._runner.current_process = None if no_process else current_process

        with ( patch( 'automation_menu.models.persistent_execution_session.threading.Thread' ) as thread,
              patch.object( pes, 'update_state' ) as update_state ):
            pes.force_stop_runner()

            if no_process:
                thread.assert_not_called()
                current_process.kill.assert_not_called()
                update_state.assert_not_called()

            else:
                thread.assert_called_once()
                assert thread.call_args.kwargs[ 'daemon' ] is True
                thread.return_value.start.assert_called_once_with()
                current_process.kill.assert_called_once_with()
                update_state.assert_called_once_with( pes._row_id, ExecutionState.FORCED_STOPPING )


    def test_list_data_is_correct_tuple( self ) -> None:
        """ Test that treeview row representation of a session
        is correctly reported """

        filename: str = 'filename.py'
        status: str = 'status'
        state: ExecutionState = ExecutionState.RUNNING
        progress: float = float( 0 )
        started: datetime.datetime = datetime.datetime.now()

        pes: PersistentExecutionSession = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._script_info = Mock()
        pes._script_info.filename = filename
        pes._status = status
        pes._state = state
        pes._progress = progress
        pes._started_at = started

        assert pes.get_list_data() == ( filename, status, state, progress, started.strftime( '%H:%M:%S' ) )


    @pytest.mark.parametrize( 'list', [ [], [ 'E1', 'E2' ] ] )
    def test_get_all_errors( self, list: list[ str ] ) -> None:
        """ Join stored error messages with newline separators.

        Args:
            list (list[str]): Error messages, including an empty-list case.
        """

        pes: PersistentExecutionSession = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._error_list = list

        assert pes.get_all_error() == '\n'.join( list )


    @pytest.mark.parametrize( 'list', [ [], [ 'O1', 'O2' ] ] )
    def test_get_all_output( self, list: list[ str ] ) -> None:
        """ Join stored output messages with newline separators.

        Args:
            list (list[str]): Output messages, including an empty-list case.
        """

        pes: PersistentExecutionSession = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._output_list = list

        assert pes.get_all_output() == '\n'.join( list )


    def test_initiate_runner( self ) -> None:
        """ Test creating a runner object """

        pes: PersistentExecutionSession = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._script_info = Mock()
        entered_input: list[ str ] = []
        python_exe: str = ''
        run_state: str = ''

        with ( patch( 'automation_menu.models.persistent_execution_session.PersistentScriptRunner' ) as runner,
              patch( 'automation_menu.models.persistent_execution_session.PersistentSessionCallbacks' ) as ops ):
            pes._session_ops = ops

            pes._runner = runner
            pes.initiate_runner( entered_input = entered_input,
                                python_exe_path = python_exe,
                                 run_state = run_state )

            pes._runner.run_script.assert_called_once_with()


    @pytest.mark.parametrize( 'not_set', [ None, 'runner', 'current_process', 'process' ] )
    def test_resuming_a_paused_process( self, not_set: str | None ) -> None :
        """ Test resuming paused process
        
        Args:
            not_set (str | None): Define what should be unset to test different branches
        """

        pes = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._row_id = 'row-1'

        current_process = Mock()
        current_process.pid = 123

        runner = Mock()
        runner.current_process = ( None if not_set == 'current_process' else current_process )
        pes._runner = None if not_set == 'runner' else runner

        process: Mock = Mock()
        child: Mock = Mock( spec = Process )
        children: list[ Process ] = [ cast( Process, child ) ]
        process.children.return_value = children

        pes._psutil_process = None if not_set == 'process' else process
        pes._psutil_children = [] if not_set == 'process' else children

        with ( patch( 'automation_menu.models.persistent_execution_session.Process',
                     return_value = process, ) as process_class,
               patch.object( pes, 'update_state' ) as update_state, ):
            pes.resume_runner()

            if not_set in ['runner', 'current_process']:
                process.resume.assert_not_called()
                child.resume.assert_not_called()
                update_state.assert_not_called()

            else:
                process.resume.assert_called_once_with()
                child.resume.assert_called_once_with()
                update_state.assert_called_once_with( row_id = 'row-1', state = 'running' )

            if not_set == 'process':
                process_class.assert_called_once_with( 123 )
                process.children.assert_called_once_with( recursive = True )

            else:
                process_class.assert_not_called()


    @pytest.mark.parametrize( 'not_set', [ 'runner', 'current_process', 'process' ] )
    def test_pause_a_running_process( self, not_set: str | None ) -> None :
        """ Test pausing a running process
        
        Args:
            not_set (str | None): Define what should be unset to test different branches
        """

        pes = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._row_id = 'row-1'

        current_process = Mock()
        current_process.pid = 123

        runner = Mock()
        runner.current_process = ( None if not_set == 'current_process' else current_process )
        pes._runner = None if not_set == 'runner' else runner

        process = Mock()
        child = Mock( spec = Process )
        children = [ cast( Process, child ) ]
        process.children.return_value = children

        pes._psutil_process = None if not_set == 'process' else process
        pes._psutil_children = [] if not_set == 'process' else children

        with ( patch( 'automation_menu.models.persistent_execution_session.Process',
                     return_value = process, ) as process_class,
               patch.object( pes, 'update_state' ) as update_state, ):
            pes.pause_runner()

            if not_set in ['runner', 'current_process']:
                process.suspend.assert_not_called()
                child.suspend.assert_not_called()
                update_state.assert_not_called()

            else:
                process.suspend.assert_called_once_with()
                child.suspend.assert_called_once_with()
                update_state.assert_called_once_with( row_id = 'row-1', state = 'paused' )

            if not_set == 'process':
                process_class.assert_called_once_with( 123 )
                process.children.assert_called_once_with( recursive = True )

            else:
                process_class.assert_not_called()


    @pytest.mark.parametrize( ( 'method_name', 'message' ),
                             [ ( 'resume_runner', 'Could not find the process to resume' ),
                              ( 'pause_runner', 'Could not find the process to pause' ), ], )
    def test_missing_process_reports_error( self, method_name: str, message: str ) -> None:
        """ Report a missing process without announcing a successful state change.

        Args:
            method_name (str): Session operation to invoke: resume_runner or pause_runner.
            message (str): Expected error text passed to update_error.
        """

        pes = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._row_id = 'row-1'
        pes._runner = Mock()
        pes._runner.current_process.pid = 123
        pes._psutil_process = None
        pes._psutil_children = []

        with ( patch( 'automation_menu.models.persistent_execution_session.Process', side_effect = NoSuchProcess( pid = 123 ), ) as process_class,
              patch.object( pes, 'update_error' ) as update_error,
              patch.object( pes, 'update_state' ) as update_state,
              patch( 'automation_menu.utils.localization._', side_effect = lambda text: text, ), ):
            getattr( pes, method_name )()

            process_class.assert_called_once_with( 123 )
            update_error.assert_called_once_with( 'row-1', message )
            update_state.assert_not_called()


    @pytest.mark.parametrize( ( 'not_set', 'is_window', 'is_iconic', 'lookup_result' ),
                             [ pytest.param( None, 0, 0, 0 ),
                              pytest.param( None, 0, 1, 42 ),
                              pytest.param( None, 1, 0, 42 ),
                              pytest.param( None, 1, 1, 42 ),
                              pytest.param( 'win_handle', 0, 0, 0 ),
                              pytest.param( 'win_handle', 0, 1, 42 ),
                              pytest.param( 'win_handle', 1, 0, 42 ),
                              pytest.param( 'win_handle', 1, 1, 42 ) ] )
    def test_show_script_main_window( self, not_set: str | None, is_window: int, is_iconic: int, lookup_result: int ) -> None:
        """ Test bringing the scripts main window to be shown.

        Args:
            not_set (str | None): Define what not should be set
            is_window (int): Defining that the thought handle is a window or not
            is_iconic (int): Defining if the window is iconic or not
            lookup_result (int): Predefined window handle
        """

        pes = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._window_handle = 0 if not_set == 'win_handle' else 1

        proc = Mock( pid = 1 )
        proc.pid = 1
        pes._process = None if not_set == 'process' else cast( subprocess.Popen, proc )

        with ( patch( 'automation_menu.models.persistent_execution_session.win32gui' ) as win,
              patch.object( pes, 'get_main_window_handle',
                           return_value = lookup_result ) as lookup ):
            win.IsWindow.return_value = is_window
            win.IsIconic.return_value = is_iconic

            pes.show_main_window()

            needs_lookup = not_set == 'win_handle' or not is_window
            expected_handle = lookup_result if needs_lookup else 1

            if needs_lookup:
                lookup.assert_called_once_with( pid = 1 )

            else:
                lookup.assert_not_called()

            assert pes._window_handle == expected_handle

            if expected_handle == 0:
                win.IsIconic.assert_not_called()
                win.ShowWindow.assert_not_called()
                win.SetForegroundWindow.assert_not_called()

            else:
                win.IsIconic.assert_called_once_with( expected_handle )
                win.ShowWindow.assert_called_once_with( expected_handle, 9 if is_iconic else 5 )

                win.SetForegroundWindow.assert_called_once_with( expected_handle )


    @pytest.mark.parametrize( 'with_process', [ True, False ] )
    def test_show_main_window_with_no_process( self, with_process: bool ) -> None:
        """ Test showing window when process is not registered.

        Args:
            with_process (bool): Should an attached process be simulated
        """

        pes = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._row_id = 'r1'
        pes._error_list = []

        pes._process = Mock( pid = None ) if with_process else None

        with ( patch.object( pes, 'update_error' ) as update_error,
              patch( 'automation_menu.utils.localization._', side_effect = lambda text: text, ), ):
            pes.show_main_window()

            update_error.assert_called_once_with( 'r1', 'Could not find the scripts main window' )


    def test_update_error( self ) -> None:
        """ Test updating error list """

        pes = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._error_list = []
        pes._session_gui_ops = Mock()

        pes.update_error( 'row-1', 'E1' )

        assert len( pes._error_list ) == 1
        pes._session_gui_ops.update_ui.assert_called_once()


    def test_update_output( self ) -> None:
        """ Test updating output list """

        pes = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._output_list = []
        pes._session_gui_ops = Mock()

        pes.update_output( 'row-1', 'O1' )

        assert len( pes._output_list ) == 1
        pes._session_gui_ops.update_ui.assert_called_once()


    def test_update_progress( self ) -> None:
        """ Test updating runner progress """

        pes = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._session_gui_ops = Mock()

        pes.update_progress( 'row-1', 1 )

        assert pes._progress == float( 1 )
        pes._session_gui_ops.update_ui.assert_called_once()


    def test_update_state( self ) -> None:
        """ Test updating session state """

        pes = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._session_gui_ops = Mock()

        pes.update_state( 'row-1', 'running' )

        assert pes._state == ExecutionState.RUNNING
        pes._session_gui_ops.update_ui.assert_called_once()


    def test_update_status( self ) -> None:
        """ Test updating session status """

        pes = PersistentExecutionSession.__new__( PersistentExecutionSession )
        pes._session_gui_ops = Mock()

        pes.update_status( 'row-1', 'running' )

        assert pes._status == 'running'
        pes._session_gui_ops.update_ui.assert_called_once()


    @pytest.mark.parametrize( ( 'raise_psutil', 'parent_gotten', 'tp_id' ),
                             [ pytest.param( True, 0, ( 1, 123 ) ),
                              pytest.param( True, 0, ( 1, 999 ) ),
                              pytest.param( True, 1, ( 1, 123 ) ),
                              pytest.param( True, 1, ( 1, 999 ) ),
                              pytest.param( False, 0, ( 1, 123 ) ),
                              pytest.param( False, 0, ( 1, 999 ) ),
                              pytest.param( False, 1, ( 1, 123 ) ),
                              pytest.param( False, 1, ( 1, 999 ) ) ] )
    def test_getting_main_window_handle( self, raise_psutil: bool, parent_gotten: int, tp_id: tuple[ int, int ] ) -> None:
        """ Find a matching top-level window or return zero after the timeout.

        Args:
            raise_psutil (bool): Make process lookup fail to exercise the PID fallback.
            parent_gotten (int): Parent handle returned for the enumerated window;
                zero identifies a top-level window.
            tp_id (tuple[int, int]): Thread ID and process ID returned for the window.
        """

        # Arrange
        pes = PersistentExecutionSession.__new__( PersistentExecutionSession )

        process: Mock = Mock( pid = 123 )
        process.children.return_value = []
        expected_match = parent_gotten == 0 and tp_id[ 1 ] == 123

        module = 'automation_menu.models.persistent_execution_session'

        def enumerate_win( callback: Callable[ [ int, object ], bool ], extra: object ) -> None:
            """ Simulate Windows reporting one window.

            Args:
                callback (Callable[[int, object], bool]): Callback receiving a window
                    handle and context, returning whether enumeration should continue.
                extra (object): Context forwarded unchanged to the callback.
            """

            should_continue = callback( 42, extra )
            assert should_continue is ( not expected_match )

        with ( patch( f'{ module }.psutil.Process', return_value = process if not raise_psutil else None, side_effect = psutil.NoSuchProcess( pid = 123 ) if raise_psutil else None ) as process_class,
              patch( f'{ module }.win32gui.EnumWindows', side_effect = enumerate_win ),
              patch( f'{ module }.win32gui.GetParent', return_value = parent_gotten ),
              patch( f'{ module }.win32process.GetWindowThreadProcessId', return_value = tp_id ),
              patch( f'{ module }.time.time', side_effect = [ 100, 100, 106 ] ),
              patch( f'{ module }.time.sleep' ) ):

            # Act
            handle = pes.get_main_window_handle( pid = 123 )
            process_class.assert_called_once_with( 123 )

        # Assert
        assert handle == ( 42 if expected_match else 0 )
