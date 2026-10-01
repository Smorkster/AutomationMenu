"""
Test cases for script menu item

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter.ttk import Frame, Label
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call, patch

import pytest

from automation_menu.core.script_menu_item import ScriptMenuItem
from automation_menu.models.custom_exceptions import InvalidInputError
from automation_menu.models.scriptinfo import ScriptInfo


class TestUse:
    @pytest.mark.parametrize( 'has_parameters', [ False, True ] )
    def test_click_requests_input_or_runs_script( self, has_parameters: bool ) -> None:
        """ Verify that label click requests input or runs_script

        Args:
            has_parameters (bool): Specify if mocked ScriptInfo has any script iput parameters
        """

        smd: dict = { 'synopsis': 'S',
                     'author': 'a',
                     'description': 'D',
                     'state': 'Prod',
                     'script_input_parameters': [ {} ] if has_parameters else [] }
        used_attributes = { 'fullpath': 'C:\\file_path.py',
                           'filename': 'file_path.py',
                           'scriptmeta': smd }
        script_info: ScriptInfo = ScriptInfo.from_dict( used_attributes )

        main_window = Mock()
        hide_menu = Mock()

        with patch( 'automation_menu.core.script_menu_item.Label' ) as label:
            item = ScriptMenuItem( script_menu = Mock(),
                                  script_info = script_info,
                                  main_object = main_window,
                                  menu_hide_callback = hide_menu )

        with patch.object( item, 'run_script' ) as run_script:
            click_binding = next( call
                                 for call in label.return_value.bind.call_args_list
                                 if call.args[ 0 ] == '<Button-1>' )

            on_click = click_binding.args[ 1 ]
            on_click( Mock() )

            hide_menu.assert_called_once_with()

            input_manager = main_window.app_context.InputManager

            if has_parameters:
                input_manager.show_for_script.asser_called_once_with( script_info = script_info,
                                                                    submit_input_callback = run_script )
                run_script.assert_not_called()

            else:
                input_manager.show_for_script.assert_not_called()
                run_script.assert_called_once_with()


    @pytest.mark.parametrize( 'missing', [ None, 'runner', 'process', 'stdin' ] )
    def test_continues_after_breakpoint( self, missing: str | None ) -> None:
        """ Test if runner is continued after breakpoint

        Args:
            missing (str | None): Define testcases on what is missing.
        """

        stdin = Mock()
        process = Mock( stdin = None if missing == 'stdin' else stdin )
        runner = Mock( current_process = None if missing == 'process' else process )

        main_window = Mock()
        main_window.app_context.ExecutionManager.current_runner = ( None if missing == 'runner' else runner )

        item = ScriptMenuItem.__new__( ScriptMenuItem )
        item.master_self = main_window

        item.continue_breakpoint()

        if missing is None:
            assert stdin.mock_calls == [ call.write( 'c\n' ),
                                        call.flush() ]

        else:
            assert stdin.mock_calls == []


    def test_on_enter_changes_style( self ) -> None:
        """ Test that mouse entering label boundaries, changes style """

        item: ScriptMenuItem = ScriptMenuItem.__new__( ScriptMenuItem )
        item._style_hover = 'ScriptHover.TLabel'

        widget = Mock( spec = Label )
        event = Mock( widget = widget )
        item.on_enter( event )

        widget.configure.assert_called_once_with( style = 'ScriptHover.TLabel' )


    def test_on_enter_ignores_other_widgets( self ) -> None:
        """ Test that on_enter ignores other widgets """

        item: ScriptMenuItem = ScriptMenuItem.__new__( ScriptMenuItem )
        item._style_hover = 'ScriptHover.TLabel'

        widget = Mock( spec = Frame )
        event = Mock( widget = widget )
        item.on_enter( event )

        widget.configure.assert_not_called()


    def test_on_leave_changes_style( self ) -> None:
        """ Test that mouse entering label boundaries, changes style """

        item: ScriptMenuItem = ScriptMenuItem.__new__( ScriptMenuItem )
        item._style_normal = 'ScriptHover.TLabel'

        widget = Mock( spec = Label )
        event = Mock( widget = widget )
        item.on_leave( event )

        widget.configure.assert_called_once_with( style = 'ScriptHover.TLabel' )


    def test_on_leave_ignores_other_widgets( self ) -> None:
        """ Test that on_enter ignores other widgets """

        item: ScriptMenuItem = ScriptMenuItem.__new__( ScriptMenuItem )
        item._style_normal = 'ScriptHover.TLabel'

        widget = Mock( spec = Frame )
        event = Mock( widget = widget )
        item.on_leave( event )

        widget.configure.assert_not_called()


    @pytest.mark.parametrize( 'disable_minimize', [ False, True ] )
    def test_script_runs_one_time_runner( self, disable_minimize: bool ) -> None:
        """ Test that one time runner is started

        Args:
            disable_minimize (bool): True to test with setting main window to minimized size
         """

        menu_item: ScriptMenuItem = ScriptMenuItem.__new__( ScriptMenuItem )
        main_window = Mock()
        menu_item.master_self = main_window
        menu_item.master_self.execution_controller.execution_pre_work = Mock()

        smd: dict = { 'synopsis': 's',
                     'author': 'a',
                     'description': 'D',
                     'state': 'Dev',
                     'disable_minimize_on_running': disable_minimize,
                     'script_input_parameters': [] }
        si: dict = { 'fullpath': 'C:\\file_path.py',
                           'filename': 'file_path.py',
                           'scriptmeta': smd }

        menu_item.script_info = ScriptInfo.from_dict( si )

        context = main_window.app_context
        controller = main_window.execution_controller

        context.InputManager.collect_entered_input.return_value = [ SimpleNamespace( name = 'count', value = 3 ),
                                                                   SimpleNamespace( name = 'message', value = 'Hello' ) ]

        runner = Mock()
        runner_context = MagicMock()
        runner_context.__enter__.return_value = runner
        runner_context.__exit__.return_value = False

        context.ExecutionManager.create_runner.return_value = runner_context

        with patch( 'automation_menu.core.script_menu_item.threading.Thread' ) as thread:
            menu_item.run_script()

            controller.execution_pre_work.assert_called_once_with( disable_minimize = menu_item.script_info.scriptmeta.disable_minimize_on_running )
            thread.assert_called_once()
            assert thread.call_args.kwargs[ 'daemon' ] is True
            thread.return_value.start.assert_called_once_with()

            runner.run_script.assert_not_called()
            controller.execution_post_work.assert_not_called()
            target = thread.call_args.kwargs[ 'target' ]
            target()

        context.InputManager.collect_entered_input.assert_called_once_with()
        context.ExecutionManager.create_runner.assert_called_once_with()

        inp = []
        for ns in context.InputManager.collect_entered_input.return_value:
            inp.extend( [ f'--{ ns.name }', str( ns.value ) ] )

        runner.run_script.assert_called_once_with( script_info = menu_item.script_info,
                                                  main_window = main_window.root,
                                                  api_callbacks = main_window.api_callbacks,
                                                  enable_stop_button_callback = main_window.enable_stop_script_button,
                                                  enable_pause_button_callback = main_window.enable_pause_script_button,
                                                  stop_pause_button_blinking_callback = ( controller.stop_pause_button_blinking ),
                                                  run_input = inp )

        runner_context.__exit__.assert_called_once_with( None, None, None )
        controller.execution_post_work.assert_called_once_with( disable_minimize = menu_item.script_info.scriptmeta.disable_minimize_on_running )

        context.PersistentGuiManager.start_script.assert_not_called()


    @pytest.mark.parametrize( 'persistent', [ True, False ] )
    def test_persistent_script_runs( self, persistent: bool ) -> None:
        """ Test if a persistent script runs

        Args:
            persistent (bool): True if testing with persistent_gui,
                False if testing with persistent_gui_multiple
        """

        menu_item: ScriptMenuItem = ScriptMenuItem.__new__( ScriptMenuItem )
        main_window: Mock = Mock()
        menu_item.master_self = main_window

        smd: dict = { 'synopsis': 's',
                     'author': 'a',
                     'description': 'D',
                     'state': 'Dev',
                     'disable_minimize_on_running': False,
                     'persistent_gui': persistent,
                     'persistent_gui_multiple': not persistent,
                     'script_input_parameters': [] }
        si: dict = { 'fullpath': 'C:\\file_path.py',
                    'filename': 'file_path.py',
                    'scriptmeta': smd }
        menu_item.script_info = ScriptInfo.from_dict( si )

        context = main_window.app_context
        context.InputManager.collect_entered_input.return_value = []

        with patch( 'automation_menu.core.script_menu_item.threading.Thread' ) as thread:
            menu_item.run_script()

            context.PersistentGuiManager.start_script.assert_called_once_with( script_info = menu_item.script_info,
                                                                              entered_input = [] )

            thread.assert_not_called()

        context.ExecutionManager.create_runner.assert_not_called()


    def test_invalid_input_error_from_input_collection( self ) -> None:
        """ Test exception of InvalidInputError from collecting input """

        menu_item: ScriptMenuItem = ScriptMenuItem.__new__( ScriptMenuItem )
        main_window: Mock = Mock()
        menu_item.master_self = main_window

        smd: dict = { 'synopsis': 's',
                     'author': 'a',
                     'description': 'D',
                     'state': 'Dev',
                     'disable_minimize_on_running': False,
                     'script_input_parameters': [] }
        si: dict = { 'fullpath': 'C:\\file_path.py',
                    'filename': 'file_path.py',
                    'scriptmeta': smd }
        menu_item.script_info = ScriptInfo.from_dict( si )

        context = main_window.app_context
        context.InputManager.collect_entered_input.side_effect = ( InvalidInputError( 'Invalid count' ) )

        with patch( 'automation_menu.core.script_menu_item.dynamic_inputbox' ) as d:
            menu_item.run_script()

            d.assert_called_once()
            d.return_value.show.assert_called_once_with()

        context.PeristentGuiManager.start_script.assert_not_called()
        context.ExecutionManager.create_runner.assert_not_called()
        main_window.execution_controller.execution_pre_work.assert_not_called()


    def test_value_error_from_input_collection( self ) -> None:
        """ Test exception of InvalidInputError from collecting input """

        menu_item: ScriptMenuItem = ScriptMenuItem.__new__( ScriptMenuItem )
        main_window: Mock = Mock()
        menu_item.master_self = main_window

        smd: dict = { 'synopsis': 's',
                     'author': 'a',
                     'description': 'D',
                     'state': 'Dev',
                     'disable_minimize_on_running': False,
                     'script_input_parameters': [] }
        si: dict = { 'fullpath': 'C:\\file_path.py',
                    'filename': 'file_path.py',
                    'scriptmeta': smd }
        menu_item.script_info = ScriptInfo.from_dict( si )

        context = main_window.app_context
        context.InputManager.collect_entered_input.side_effect = ( ValueError( 'Invalid count' ) )

        with patch( 'automation_menu.core.script_menu_item.dynamic_inputbox' ) as d:
            menu_item.run_script()

            d.assert_called_once()
            d.return_value.show.assert_called_once_with()

        context.PeristentGuiManager.start_script.assert_not_called()
        context.ExecutionManager.create_runner.assert_not_called()
        main_window.execution_controller.execution_pre_work.assert_not_called()


class TestCreation:
    def test_script_menu_item__synopsis_is_missing( self, ) -> None:
        """ Check that synopsis is set as filename if text is missing """

        filename = 'file_path.py'
        smd: dict = { 'synopsis': 's',
                     'author': 'a',
                     'description': 'D',
                     'state': 'Prod',
                     'script_input_parameters': [] }
        used_attributes = { 'fullpath': 'C:\\file_path.py',
                           'filename': filename,
                           'scriptmeta': smd }
        script_info: ScriptInfo = ScriptInfo.from_dict( used_attributes )
        delattr( script_info.scriptmeta, 'synopsis' )

        main_window = Mock()
        hide_menu = Mock()

        with patch( 'automation_menu.core.script_menu_item.Label' ) as label:
            item = ScriptMenuItem( script_menu = Mock(),
                                script_info = script_info,
                                main_object = main_window,
                                menu_hide_callback = hide_menu )

        assert item.label_text == filename


    def test_script_menu_item__state_is_dev( self ) -> None:
        """ Test that label has ' (Dev)' added for script state 'DEV' """

        smd: dict = { 'synopsis': 's',
                     'author': 'a',
                     'description': 'D',
                     'state': 'Dev',
                     'script_input_parameters': [] }
        used_attributes = { 'fullpath': 'C:\\file_path.py',
                           'filename': 'file_path.py',
                           'scriptmeta': smd }
        script_info: ScriptInfo = ScriptInfo.from_dict( used_attributes )

        main_window = Mock()
        hide_menu = Mock()

        with patch( 'automation_menu.core.script_menu_item.Label' ) as label:
            item = ScriptMenuItem( script_menu = Mock(),
                                script_info = script_info,
                                main_object = main_window,
                                menu_hide_callback = hide_menu )

        assert ' (Dev)' in item.label_text
        assert item._style_normal == 'DevNormal.TLabel'
        assert item._style_hover == 'DevHover.TLabel'


    def test_script_menu_item__automationmenu_test_file_is_correctly_displayed( self ) -> None:
        """ Test that a script for AutomationMenu testing is correctly displayed """

        smd: dict = { 'synopsis': 's',
                     'author': 'a',
                     'description': 'D',
                     'state': 'Dev',
                     'script_input_parameters': [] }
        si_attributes = { 'fullpath': 'C:\\file_path.py',
                         'filename': 'AMTest_file_path.py',
                         'scriptmeta': smd }
        script_info: ScriptInfo = ScriptInfo.from_dict( si_attributes )
        script_info.scriptmeta.synopsis = ''

        main_window = Mock()
        hide_menu = Mock()

        with patch( 'automation_menu.core.script_menu_item.Label' ) as label:
            item = ScriptMenuItem( script_menu = Mock(),
                                script_info = script_info,
                                main_object = main_window,
                                menu_hide_callback = hide_menu )

        assert item._style_normal == 'AppTestNormal.TLabel'
        assert item._style_hover == 'AppTestHover.TLabel'
