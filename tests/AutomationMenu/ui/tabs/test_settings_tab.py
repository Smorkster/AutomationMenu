"""
Test cases for settings tab

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from pathlib import Path
from typing import Any, Callable, cast

import pytest

from collections import defaultdict
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, call, patch

import automation_menu.ui.tabs.settings_tab as settings_tab
from automation_menu.ui.tabs.settings_tab import SettingsUi, create_settings_tab
import automation_menu.utils.localization as localization


@pytest.fixture
def module() -> str:
    """ Module import path

    Returns:
        (str): Returns module import path
    """

    return 'automation_menu.ui.tabs.settings_tab'


@pytest.fixture
def tab_environment( monkeypatch: pytest.MonkeyPatch ) -> SimpleNamespace:
    """ Provide an isolated environment for testing settings-tab construction.

    Replace Tkinter widget and variable constructors, tooltip creation, and
    localization functions with mocks. Each constructor call produces a
    distinct mock and records its arguments for inspection.

    BooleanVar and StringVar mocks retain values through get() and set().
    Trace callbacks and callbacks scheduled through after_idle() are recorded
    but must be invoked explicitly by tests. SettingsUi and
    WidgetForTranslation remain real objects.

    The UI is not built automatically. Configure the supplied settings and
    mock return values before calling build(). Pytest restores patched
    attributes after each test.

    Args:
        monkeypatch (pytest.MonkeyPatch): Fixture used to temporarily replace
            dependencies in the settings-tab and localization modules.

    Returns:
        SimpleNamespace: Test environment exposing:
            settings: Mock settings with default boolean, language, shortcut,
                and script-folder values.
            controller: Mock controller receiving UI action calls.
            tab: Mock parent frame supplied to build_settings().
            notebook: Mock notebook available for tab-creation tests.
            add_translatable: Mock recording translation registrations.
            translate: Mock translation function returning text unchanged.
            languages: Mock language provider returning ['en', 'sv'].
            constructors: Constructor mocks indexed by class name.
            created: Creation records grouped by class name. Each record
                contains widget, args, and kwargs.
            build: Callable that runs the real build_settings() function
                using this environment.
    """

    created = defaultdict( list )
    constructors = {}

    def make_factory( kind: str ) -> Callable:
        """ Create a mock-construction function for one widget or variable type.

        Args:
            kind (str): Name of the constructor being replaced, such as
                'Checkbutton', 'Canvas', or 'StringVar'.

        Returns:
            Callable: Factory that creates a distinct mock on each call and
                appends its creation record to created[kind].
        """

        def factory( *args: Any, **kwargs: Any ) -> MagicMock:
            """ Create and record a mock widget or Tkinter variable.

            Support option lookup through subscription, such as widget['values'],
            using the constructor's keyword arguments. Canvas mocks provide default
            geometry values, Treeview mocks start without a selection, and variable
            mocks retain their current value through get() and set().

            Args:
                *args (Any): Positional arguments supplied to the mocked constructor.
                **kwargs (Any): Keyword arguments supplied to the mocked constructor.

            Returns:
                MagicMock: Newly created mock, also stored in created[kind] alongside
                    its positional and keyword constructor arguments.
            """

            widget = MagicMock( name = f'{ kind }_{ len( created[ kind ] ) }' )
            options = dict( kwargs )

            # Support access such as combobox[ 'values' ].
            widget.__getitem__.side_effect = options.__getitem__

            if kind == 'Canvas':
                widget.winfo_width.return_value = 200
                widget.bbox.return_value = ( 0, 0, 200, 600 )
                widget.create_window.return_value = 1

            if kind == 'Treeview':
                widget.selection.return_value = ()

            if kind in ( 'BooleanVar', 'StringVar' ):
                initial_value = False if kind == 'BooleanVar' else ''
                value = { 'current': kwargs.get( 'value', initial_value ) }

                widget.get.side_effect = lambda: value[ 'current' ]

                def set_value( new_value: Any ) -> None:
                    """ Store the value returned by subsequent calls to the variable's get().

                    This helper does not perform Tkinter type conversion or automatically
                    invoke registered trace callbacks.

                    Args:
                        new_value (Any): Value to store in the mocked variable.
                    """

                    value[ 'current' ] = new_value

                widget.set.side_effect = set_value

            created[ kind ].append( SimpleNamespace( widget = widget,
                                                    args = args,
                                                    kwargs = options, ) )

            return widget

        return factory

    for kind in ( 'Frame',
                 'Canvas',
                 'Scrollbar',
                 'Label',
                 'LabelFrame',
                 'Checkbutton',
                 'Combobox',
                 'Entry',
                 'Treeview',
                 'Button',
                 'BooleanVar',
                 'StringVar',
                 'AlwaysOnTopToolTip', ):
        constructor = Mock( name = kind, side_effect = make_factory( kind ) )
        constructors[ kind ] = constructor
        monkeypatch.setattr( settings_tab, kind, constructor )

    translate = Mock( side_effect = lambda text: text )
    languages = Mock( return_value = [ 'en', 'sv' ] )

    monkeypatch.setattr( localization, '_', translate )
    monkeypatch.setattr( localization, 'get_available_languages', languages )

    settings = Mock()
    settings.on_top = False
    settings.minimize_on_running = False
    settings.force_focus_post_execution = False
    settings.send_mail_on_error = False
    settings.include_ss_in_error_mail = False
    settings.current_language = 'en'
    settings.keepass_shortcut = { 'ctrl': True,
                                 'alt': False,
                                 'shift': False,
                                 'key': 'A', }
    settings.script_folders = []

    controller = Mock()
    add_translatable = Mock()
    tab = Mock()
    notebook = Mock()

    def build() -> SettingsUi:
        """ Build the settings UI using the environment's current configuration.

        Call the real build_settings() with mocked dependencies. Each call
        creates new mock widgets and appends their records to created; existing
        records and mock call histories are not cleared.

        Returns:
            SettingsUi: Real UI reference container populated with the created
                mock widgets and variables.
        """

        return settings_tab.build_settings( tab = tab,
                                           settings = settings,
                                           settings_ui_controller = controller,
                                           add_translatable = add_translatable, )

    return SimpleNamespace( settings = settings,
                           controller = controller,
                           tab = tab,
                           notebook = notebook,
                           add_translatable = add_translatable,
                           translate = translate,
                           languages = languages,
                           constructors = constructors,
                           created = created,
                           build = build, )


class TestCreateSettingsTab:

    def test_creates_adds_and_returns_settings_frame( self, module: str ) -> None:
        """ Create the frame under the notebook, add its tab, and return it.

        Args:
            module (str): Fixture for module import path
        """

        nb = Mock()
        cb = Mock()

        with ( patch( f'{ module }.Frame' ) as f,
              patch( f'{ module }.WidgetForTranslation' ) as wft ):
            basic_ret = create_settings_tab( tab_control = nb, translate_store_callback = cb )
            ret = cast( Mock, basic_ret )

            f.assert_called_once_with( nb,
                                      padding = ( 5, 5, 5, 5 ),
                                      name = 'settings' )
            ret.grid.assert_called_once_with( sticky = 'nswe' )
            ret.columnconfigure.assert_called_once_with( index = 0,
                                                        weight = 1 )
            ret.rowconfigure.assert_called_once_with( index = 0,
                                                     weight = 1 )


    def test_registers_tab_for_translation( self, module: str ) -> None:
        """ Register the created frame with default text 'Settings'.

        Args:
            module (str): Fixture for module import path
        """

        nb = Mock()
        cb = Mock()

        with ( patch( f'{ module }.Frame' ) as f,
              patch( f'{ module }.WidgetForTranslation', return_value = Mock() ) as wft ):
            basic_ret = create_settings_tab( tab_control = nb, translate_store_callback = cb )

            nb.add.assert_called_once_with( child = basic_ret,
                                           text = 'Settings' )
            wft.assert_called_once_with( widget = basic_ret,
                                        default_text = 'Settings' )
            cb.assert_called_once_with( wft.return_value )


class TestBuildSettings:

    def test_returns_ui_with_created_widget_references( self, tab_environment: SimpleNamespace ) -> None:
        """ Return a SettingsUi containing the actual created controls.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
        """

        env = tab_environment
        ui = env.build()

        assert ui.chb_top_most is env.created[ 'Checkbutton' ][ 0 ].widget
        assert ui.chb_minimize_on_running is env.created[ 'Checkbutton' ][ 1 ].widget
        assert ui.chb_force_focus_post_execution is env.created[ 'Checkbutton' ][ 2 ].widget

        assert ui.cmb_current_language is env.created[ 'Combobox' ][ 0 ].widget
        assert ui.script_folders_list is env.created[ 'Treeview' ][ 0 ].widget


    def test_connects_canvas_scrollbar_and_content_frame( self, tab_environment: SimpleNamespace ) -> None:
        """ Verify canvas, scrollbar, and content frame connections.

        Check that the canvas and scrollbar share a parent, their scrolling
        callbacks are connected, and the content frame is embedded in the canvas.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
        """

        env = tab_environment
        env.build()

        root_frame = env.created[ 'Frame' ][ 0 ].widget
        content_frame = env.created[ 'Frame' ][ 1 ].widget
        canvas = env.created[ 'Canvas' ][ 0 ].widget
        scrollbar = env.created[ 'Scrollbar' ][ 0 ].widget

        # Canvas and scrollbar share the outer frame.
        env.constructors[ 'Canvas' ].assert_called_once_with( master = root_frame,
                                                             highlightthickness = 0, )
        env.constructors[ 'Scrollbar' ].assert_called_once_with( master = root_frame,
                                                                orient = 'vertical',
                                                                command = canvas.yview, )

        # Canvas movement updates the scrollbar.
        canvas.configure.assert_called_once_with( yscrollcommand = scrollbar.set, )

        # The content frame belongs to, and is embedded in, the canvas.
        assert env.created[ 'Frame' ][ 1 ].kwargs[ 'master' ] is canvas
        canvas.create_window.assert_called_once_with( ( 0, 0 ),
                                                     window = content_frame,
                                                     anchor = 'nw', )


    @pytest.mark.parametrize( ( 'w_type', 'kwarg_name', 'text' ),
                             [ pytest.param( 'Label', 'text', 'Application settings' ),
                             pytest.param( 'Label', 'text', 'Set as topmost window' ),
                             pytest.param( 'AlwaysOnTopToolTip', 'msg', 'Shall the window be set as topmost, above all other windows' ),
                             pytest.param( 'Label', 'text', 'Minimize size during script execution' ),
                             pytest.param( 'AlwaysOnTopToolTip', 'msg', 'Downsize the window during script execution, trying not to be in its way. This setting can be ignored in ScriptInfo-block with \'DisableMinimizeOnRunning\'.' ),
                             pytest.param( 'Label', 'text', 'Main window focus post execution' ),
                             pytest.param( 'AlwaysOnTopToolTip', 'msg', 'Should the main window be forced back to focus after execution of script or sequence have finished' ),
                             pytest.param( 'Label', 'text', 'Application language' ),
                             pytest.param( 'AlwaysOnTopToolTip', 'msg', 'Language to use in the application' ),
                             pytest.param( 'Label', 'text', 'KeePass shortcut' ),
                             pytest.param( 'Checkbutton', 'text', 'CTRL' ),
                             pytest.param( 'Checkbutton', 'text', 'ALT' ),
                             pytest.param( 'Checkbutton', 'text', 'Shift' ),
                             pytest.param( 'AlwaysOnTopToolTip', 'msg', 'Shortcut used to activate KeePass for auto typing' ),
                             pytest.param( 'Label', 'text', 'Script folders' ),
                             pytest.param( 'Button', 'text', 'Add' ),
                             pytest.param( 'Button', 'text', 'Remove' ),
                             pytest.param( 'Label', 'text', 'To have any new or changed scripts listed in the menu, click ''Rebuild'' to read all script information again.' ),
                             pytest.param( 'Button', 'text', 'Rebuild' ),
                             pytest.param( 'Label', 'text', 'Errorhandling' ),
                             pytest.param( 'Label', 'text', 'Send mail to developer on script error' ),
                             pytest.param( 'AlwaysOnTopToolTip', 'msg', 'Should an mail be sent to its developer if an error occurs in the script?' ),
                             pytest.param( 'Label', 'text', 'Include screenshot in mail when reporting error' ),
                             pytest.param( 'AlwaysOnTopToolTip', 'msg', 'Should the mail be sent to script developer when reporting that an error occured, have a screenshot of main window attached?' ),
                               ] )
    def test_registers_labels_buttons_and_tooltips_for_translation( self, tab_environment: SimpleNamespace, w_type: str, kwarg_name: str, text: str ) -> None:
        """ Associate translatable widgets with their expected default texts.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            w_type (str): Widget type created
            kwarg_name (str): Argument name to match text
            text (str): Text associated with widget
        """

        env = tab_environment
        env.build()

        matches = [ record
                   for record in env.created[ w_type ]
                   if record.kwargs.get( kwarg_name ) == text ]
        assert len( matches ) == 1, ( f'Expected one { w_type } with \'{ kwarg_name }\' = \'{ text }\'' )
        record = matches[ 0 ]

        assert record.kwargs[ kwarg_name ] == text

        registrations = [ registered_call.args[ 0 ]
                         for registered_call in env.add_translatable.call_args_list
                         if registered_call.args[ 0 ].widget is record.widget ]

        assert len( registrations ) == 1
        assert registrations[ 0 ].default_text == text


    @pytest.mark.parametrize( ( 'setting_name', 'ui_attribute' ),
                             [ pytest.param( 'on_top', 'chb_top_most' ),
                              pytest.param( 'minimize_on_running', 'chb_minimize_on_running' ),
                              pytest.param( 'force_focus_post_execution', 'chb_force_focus_post_execution' ),
                              pytest.param( 'send_mail_on_error', 'chb_send_mail_on_error' ),
                              pytest.param( 'include_ss_in_error_mail', 'chb_include_ss_in_error_mail' ) ] )
    @pytest.mark.parametrize( 'initial_value', [ False, True ] )
    def test_boolean_controls_start_with_saved_values( self, tab_environment: SimpleNamespace, setting_name: str, ui_attribute: str, initial_value: bool ) -> None:
        """ Initialize each settings checkbox variable from its saved setting.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            setting_name (str): Name of setting to test
            ui_attribute (str): Widget name associated with setting
            initial_value (bool): Value widget is created with
        """

        env = tab_environment
        setattr( env.settings, setting_name, initial_value )

        ui = env.build()

        checkbox = getattr( ui, ui_attribute )
        record = next( record
                      for record in env.created[ 'Checkbutton' ]
                      if record.widget is checkbox )
        variable = record.kwargs[ 'variable' ]

        assert variable.get() is initial_value


class TestCheckboxCallbacks:

    @pytest.mark.parametrize( 'setting_name',
                             [ 'on_top',
                              'minimize_on_running',
                              'force_focus_post_execution',
                              'send_mail_on_error',
                              'include_ss_in_error_mail', ], )
    @pytest.mark.parametrize( 'new_value', [ False, True ] )
    def test_checkbox_command_passes_current_value_to_controller( self, tab_environment: SimpleNamespace, setting_name: str, new_value: bool ) -> None:
        """ Invoke the correct controller setter with the variable's current value.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            setting_name (str): Setting to test checkbox with
            new_value (bool): Value to set
        """

        env = tab_environment
        setattr( env.settings, setting_name, not new_value )
        ui = env.build()

        checkbox = getattr( ui, f'chb_{ setting_name if setting_name != 'on_top' else 'top_most' }' )
        record = next( record
                      for record in env.created[ 'Checkbutton' ]
                      if record.widget is checkbox )

        variable = record.kwargs[ 'variable' ]
        variable.set( new_value )

        controller_method = getattr( env.controller, f'set_{ setting_name }' )
        controller_method.assert_not_called()

        command = record.kwargs[ 'command' ]
        command()

        controller_method.assert_called_once_with( new_value )


    @pytest.mark.parametrize( 'send_mail', [ False, True ] )
    def test_screenshot_checkbox_initial_state_depends_on_send_mail( self, tab_environment: SimpleNamespace, send_mail: bool ) -> None:
        """ Disable screenshots when email is off; leave enabled when it is on.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            send_mail (bool): True if setting says to send mail
        """

        env = tab_environment
        setattr( env.settings, 'send_mail_on_error', not send_mail )
        ui = env.build()

        checkbox_send_ss = ui.chb_include_ss_in_error_mail
        record_ss = next( record
                         for record in env.created[ 'Checkbutton' ]
                         if record.widget is checkbox_send_ss )

        control = record_ss.widget

        if send_mail:
            control.config.assert_called_once_with( state = 'disabled' )

        else:
            control.config.assert_not_called()


class TestLanguage:

    def test_combobox_contains_available_languages( self, tab_environment: SimpleNamespace ) -> None:
        """ Populate language choices from get_available_languages.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
        """

        env = tab_environment
        ui = env.build()

        cb = ui.cmb_current_language
        record = next( r
                      for r in env.created[ 'Combobox' ]
                      if r.widget is cb )

        env.languages.assert_called_once()
        assert record.kwargs[ 'values' ] == env.languages.return_value


    @pytest.mark.parametrize( 'saved_language_available', [ False, True ] )
    def test_selects_saved_language_or_first_available( self, tab_environment: SimpleNamespace, saved_language_available: bool ) -> None:
        """ Select the saved language when available, otherwise the first choice.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            saved_language_available (bool): Simulate if language from settings is available
        """

        env = tab_environment
        setattr( env.settings, 'current_language', 'sv' if saved_language_available else 'dk' )
        ui = env.build()

        cb = ui.cmb_current_language
        record = next( r
                      for r in env.created[ 'Combobox' ]
                      if r.widget is cb )

        variable = record.kwargs[ 'textvariable' ]

        if saved_language_available:
            variable.set.assert_called_once_with( env.settings.current_language )

        else:
            variable.set.assert_called_once_with( env.languages.return_value[ 0 ] )


    def test_language_selection_is_bound_to_controller( self, tab_environment: SimpleNamespace ) -> None:
        """ Bind ComboboxSelected to the controller's language handler.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
        """

        env = tab_environment
        ui = env.build()

        cb = ui.cmb_current_language
        record = next( r
                      for r in env.created[ 'Combobox' ]
                      if r.widget is cb )

        record.widget.bind.assert_called_once_with( '<<ComboboxSelected>>', env.controller.set_current_language )


class TestKeepassShortcut:

    @pytest.mark.parametrize( 'set_modifier', [ 'ctrl', 'alt', 'shift' ] )
    def test_shortcut_controls_start_with_saved_values( self, tab_environment: SimpleNamespace, set_modifier: str ) -> None:
        """ Initialize Ctrl, Alt, Shift, and key variables from saved settings.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            set_modifier (str): Modifier setting to be set
        """

        env = tab_environment
        env.settings.keepass_shortcut[ 'ctrl' ] = set_modifier == 'ctrl'
        env.settings.keepass_shortcut[ 'alt' ] = set_modifier == 'alt'
        env.settings.keepass_shortcut[ 'shift' ] = set_modifier == 'shift'
        ui = env.build()

        ctrl = ui.keepass_shortcut_ctrl
        record_ctrl = next( r
                      for r in env.created[ 'Checkbutton' ]
                      if r.widget is ctrl )
        alt = ui.keepass_shortcut_alt
        record_alt = next( r
                      for r in env.created[ 'Checkbutton' ]
                      if r.widget is alt )
        shift = ui.keepass_shortcut_shift
        record_shift = next( r
                      for r in env.created[ 'Checkbutton' ]
                      if r.widget is shift )
        key = ui.keepass_shortcut_key
        record_key = next( r
                      for r in env.created[ 'Entry' ]
                      if r.widget is key )

        for name, record in [ ( 'alt', record_alt ), ( 'ctrl', record_ctrl ), ( 'shift', record_shift ) ]:
            assert record.kwargs[ 'variable' ].get() is env.settings.keepass_shortcut[ name ]

        assert record_key.kwargs[ 'textvariable' ].get() == env.settings.keepass_shortcut[ 'key' ]


    @pytest.mark.parametrize( 'key', [ 'alt', 'ctrl', 'shift', 'key' ] )
    def test_shortcut_variable_write_updates_matching_setting( self, tab_environment: SimpleNamespace, key: str ) -> None:
        """ Invoke the registered write trace and save the current key value.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            key (str): Key to simulate for
        """

        env = tab_environment
        env.settings.keepass_shortcut[ 'ctrl' ] = key == 'ctrl' or key == 'key'
        env.settings.keepass_shortcut[ 'alt' ] = key == 'alt'
        env.settings.keepass_shortcut[ 'shift' ] = key == 'shift'
        ui = env.build()

        control = getattr( ui, f'keepass_shortcut_{ key }' )

        if key == 'key':
            control_type = 'Entry' 
            var_type = 'StringVar'
            control_var_arg_name = 'textvariable'

        else:
            control_type = 'Checkbutton'
            var_type = 'BooleanVar'
            control_var_arg_name = 'variable'

        record = next( record
                      for record in env.created[ control_type ]
                      if record.widget is control )

        variable = record.kwargs[ control_var_arg_name ]
        variable.trace_add.assert_called_once()
        registration = variable.trace_add.call_args.kwargs
        assert registration[ 'mode' ] == 'write'

        callback = registration[ 'callback' ]
        new_value = 'B' if key == 'key' else not variable.get()
        variable.set( new_value )

        env.settings.set_keepass_shortcut.assert_not_called()
        callback( 'variable_name', '', 'write' )

        env.settings.set_keepass_shortcut.assert_called_once_with( shortcut_key = key,
                                                                  shortcut_val = new_value )


class TestScriptFolders:

    def test_saved_folders_are_inserted_in_order_with_existence_tags( self, tab_environment: SimpleNamespace ) -> None:
        """ Populate existing and missing folders with their corresponding tags.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
        """

        env = tab_environment
        env.settings.script_folders = [ Path( 'C:\\' ), Path( 'C:\\NotAvailable' ) ]
        ui = env.build()

        call_list = [ call( parent = '', index = 'end', text = 'C:\\', tags = ( 'exists' ) ),
                     call( parent = '', index = 'end', text = 'C:\\NotAvailable', tags = ( 'not_exists' ) )]
        assert ui.script_folders_list.insert.call_args_list == call_list


    def test_empty_folder_list_creates_no_rows( self, tab_environment: SimpleNamespace ) -> None:
        """ Leave the folder tree empty when no folders are configured.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
        """

        env = tab_environment
        env.settings.script_folders = []
        ui = env.build()

        ui.script_folders_list.insert.assert_not_called()


    @pytest.mark.parametrize( ( 'button_text', 'controller_method' ),
                             [ ( 'Add', 'add_script_folder' ),
                              ( 'Remove', 'remove_script_folder'),
                              ( 'Rebuild', 'rebuild_menu' ), ], )
    def test_folder_buttons_call_controller( self, tab_environment: SimpleNamespace, button_text: str, controller_method: str ) -> None:
        """ Wire each button to its intended controller method.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            button_text (str): Control to check
            controller_method (str): Method name that should be wired
        """

        env = tab_environment
        env.build()

        control = next( b
                       for b in env.created[ 'Button' ]
                       if b.kwargs[ 'text' ] == button_text )

        expected_method = getattr( env.controller, controller_method )
        command = control.kwargs[ 'command' ]

        assert command is expected_method
        expected_method.assert_not_called()

        command()
        expected_method.assert_called_once_with()


    def test_remove_button_starts_disabled( self, tab_environment: SimpleNamespace ) -> None:
        """ Prevent removal before a folder is selected.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
        """

        env = tab_environment
        env.build()
        control = next( b
                       for b in env.created[ 'Button' ]
                       if b.kwargs[ 'text' ] == 'Remove' )

        assert control.kwargs[ 'state' ] == 'disabled'


    @pytest.mark.parametrize( 'has_selection', [ False, True ] )
    def test_tree_selection_updates_remove_button_state( self, tab_environment: SimpleNamespace, has_selection: bool )-> None:
        """ Enable removal with a selection and disable it without one.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            has_selection (bool): True if selection is simulated
        """

        env = tab_environment
        env.build()

        tree = next( t
                    for t in env.created[ 'Treeview' ]
                    if t.kwargs[ 'name' ] == 'script_folder_list' )

        binding = next( b
                       for b in tree.widget.bind.call_args_list
                       if b.args[ 0 ] == '<<TreeviewSelect>>' )
        tree.widget.selection.return_value = ( 'r1', ) if has_selection else ()
        event = Mock( widget = tree.widget )
        binding.args[ 1 ]( event )

        btn = next( b
                    for b in env.created[ 'Button' ]
                    if b.kwargs[ 'name' ] == 'script_folder_btn_remove' )

        btn.widget.config.assert_called_once_with( state = '!disabled' if has_selection else 'disabled' )


class TestScrolling:

    @pytest.mark.parametrize( 'event_source',
                             [ 'canvas', 'content-frame' ] )
    def test_resize_schedules_scrollregion_refresh( self, tab_environment: SimpleNamespace, event_source: str ) -> None:
        """ Invoke the bound Configure handler and verify after_idle scheduling.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            event_source (str): Source control of event
        """

        env = tab_environment
        env.build()

        canvas = env.created[ 'Canvas' ][ 0 ].widget

        # Retrieve the frame embedded in the canvas without relying on Frame indexes.
        content_frame = canvas.create_window.call_args.kwargs[ 'window' ]
        source = canvas if event_source == 'canvas' else content_frame

        binding = next( recorded
                       for recorded in source.bind.call_args_list
                       if recorded.args[ 0 ] == '<Configure>' )
        resize_handler = binding.args[ 1 ]

        resize_handler( Mock( widget = source ) )

        canvas.after_idle.assert_called_once()
        refresh = canvas.after_idle.call_args.args[ 0 ]
        assert callable( refresh )

        # Refreshing should be deferred, not performed by the resize handler.
        canvas.bbox.assert_not_called()

        # Simulate Tkinter running the scheduled callback.
        refresh()

        canvas.bbox.assert_called_once_with( 'all' )
        canvas.configure.assert_any_call( scrollregion = canvas.bbox.return_value, )


    @pytest.mark.parametrize( 'canvas_width', [ 1, 200 ] )
    def test_refresh_resizes_embedded_frame_only_for_usable_width( self, tab_environment: SimpleNamespace, canvas_width: int ) -> None:
        """ Apply canvas width only when it is greater than one.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            canvas_width (int): New canvas width
        """

        env = tab_environment
        env.build()

        canvas = env.created[ 'Canvas' ][ 0 ].widget
        canvas.winfo_width.return_value = canvas_width
        window_id = canvas.create_window.return_value

        binding = next( recorded
                       for recorded in canvas.bind.call_args_list
                       if recorded.args[ 0 ] == '<Configure>' )

        # Resize schedules the refresh.
        binding.args[ 1 ]( Mock( widget = canvas ) )

        canvas.after_idle.assert_called_once()
        refresh = canvas.after_idle.call_args.args[ 0 ]

        # Execute the scheduled refresh.
        refresh()

        canvas.winfo_width.assert_called_once_with()

        if canvas_width > 1:
            canvas.itemconfig.assert_called_once_with( window_id,
                                                      width = canvas_width, )
        else:
            canvas.itemconfig.assert_not_called()


    @pytest.mark.parametrize( 'has_bbox', [ False, True ] )
    def test_refresh_sets_scrollregion_when_bounds_exist( self, tab_environment: SimpleNamespace, has_bbox: bool ) -> None:
        """ Use canvas bounds when available; skip the update when bbox is None.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            has_bbox (bool): Simulate if widget has bbox
        """

        env = tab_environment
        env.build()

        canvas = env.created[ 'Canvas' ][ 0 ].widget
        bounds = ( 0, 0, 200, 600 )
        canvas.bbox.return_value = bounds if has_bbox else None

        binding = next( recorded
                       for recorded in canvas.bind.call_args_list
                       if recorded.args[ 0 ] == '<Configure>' )
        binding.args[ 1 ]( Mock( widget = canvas ) )

        canvas.after_idle.assert_called_once()
        refresh = canvas.after_idle.call_args.args[ 0 ]

        canvas.configure.reset_mock()
        refresh()

        canvas.bbox.assert_called_once_with( 'all' )

        if has_bbox:
            canvas.configure.assert_called_once_with( scrollregion = bounds )

        else:
            canvas.configure.assert_not_called()


    @pytest.mark.parametrize( ( 'delta', 'expected_units' ),
                             [ ( 120, -1 ),
                              ( -120, 1 ),
                              ( 240, -2 ),
                              ( 30, -1 ),
                              ( -30, 1 ) ], )
    def test_mousewheel_scrolls_in_expected_direction( self, tab_environment: SimpleNamespace, delta: int, expected_units: int ) -> None:
        """ Scroll at least one unit for a nonzero wheel delta.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            delta (int): Distance scrolled
            expected_units (int): Scrolled unit
        """

        env = tab_environment
        env.build()

        canvas = env.created[ 'Canvas' ][ 0 ].widget

        binding = next( recorded
                       for recorded in canvas.bind_all.call_args_list
                       if recorded.args[ 0 ] == '<MouseWheel>' )
        mousewheel_handler = binding.args[ 1 ]

        mousewheel_handler( Mock( delta = delta ) )

        canvas.yview_scroll.assert_called_once_with( expected_units, 'units' )


    @pytest.mark.parametrize( 'has_delta', [ False, True ] )
    def test_mousewheel_ignores_missing_or_zero_delta( self, tab_environment: SimpleNamespace, has_delta: bool ) -> None:
        """ Do not scroll when delta is absent or zero.

        Args:
            tab_environment (SimpleNamespace): Fixture providing mocked widgets and creation records.
            has_delta (bool): Was scroll performed
        """

        env = tab_environment
        env.build()

        canvas = env.created[ 'Canvas' ][ 0 ].widget

        binding = next( recorded
                       for recorded in canvas.bind_all.call_args_list
                       if recorded.args[ 0 ] == '<MouseWheel>' )
        mousewheel_handler = binding.args[ 1 ]
        mousewheel_handler( Mock( delta = int( has_delta ) ) )

        if has_delta:
            canvas.yview_scroll.assert_called_once()

        else:
            canvas.yiew_scroll.assert_not_called()
