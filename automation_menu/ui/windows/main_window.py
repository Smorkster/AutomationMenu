"""
Create and manage main GUI window

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from pathlib import Path
from tkinter import Event, Tk
from tkinter.ttk import Notebook, Style
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.models.application_state import ApplicationState

from automation_menu.models.enums import ApplicationRunState
from automation_menu.ui.components.op_buttons import get_op_buttons
from automation_menu.ui.components.statusbar import get_statusbar
from automation_menu.ui.controllers.async_output_controller import AsyncOutputController
from automation_menu.ui.controllers.execution_ui_controller import ExecutionUiController
from automation_menu.ui.controllers.input_manager import InputManager
from automation_menu.ui.controllers.sequence_ui_controller import SequenceUiController
from automation_menu.ui.controllers.tab_ui_controller import ExecutionTabUiController
from automation_menu.ui.controllers.window_lifecycle_controller import ExecutionWindowLifecycleController
from automation_menu.ui.styling.config_ui_style import set_output_styles, set_ui_style
from automation_menu.ui.tabs.output_tab import get_output_tab
from automation_menu.ui.types.exec_button_refs import ExecutionButtonRefs
from automation_menu.ui.types.exec_lifecycle_refs import ExecutionLifecycleRefs
from automation_menu.ui.types.exec_min_max_refs import ExecutionMinMaxRefs
from automation_menu.ui.types.exec_post_work_refs import ExecutionPostWorkRefs
from automation_menu.ui.types.exec_pre_work_refs import ExecutionPreWorkRefs
from automation_menu.ui.types.exec_refs import ExecRefs
from automation_menu.ui.types.exec_status_refs import ExecutionStatusRefs
from automation_menu.ui.types.exec_tab_refs import ExecutionTabUiRefs
from automation_menu.ui.types.op_buttons_ui import OpButtonsUi
from automation_menu.ui.types.status_ui import StatusUi
from automation_menu.utils.decorators import ui_guard_method


class AutomationMenuWindow:
    """ Create and manage the main application window and its execution-related UI."""

    def __init__( self, app_state: ApplicationState, app_context: ApplicationContext ) -> None:
        """ Initialize the main application window.

        Args:
            app_state (ApplicationState): State object for application runtime state.
            app_context (ApplicationContext): Context container for managers and shared application objects.
        """

        from automation_menu.utils.localization import _

        self.app_state: ApplicationState = app_state
        self.app_context: ApplicationContext = app_context

        self._init_state()

        self._init_root()

        self._init_core_widgets()

        self._init_execution()

        self._init_tabs()

        self._finalize_window()


    @ui_guard_method( when_message = 'Centering window on screen' )
    def _center_screen( self ) -> None:
        """ Center the main window on the screen."""

        self.root.update_idletasks()
        width: int = self.root.winfo_width()
        height: int = self.root.winfo_height()

        if width <= 1 or height <= 1:
            self.root.after( 10, self._center_screen )

            return

        frm_width: int = self.root.winfo_rootx() - self.root.winfo_x()
        win_width: int = width + 2 * frm_width

        titlebar_height: int = self.root.winfo_rooty() - self.root.winfo_y()
        win_height: int = height + titlebar_height + frm_width

        x: float = self.root.winfo_screenwidth() // 2 - win_width // 2
        y: float = self.root.winfo_screenheight() // 2 - win_height // 2

        self.root.geometry( newGeometry = f'{ width }x{ height }+{ x }+{ y }' )


    def _create_execution_refs( self ) -> None:
        """ Create grouped execution-related UI reference objects."""

        self._exec_refs: ExecRefs = ExecRefs(
            ExecutionPreWorkRefs= ExecutionPreWorkRefs( op_buttons = self.op_buttons,
                                                         tab_control = self.tab_control,
                                                         status_widgets = self.status_widgets,
                                                         textbox_output = self.textbox_output,
                                                         root = self.root ),
            ExecutionPostWorkRefs = ExecutionPostWorkRefs( root = self.root ),
            ExecutionButtonRefs =  ExecutionButtonRefs( btn_pause_resume_script = self.op_buttons.btn_pause_resume_script,
                                                       root = self.root ),
            ExecutionMinMaxRefs = ExecutionMinMaxRefs( tab_control = self.tab_control,
                                                       op_buttons = self.op_buttons,
                                                       status_ui = self.status_widgets,
                                                       root = self.root ),
            ExecutionStatusRefs = ExecutionStatusRefs( progress_frame = self.status_widgets.status_bar,
                                                       text_status = self.status_widgets.text_status,
                                                       progressbar = self.status_widgets.progressbar,
                                                       separator = self.status_widgets.separator,
                                                       root = self.root )
        )


    def _create_lifecycle_refs( self ) -> None:
        """ Create grouped lifecycle-related UI and controller reference objects."""

        self._lifecycle_refs = ExecutionLifecycleRefs( output_controller = self.output_controller,
                                                      execution_controller = self.execution_controller,
                                                      tab_control = self.tab_control,
                                                      op_buttons = self.op_buttons,
                                                      status_ui = self.status_widgets,
                                                      root = self.root )


    def _init_core_widgets( self ) -> None:
        """ Initialize the main notebook, operation buttons, output tab, and status bar."""

        self.tab_control: Notebook = Notebook( master = self.root, style = self.tab_style )

        # Create buttons for script operations
        frame_style: str = f'{ self.app_context.startup_arguments[ 'app_run_state' ].value }Indicator.TFrame'
        self.op_buttons: OpButtonsUi = get_op_buttons( main_root = self.root, main_self = self, frame_style = frame_style )

        # Create output
        self.tab_output, self.textbox_output = get_output_tab( tabcontrol = self.tab_control, translate_callback = self.app_context.LanguageManager.add_translatable_widget )

        set_output_styles( widget = self.textbox_output )

        # Create statusbar
        self.status_widgets: StatusUi = get_statusbar( master_root = self.root )


    def _init_execution( self ) -> None:
        """ Initialize execution-related controllers, callbacks, and managers."""

        # Execution bindings
        self._create_execution_refs()
        self.execution_controller = ExecutionUiController( window = self,
                                                          app_context = self.app_context,
                                                          app_state = self.app_state,
                                                          exec_bindings = self._exec_refs )

        self.api_callbacks = { 'determinate_progress': self.execution_controller.set_progress_determined,
                              'hide_progress': self.execution_controller.hide_progress,
                              'indeterminate_progress': self.execution_controller.set_progress_indetermined,
                              'show_progress': self.execution_controller.show_progress,
                              'update_progress': self.execution_controller.update_progress,
                              'clear_status': self.execution_controller.clear_status,
                              'get_status': self.execution_controller.get_status,
                              'set_status': self.execution_controller.set_status,
                              'setting': self.setting }

        self.output_controller: AsyncOutputController = AsyncOutputController( output_queue = self.app_context.OutputQueue,
                                                                              text_widget = self.textbox_output,
                                                                              breakpoint_button = self.op_buttons.btn_continue_breakpoint,
                                                                              history_manager = self.app_context.HistoryManager,
                                                                              api_callbacks = self.api_callbacks,
                                                                              logger = self.app_context.debug_logger )
        self.output_controller.start()

        self._create_lifecycle_refs()
        self.lifecycle_controller = ExecutionWindowLifecycleController( app_context = self.app_context,
                                                                       app_state = self.app_state,
                                                                       exec_bindings = self._lifecycle_refs )

        self.app_context.InputManager = InputManager( root = self.root,
                                                     language_manager = self.app_context.LanguageManager )

        self.app_context.SequenceManager.sequence_ui_controller = SequenceUiController( app_context = self.app_context,
                                                                                       sequence_manager = self.app_context.SequenceManager,
                                                                                       execution_ui_controller = self.execution_controller,
                                                                                       debugger = self.app_context.debug_logger,
                                                                                       get_script_callback = self.app_context.ScriptManager.get_script_info_by_filename )


    def _finalize_window( self ) -> None:
        """ Finalize window layout, bind shortcuts, and start the main event loop."""

        self.root.columnconfigure( index = 0, weight = 1 )
        self.root.columnconfigure( index = 1, weight = 0 )
        self.root.rowconfigure( index = 0, weight = 0 ) # Op buttons
        self.root.rowconfigure( index = 1, weight = 0 ) # Input frame
        self.root.rowconfigure( index = 2, weight = 1 ) # Notebook tabs
        self.root.rowconfigure( index = 3, weight = 0 ) # Status bar

        # Shortcuts bindings
        self.root.bind( '<Control-m>', self._on_script_menu_shortcut )

        self.root.protocol( 'WM_DELETE_WINDOW', self.lifecycle_controller.on_closing )

        self.root.deiconify()
        self.root.focus_force()
        self.root.after_idle( self._center_screen )
        self.root.mainloop()


    def _init_root( self ) -> None:
        """ Create and configure the root Tk window and application styles."""

        # Create main GUI
        self.root: Tk = Tk()
        self.root.withdraw()
        self.root.geometry( '1100x600' )
        self.root.minsize( width = 620, height= 600 )

        title_string: str = self.app_state.secrets[ 'mainwindowtitle' ]

        if self.app_context.startup_arguments[ 'app_run_state' ].name != 'PROD':
            title_string += f' <{ self.app_context.startup_arguments[ 'app_run_state' ].name }>'

        self.tab_style = f'{ self.app_context.startup_arguments[ 'app_run_state' ].value }.TNotebook'

        self.root.title( string = title_string )

        # Setup styles
        self._style: Style = Style()
        set_ui_style( style = self._style )


    def _init_state( self ) -> None:
        """ Initialize window-related application state and shared UI values."""

        self.app_context.main_window = self
        self.settings_file_path: Path = self.app_state.secrets[ 'settings_file_path' ]

        self.button_margin: dict[ str, int ] = {
            'x': 5,
            'y': 5
        }


    def _init_tabs( self ) -> None:
        """ Initialize tab controller bindings and create the main application tabs."""

        self._tab_ui_refs = ExecutionTabUiRefs( tab_control = self.tab_control )

        self.tab_ui_controller = ExecutionTabUiController( app_context = self.app_context,
                                                          exec_bindings = self._tab_ui_refs )

        self.tab_ui_controller.init_tabs()


    def continue_breakpoint( self ) -> None:
        """ Continue execution after a breakpoint pause."""

        if self.app_state.running_automation is None:

            return

        self.op_buttons.btn_continue_breakpoint.state( [ "disabled" ] )
        self.app_state.running_automation.continue_breakpoint()


    @ui_guard_method( when_message = 'Opening script menu with shortcut' )
    def _on_script_menu_shortcut( self, event: Event | None = None ) -> None:
        """ Open the script menu through the keyboard shortcut.

        Args:
            event (Event | None): Event that triggered the handler.
        """

        self.op_buttons.script_menu.show_popup_menu()


    def set_display_dev( self ) -> None:
        """ Show or hide developer controls based on the configured state."""

        pass


    # region Button ops
    @ui_guard_method( when_message = 'Enabling breakpoint continue button' )
    def enable_breakpoint_button( self ) -> None:
        """ Enable the breakpoint continue button."""

        self.op_buttons.btn_continue_breakpoint.state( [ '!disabled' ] )


    @ui_guard_method( when_message = 'Disabling breakpoint continue button' )
    def disable_breakpoint_button( self ) -> None:
        """ Disable the breakpoint continue button."""

        self.op_buttons.btn_continue_breakpoint.state( [ 'disabled' ] )


    @ui_guard_method( when_message = 'Enabling pause/resume button' )
    def enable_pause_script_button( self ) -> None:
        """ Enable the pause or resume script button."""

        self.op_buttons.btn_pause_resume_script.state( [ '!disabled' ] )


    @ui_guard_method( when_message = 'Disabling pause/resume button' )
    def disable_pause_script_button( self ) -> None:
        """ Disable the pause or resume script button and reset its label."""

        from automation_menu.utils.localization import _

        self.op_buttons.btn_pause_resume_script.state( [ 'disabled' ] )
        self.op_buttons.btn_pause_resume_script.config( text = _( 'Pause' ) )


    @ui_guard_method( when_message = 'Enabling stop button' )
    def enable_stop_script_button( self ) -> None:
        """ Enable the stop script button."""

        self.op_buttons.btn_stop_script.state( [ '!disabled' ] )


    @ui_guard_method( when_message = 'Disabling stop button' )
    def disable_stop_script_button( self ) -> None:
        """ Disable the stop script button."""

        self.op_buttons.btn_stop_script.state( [ 'disabled' ] )
        self.execution_controller.stop_pause_button_blinking()


    @ui_guard_method( when_message = 'Pausing script' )
    def pause_resume_script( self ) -> None:
        """ Pause or resume the currently running script."""

        self.execution_controller.pause_resume_script()


    @ui_guard_method( when_message = 'Stopping script' )
    def stop_script( self ) -> None:
        """ Stop the currently running script."""

        self.execution_controller.stop_script()
    # endregion


    # region Settings API callbacks
    @ui_guard_method( when_message = 'API setting retrieval' )
    def setting( self, key_dict: dict ) -> None:
        """ Return a setting value through the API.

        Args:
            key_dict (dict): Dictionary specifying which setting to retrieve.
        """

        runner = self.app_context.ExecutionManager.current_runner

        if runner is None:
            return

        setting = self.lifecycle_controller.serialize_setting( key = key_dict[ 'key' ] )
        self.root.after( 10, lambda: runner.send_api_response( response = setting ) )

    # endregion Settings API callbacks
