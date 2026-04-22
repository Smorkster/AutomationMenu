"""
Create and manage main GUI window

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from __future__ import annotations
import json
from pathlib import Path
import time
from typing import TYPE_CHECKING, Any, Callable, Dict, cast

from automation_menu.models.geometry import Geometry
from automation_menu.ui.custom_menu import CustomMenu

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.models.application_state import ApplicationState

import dynamicinputbox

from tkinter import E, N, S, W, Event, Tk, Widget, messagebox
from tkinter.ttk import Button, Combobox, Frame, Notebook, Style
from typing import Tuple

from automation_menu.filehandling.settings_handler import write_settingsfile
from automation_menu.models.enums import ApplicationRunState, OutputStyleTags, SysInstructions
from automation_menu.ui.async_output_controller import AsyncOutputController
from automation_menu.ui.config_ui_style import set_output_styles, set_ui_style
from automation_menu.ui.input_manager import InputManager
from automation_menu.ui.op_buttons import ButtonDict, get_op_buttons
from automation_menu.ui.output_tab import get_output_tab
from automation_menu.ui.settings_tab import SettingsUiDict
from automation_menu.ui.statusbar import StatusDict, get_statusbar
from automation_menu.utils.decorators import ui_guard_method


class AutomationMenuWindow:
    def __init__( self, app_state: ApplicationState, app_context: ApplicationContext ) -> None:
        """ Creates the main window

        Args:
            app_state (ApplicationState): State object for various application states
            app_context (ApplicationContext): Context vault for function managers and various states
        """

        from automation_menu.utils.localization import _

        self.app_state: ApplicationState = app_state
        self.app_context: ApplicationContext = app_context
        self.app_context.main_window = self
        self.settings_file_path: Path = self.app_state.secrets[ 'settings_file_path' ]

        self.old_window_geometry: Geometry = Geometry()
        self.widgets = {}
        self._blink_active: bool = False
        self._blink_job: str = ''
        self._blink_state: bool = False
        self._close_confirmed: bool = False
        self._progressbar_visible: bool = False
        self._tabs_build = {}

        self.api_callbacks = {
            'determinate_progress': self.set_progress_determined,
            'hide_progress': self.hide_progress,
            'indeterminate_progress': self.set_progress_indetermined,
            'show_progress': self.show_progress,
            'update_progress': self.update_progress,

            'clear_status': self.clear_status,
            'get_status': self.get_status,
            'set_status': self.set_status,

            'setting': self.setting
        }

        self.sequence_callbacks: dict[ str, Callable ] = {
            'op_abort_add_sequence_step': self.op_abort_add_sequence_step,
            'op_add_sequence_step': self.op_add_sequence_step,
            'op_create_new_sequence': self.op_create_new_sequence,
            'op_save_sequence': self.op_save_sequence,
            'op_remove_sequence_step': self.op_remove_sequence_step,
            'op_edit_sequence': self.op_edit_sequence,
            'op_delete_sequence': self.op_delete_sequence,
            'op_abort_sequence_edit': self.op_abort_sequence_edit,
            'op_run_sequence': self.op_run_sequence
        }

        # Create main GUI
        self.root: Tk = Tk()
        self.root.withdraw()
        self.root.geometry( '1100x600' )

        title_string: str = self.app_state.secrets[ 'mainwindowtitle' ]

        if self.app_context.startup_arguments[ 'app_run_state' ] == ApplicationRunState.DEV:
            title_string += " <DEV>"
            self.tab_style = 'Dev.TNotebook'

        elif self.app_context.startup_arguments[ 'app_run_state' ] == ApplicationRunState.TEST:
            title_string += " <TEST>"
            self.tab_style = 'Test.TNotebook'

        else:
            self.tab_style = 'TNotebook'

        self.root.title( string = title_string )

        self.app_context._input_manager = InputManager( root = self.root,
                                                       language_manager = self.app_context.LanguageManager
                                                      )

        # Setup styles
        self._style: Style = Style()
        set_ui_style( style = self._style )

        self.button_margin: dict[ str, int ] = {
            'x': 5,
            'y': 5
        }

        # Create buttons for script operations
        self.op_buttons: ButtonDict = get_op_buttons( main_root = self.root, main_self = self )

        # Add tabs
        self.tab_control: Notebook = Notebook( master = self.root, style = self.tab_style )
        self.tab_control.bind( '<<NotebookTabChanged>>', self._on_tab_change )
        self.tab_control.grid( column = 0, columnspan = 2, row = 2, sticky = 'nswe' )
        tab_index = 0

        # Create output
        self.tab_output, self.textbox_output = get_output_tab( tabcontrol = self.tab_control, translate_callback = self.app_context.LanguageManager.add_translatable_widget )

        set_output_styles( widget = self.textbox_output )

        # Manage output
        self.output_controller: AsyncOutputController = AsyncOutputController( output_queue = self.app_context.OutputQueue,
                                                       text_widget = self.textbox_output,
                                                       breakpoint_button = self.op_buttons[ 'btnContinueBreakpoint' ],
                                                       history_manager = self.app_context.HistoryManager,
                                                       api_callbacks = self.api_callbacks,
                                                       logger = self.app_context.debug_logger
                                                       )
        self.output_controller.start()

        # Create sequence tab
        tab_index += 1
        self.sequence_tab: Frame = self.app_context.SequenceManager.create_sequence_tab( tabcontrol = self.tab_control, sequence_callbacks = self.sequence_callbacks, translate_callback = self.app_context.LanguageManager.add_translatable_widget )
        self._tabs_build[ tab_index ] = { 'idx': tab_index, 'built': False }

        # Create settings tab
        tab_index += 1
        self.tabSettings: Frame = app_context.SettingsManager.create_tab( parent_tab = self.tab_control, translate_store_callback = self.app_context.LanguageManager.add_translatable_widget )
        self._tabs_build[ tab_index ] = { 'idx': tab_index, 'built': False }

        # Create history tab
        tab_index += 1
        self.tabHistory: Frame = self.app_context.HistoryManager.get_history_tab( tabcontrol = self.tab_control, translate_store_callback = self.app_context.LanguageManager.add_translatable_widget )
        self._tabs_build[ tab_index ] = { 'idx': tab_index, 'built': False }

        # Create statusbar
        self.status_widgets: StatusDict = get_statusbar( master_root = self.root )

        self.root.columnconfigure( index = 0, weight = 1 )
        self.root.columnconfigure( index = 1, weight = 0 )
        self.root.rowconfigure( index = 0, weight = 0 ) # Op buttons
        self.root.rowconfigure( index = 1, weight = 0 ) # Input frame
        self.root.rowconfigure( index = 2, weight = 1 ) # Notebook tabs
        self.root.rowconfigure( index = 3, weight = 0 ) # Status bar

        # Shortcuts bindings
        self.root.bind( '<Control-m>', self._on_script_menu_shortcut )

        self.root.protocol( 'WM_DELETE_WINDOW', self.on_closing )

        self.root.deiconify()
        self.root.focus_force()
        self.root.after_idle( self._center_screen )
        self.root.mainloop()


    @ui_guard_method( when_message = 'Centering window on screen' )
    def _center_screen( self ) -> None:
        """ Center main window on screen """

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


    def _confirm_close_process( self ) -> bool:
        """ Should the running script be terminated before closing application """

        from automation_menu.utils.localization import _

        line: str = _( 'There is a script running. Do you want to terminate the script process before closing the application?' )
        answ: bool = messagebox.askyesno( title = _( 'Script still runnning' ), message = line, parent = self.root )

        if answ:
            self._stop_script()

        return answ


    def _continue_breakpoint( self ) -> None:
        """ Reset application debug mode """

        if self.app_state.running_automation is None:

            return

        self.op_buttons[ 'btnContinueBreakpoint' ].state( [ "disabled" ] )
        self.app_state.running_automation.continue_breakpoint()


    def _minimize_hide_controls( self ) -> None:
        """ Hide UI control widgets when window is minimized during script execution """

        self.tab_control.config( style = 'HiddenTabs.TNotebook' )
        self.status_widgets[ 'separator' ].grid_remove()
        self.status_widgets[ 'text_status' ].grid_remove()
        self.status_widgets[ 'status_bar' ].grid_remove()
        self.status_widgets[ 'status_bar' ].grid_columnconfigure( index = 0, weight = 0 )
        self.status_widgets[ 'status_bar' ].grid_columnconfigure( index = 1, weight = 0 )

        self.op_buttons[ 'menu_frame' ].grid_remove()
        self.op_buttons[ 'btnContinueBreakpoint' ].config( style = 'RunningSmall.TButton' )
        self.op_buttons[ 'btnStopScript' ].config( style = 'RunningSmall.TButton' )
        self.op_buttons[ 'btnPauseResumeScript' ].config( style = 'RunningSmall.TButton' )

        self.status_widgets[ 'progressbar' ].config( style = 'RunningSmall.TProgressbar' )

        self.root.overrideredirect( True )  # Remove window decorations


    def _minimize_show_controls( self ) -> None:
        """ Show all hidden UI control widgets when script execution has finished """

        self.tab_control.config( style = self.tab_style )
        self.status_widgets[ 'status_bar' ].grid()
        self.status_widgets[ 'separator' ].grid()
        self.status_widgets[ 'text_status' ].grid()
        self.status_widgets[ 'status_bar' ].grid_columnconfigure( index = 0, weight = 1 )
        self.status_widgets[ 'status_bar' ].grid_columnconfigure( index = 1, weight = 0 )

        self.op_buttons[ 'menu_frame' ].grid()
        self.op_buttons[ 'btnContinueBreakpoint' ].config( style = 'TButton' )
        self.op_buttons[ 'btnStopScript' ].config( style = 'TButton' )
        self.op_buttons[ 'btnPauseResumeScript' ].config( style = 'TButton' )

        self.status_widgets[ 'progressbar' ].config( style = 'TProgressbar' )

        self.root.overrideredirect( False )  # Reapply window decorations


    @ui_guard_method( when_message = 'Opening script menu with shortcut' )
    def _on_script_menu_shortcut( self, event: Event | None = None ) -> None:
        """ Open script menu with shortcut

        Args:
            event (Event | None): Event triggering the handler
        """

        self.op_buttons[ 'script_menu' ].show_popup_menu()


    @ui_guard_method( when_message = 'Tab change' )
    def _on_tab_change( self, event: Event | None = None ) -> None:
        """ Notebook tab changes focus, check if tab have been loaded yet

        Args:
            event (Event | None): Event triggering the handler
        """

        if event is None or not isinstance( event.widget, Notebook ):

            return

        idx = event.widget.index( 'current' )

        if not self._tabs_build.get( idx, {} ).get( 'built', True ):
            if idx == 1:
                self.app_context.SequenceManager.build_tab_content()

            elif idx == 2:
                self.settings_ui: SettingsUiDict = self.app_context.SettingsManager.build_tab_content()

            elif idx == 3:
                self.app_context.HistoryManager.build_tab_content( translate_store_callback = self.app_context.LanguageManager.add_translatable_widget, translate_callback = self.app_context.LanguageManager.translate )

            self._tabs_build[ idx ][ 'built' ] = True


    @ui_guard_method( when_message = 'Changing language' )
    def _on_language_change( self, new_lang: str ) -> None:
        """ Eventhandler for when application changes by the user

        Args:
            new_lang (str): The new language to change to
        """

        self.app_state.settings.current_language = new_lang
        write_settingsfile( settings = self.app_state.settings, settings_file_path = str( self.settings_file_path ) )


    @ui_guard_method( when_message = 'Pausing/resuming execution' )
    def _pause_resume_script( self ) -> None:
        """ Pause script execution """

        from automation_menu.utils.localization import _

        if self.app_context.ExecutionManager.is_paused():
            if self.app_context.ExecutionManager.resume_current_script():
                self.app_context.OutputQueue.put( { 'line': _( 'Process was resumed' ),
                                                    'tag': OutputStyleTags.SYSINFO
                                                    } )
                self.op_buttons[ 'btnPauseResumeScript' ].config( text = _( 'Pause' ) )

                self._blink_active = False
                self.stop_pause_button_blinking()

        else:
            if self.app_context.ExecutionManager.pause_current_script():
                self.app_context.OutputQueue.put( { 'line': _( 'Process was paused' ),
                                                    'tag': OutputStyleTags.SYSINFO
                                                    } )
                self.op_buttons[ 'btnPauseResumeScript' ].config( text = _( 'Resume' ) )
                self._blink_active = True
                self._pause_button_blinking()


    @ui_guard_method( when_message = 'Pausing button blinking' )
    def _pause_button_blinking( self ) -> None:
        """ Initiate blinking effect of pause button during breakpoint pause """

        if not self._blink_active:
            return

        button: Button = self.op_buttons[ 'btnPauseResumeScript' ]
        self._blink_state = not self._blink_state

        self.root.after( 100, lambda: button.config( style = 'BlinkBg.TButton' if self._blink_state else 'TButton' ) )
        self.root.update_idletasks()

        self._blink_job = self.root.after( 600, self._pause_button_blinking )


    def _serialize_setting( self, key: Any ) -> str:
        """ Normalize setting value to a string

        Args:
            key (Any): Key name of setting to normalize

        Returns:
            (str): String normalization of setting value
        """

        value = self.app_state.settings.get( key )
        if value is None:

            return ""

        if isinstance( value, ( str, int, float, bool ) ):

            return str( value )

        # dict / list / TypedDict / dataclasses / etc.
        try:
            return json.dumps( value, ensure_ascii = False, default = str )

        except TypeError:
            return str( value )


    @ui_guard_method( when_message = 'Stopping script' )
    def _stop_script( self ) -> None:
        """ Eventhandler for when user clicks button stop script """

        self.app_context.ExecutionManager.stop_current_script()
        self.stop_pause_button_blinking()


    @ui_guard_method( when_message = 'Doing execution post work' )
    def execution_post_work( self, disable_minimize: bool = False, is_sequence: bool = False ) -> None:
        """ Reset UI and controls after script/sequence execution

        Args:
            disable_minimize (bool): Is minimization disabled through settings
            is_sequence (bool): Is caller a sequence
        """

        self.disable_pause_script_button()
        self.disable_stop_script_button()

        if self.app_state.settings.get( 'minimize_on_running' ) and not disable_minimize:
            self.min_max_on_running()

        self._minimize_show_controls()

        if self.app_state.settings.force_focus_post_execution:
            self.root.focus_force()


    @ui_guard_method( when_message = 'Doing execution pre work' )
    def execution_pre_work( self, disable_minimize: bool = False, is_sequence: bool = False ) -> None:
        """ Set UI and controls according to preferences before execution

        Args:
            disable_minimize (bool): Is minimization disabled through settings
            is_sequence (bool): Is caller a sequence
        """

        from automation_menu.utils.localization import _

        self.tab_control.select( 0 )
        self.app_context.OutputQueue.put( SysInstructions.CLEAROUTPUT )
        self.app_context.InputManager.hide_input_frame()

        if self.app_state.settings.get( 'minimize_on_running' ):
            if disable_minimize:
                self.app_context.OutputQueue.put( {
                    'line': _( 'The script has \'DisableMinimizeOnRunning\', meaning the window will not be minimized.' ),
                    'tag': OutputStyleTags.SYSINFO
                } )

            else:
                self._minimize_hide_controls()
                old_geometry = Geometry( height = self.root.winfo_height(),
                                        width = self.root.winfo_width(),
                                        x = self.root.winfo_x(),
                                        y = self.root.winfo_y()
                                        )
                self.min_max_on_running( old_geometry )


    @ui_guard_method( when_message = 'Closing main window' )
    def on_closing( self ) -> None:
        """ Window close event. Handle if a script is still running """

        from automation_menu.utils.localization import _

        if not self._close_confirmed and self.app_context.ExecutionManager.is_running():
            if not self._confirm_close_process():

                return

        try:
            write_settingsfile( settings = self.app_state.settings, settings_file_path = self.app_state.secrets[ 'settings_file_path' ] )

        except Exception as e:

            dynamicinputbox.dynamic_inputbox( title = _( 'Write settings error' ), message = _( 'Could not save settings to file: {e}' ).format( e = e ) ).show()

            return

        self.root.destroy()

        if hasattr( self, 'output_controller' ):
            try:
                self.output_controller.closedown()

            except Exception as e:
                self.app_context.debug_logger.warning( _( 'Error shutting down output controller: {e}' ).format( e = e ) )


    def set_current_language( self, event: Event ) -> None:
        """ Change the language in the application

        Args:
            event (Event): Event actualizing the function
        """

        if not event or not isinstance( event.widget, Combobox ):

            return

        self.app_state.settings.current_language = event.widget.get()
        self.app_context.LanguageManager.change_app_language( new_language = event.widget.get() )


    def set_force_focus_post_execution( self, new_value: bool ) -> None:
        """ Save setting to user_settings file

        Args:
            new_value (bool): New value to save
        """

        self.app_state.settings.force_focus_post_execution = new_value

        if new_value:
            self.settings_ui[ 'chb_force_focus_post_execution' ].config( state = 'normal' )

        else:
            self.settings_ui[ 'chb_force_focus_post_execution' ].config( state = 'disabled' )


    def set_display_dev( self ) -> None:
        """ Show or hide developer controls based on the checkbox state

            To be implemented
        """

        pass


    def set_send_mail_on_error( self, new_value: bool ) -> None:
        """ Save setting to user_settings file

        Args:
            new_value (bool): New value to save
        """

        self.app_state.settings.send_mail_on_error = new_value

        if new_value:
            self.settings_ui[ 'chbIncludeSsInErrorMail' ].config( state = 'normal' )

        else:
            self.settings_ui[ 'chbIncludeSsInErrorMail' ].config( state = 'disabled' )


    def set_include_ss_in_error_mail( self, new_value: bool ) -> None:
        """ Save setting to user_settings file

        Args:
            new_value (bool): New value to save
        """

        self.app_state.settings.include_ss_in_error_mail = new_value


    def set_minimize_on_running( self, new_value: bool ) -> None:
        """ Save setting to user_settings file
        
        Args:
            new_value (bool): New value to save
        """

        self.app_state.settings.minimize_on_running = new_value


    @ui_guard_method( when_message = 'Down-/resizing window before/after script execution' )
    def min_max_on_running( self, old_geometry: Geometry | None = None ) -> None:
        """ Resize window during script execution

        Args:
            old_geometry (Geometry | None): Size values of main window before script execution
        """

        win_width: int = 400
        win_height: int = 200

        if old_geometry:
            self.old_window_geometry = old_geometry
            self._minimize_hide_controls()
            self.root.geometry( newGeometry = f'{ win_width }x{ win_height }+{ self.root.winfo_screenwidth() - win_width  }+{ self.root.winfo_screenheight() - win_height - 100 }' )

        else:
            self.root.geometry( newGeometry = self.old_window_geometry.to_string() )
            self._minimize_show_controls()

        self.root.update_idletasks()


    @ui_guard_method( when_message = 'Setting window \'on top\'' )
    def set_on_top( self, new_value: bool ) -> None:
        """ Save setting to user_settings and set/unset the window as top most

        Args:
            new_value (bool): New value to set and save
        """

        self.app_state.settings.on_top = new_value
        self.root.focus_force()
        self.root.attributes( '-topmost', new_value )


    # region Button ops
    @ui_guard_method( when_message = 'Enabling breakpoint continue button' )
    def enable_breakpoint_button( self ) -> None:
        """ Enable the breakpoint button """

        self.op_buttons[ 'btnContinueBreakpoint' ].state( [ '!disabled' ] )


    @ui_guard_method( when_message = 'Disabling breakpoint continue button' )
    def disable_breakpoint_button( self ) -> None:
        """ Disable the breakpoint button """

        self.op_buttons[ 'btnContinueBreakpoint' ].state( [ 'disabled' ] )


    @ui_guard_method( when_message = 'Enabling pause/resume button' )
    def enable_pause_script_button( self ) -> None:
        """ Enable the stop script button """

        self.op_buttons[ 'btnPauseResumeScript' ].state( [ '!disabled' ] )


    @ui_guard_method( when_message = 'Disabling pause/resume button' )
    def disable_pause_script_button( self ) -> None:
        """ Enable the stop script button """

        from automation_menu.utils.localization import _

        self.op_buttons[ 'btnPauseResumeScript' ].state( [ 'disabled' ] )
        self.op_buttons[ 'btnPauseResumeScript' ].config( text = _( 'Pause' ) )


    @ui_guard_method( when_message = 'Enabling stop button' )
    def enable_stop_script_button( self ) -> None:
        """ Enable the stop script button """

        self.op_buttons[ 'btnStopScript' ].state( [ '!disabled' ] )


    @ui_guard_method( when_message = 'Disabling stop button' )
    def disable_stop_script_button( self ) -> None:
        """ Disable the stop script button """

        self.op_buttons[ 'btnStopScript' ].state( [ 'disabled' ] )
        self._pause_button_blinking()


    @ui_guard_method( when_message = 'Stopping blinking of pause button' )
    def stop_pause_button_blinking( self ) -> None:
        """ Stop blinking effect for button when script execution continues """

        self._blink_active = False

        if self._blink_job:
            self.root.after_cancel( self._blink_job )
            self._blink_job = ''
    # endregion


    # region Sequence UI ops
    @ui_guard_method( when_message = 'Call for displaying step form' )
    def op_add_sequence_step( self, *args: Tuple ) -> None:
        """ Call for view toggle of sequence step form """

        self.app_context.SequenceManager.toggle_step_form()


    @ui_guard_method( when_message = 'Call for creating new sequence' )
    def op_create_new_sequence( self, *args: Tuple ) -> None:
        """ Call for creation of new sequence """

        self.app_context.SequenceManager.create_new_sequence()


    @ui_guard_method( when_message = 'Call for aborting step editing' )
    def op_abort_add_sequence_step( self, *args: Tuple ) -> None:
        """ Call to hide step form, i.e. ending editing of step """

        self.app_context.SequenceManager.hide_step_form()


    @ui_guard_method( when_message = 'Call for aborting sequence editing' )
    def op_abort_sequence_edit( self, *args: Tuple ) -> None:
        """ Call to stop editing sequence """

        self.app_context.SequenceManager.abort_sequence_edit()


    @ui_guard_method( when_message = 'Call for deleting sequence' )
    def op_delete_sequence( self, *args: Tuple ) -> None:
        """ Call to delete sequence """

        self.app_context.SequenceManager.delete_sequence()


    @ui_guard_method( when_message = 'Call for start editing sequence' )
    def op_edit_sequence( self, *args: Tuple ) -> None:
        """ Call to edit selected sequence """

        self.app_context.SequenceManager.edit_sequence()


    @ui_guard_method( when_message = 'Call for deleting sequence step' )
    def op_remove_sequence_step( self, *args: Tuple ) -> None:
        """ Call to remove step from sequence """

        self.app_context.SequenceManager.remove_sequence_step()


    @ui_guard_method( when_message = 'Call for running sequence' )
    def op_run_sequence( self, *args: Tuple ) -> None:
        """ Call to run selected sequence """

        def on_finished() -> None:
            """ Callback function to run after execution """

            self.execution_post_work( disable_minimize = False, is_sequence = True )

        self.execution_pre_work( disable_minimize = False, is_sequence = True )

        self.app_context.SequenceManager.run_sequence( on_finished = on_finished )


    @ui_guard_method( when_message = 'Call for saving sequence' )
    def op_save_sequence( self, *args: Tuple ) -> None:
        """ Call to save sequence """

        self.app_context.SequenceManager.save_sequence()
    # endregion


    # region Progressbar API callbacks
    @ui_guard_method( when_message = 'API hide progressbar' )
    def hide_progress( self, *args: Tuple ) -> None:
        """ Hide execution progressbar """

        if self._progressbar_visible:
            self.status_widgets[ 'progressbar' ].grid_remove()
            self.status_widgets[ 'separator' ].grid_remove()
            self._progressbar_visible = False


    @ui_guard_method( when_message = 'API set progressbar determinate' )
    def set_progress_determined( self, *args: Tuple ) -> None:
        """ Set determined """

        if not self.status_widgets[ 'progressbar' ].winfo_ismapped():
            self.status_widgets[ 'progressbar' ].grid()

        self.status_widgets[ 'progressbar' ].config( mode = 'determinate' )
        self.status_widgets[ 'progressbar' ].stop()


    @ui_guard_method( when_message = 'API set progressbar indeterminate' )
    def set_progress_indetermined( self, *args: Tuple ) -> None:
        """ Set indetermined """

        if not self.status_widgets[ 'progressbar' ].winfo_ismapped():
            self.status_widgets[ 'progressbar' ].grid()

        self.status_widgets[ 'progressbar' ].start( interval = 10 )
        self.status_widgets[ 'progressbar' ].config( mode = 'indeterminate' )


    @ui_guard_method( when_message = 'API show progressbar' )
    def show_progress( self, *args: Tuple ) -> None:
        """ Show execution progressbar """

        if not self._progressbar_visible:
            self.status_widgets[ 'progressbar' ].grid()
            self._progressbar_visible = True


    @ui_guard_method( when_message = 'API update progressbar' )
    def update_progress( self, update_data: float | int | dict ) -> None:
        """ Update progressbar

        Args:
            update_data (float | int | dict): Precalculated value to set in the progressbar
        """

        new_percentage = 0

        if not self.status_widgets[ 'progressbar' ].master.winfo_ismapped():
            cast( Frame, self.status_widgets[ 'progressbar' ].master ).grid()

        if not self.status_widgets[ 'progressbar' ].winfo_ismapped():
            self.status_widgets[ 'progressbar' ].grid()

        if isinstance( update_data, ( float, int ) ):
            if update_data >= 100:
                new_percentage = 99.99999999999

            else:
                new_percentage = update_data

        else:
            if update_data[ 'percent' ] >= 100:
                new_percentage = 99.99999999999

            else:
                new_percentage = update_data[ 'percent' ]

        if not self._progressbar_visible:
            self.show_progress()

        self.status_widgets[ 'progressbar' ].config( value = new_percentage )

    # endregion


    # region Settings API callbacks
    @ui_guard_method( when_message = 'API setting retrieval' )
    def setting( self, key_dict: dict ) -> None:
        """ Return setting through the API

        Args:
            key_dict (dict): Dict for specifying setting to retrieve
        """

        runner = self.app_context.ExecutionManager.current_runner

        if runner is None:
            return

        setting = self._serialize_setting( key = key_dict[ 'key' ] )
        self.root.after( 10, lambda: runner.send_api_response( response = setting ) )

    # endregion Settings API callbacks


    # region Textstatus API callbacks
    @ui_guard_method( when_message = 'API clear status' )
    def clear_status( self, *args: Tuple ) -> None:
        """ Remove all statustext """

        self.status_widgets[ 'text_status' ].config( text = '' )


    @ui_guard_method( when_message = 'API get status' )
    def get_status( self, *args: Tuple ) -> None:
        """ Return current statustext """

        runner = self.app_context.ExecutionManager.current_runner

        if runner is None:
            return

        status = self.status_widgets[ 'text_status' ].cget( 'text' )
        self.root.after( 10, lambda: runner.send_api_response( response = status ) )


    @ui_guard_method( when_message = 'API get status' )
    def set_status( self, set_data: dict ) -> None:
        """ Set statustext

        Args:
            set_data (dict): Dictionary of what status to set
        """

        text: str = ''

        if set_data.get( 'append' ):
            text = self.status_widgets[ 'text_status' ].cget( 'text' ) + set_data[ 'set' ]

        else:
            text = set_data[ 'set' ]

        text = text.replace( '\r\n', ' ' )
        self.status_widgets[ 'text_status' ].config( text = text )

    # endregion
