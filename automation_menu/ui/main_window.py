"""
Create and manage main GUI window

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.models.application_state import ApplicationState

import logging
from tkinter import E, N, S, W, Event, Tk, messagebox, ttk
from typing import Tuple, Union

from automation_menu.api.script_api import MESSAGE_END, MESSAGE_START
from automation_menu.models.enums import OutputStyleTags, SysInstructions
from automation_menu.ui.async_output_controller import AsyncOutputController
from automation_menu.ui.config_ui_style import set_output_styles, set_ui_style
from automation_menu.ui.input_manager import InputManager
from automation_menu.ui.op_buttons import get_op_buttons
from automation_menu.ui.output_tab import get_output_tab
from automation_menu.ui.settings_tab import get_settings_tab
from automation_menu.ui.statusbar import get_statusbar
from automation_menu.filehandling.settings_handler import write_settingsfile


class AutomationMenuWindow:
    def __init__( self, app_state: ApplicationState, app_context: ApplicationContext ) -> None:
        """ Creates the main window

        Args:
            app_state (ApplicationState): State object for various application states
        """

        from automation_menu.utils.localization import _

        self.app_state = app_state
        self.app_context = app_context
        self.app_context.main_window = self
        self.settings_file_path = self.app_state.secrets.get( 'settings_file_path' )

        self.dev_controls = []
        self.old_window_geometry = {}
        self.widgets = {}
        self._blink_active = False
        self._blink_job = None
        self._blink_state = False
        self._close_confirmed = False
        self._progressbar_visible = False

        self.api_callbacks = {
            'determinate_progress': self.set_progress_determined,
            'hide_progress': self.hide_progress,
            'indeterminate_progress': self.set_progress_indetermined,
            'show_progress': self.show_progress,
            'update_progress': self.update_progress,

            'clear_status': self.clear_status,
            'get_status': self.get_status,
            'set_status': self.set_status
        }
        self.sequence_callbacks = {
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
        logging.basicConfig( level = logging.DEBUG )

        # Create main GUI
        self.root = Tk()
        self.root.title( string = self.app_state.secrets.get( 'mainwindowtitle' ) )

        self.app_context.input_manager = InputManager( root = self.root,
                                                      language_manager = self.app_context.language_manager
                                                      )

        # Setup styles
        self._style = ttk.Style()
        set_ui_style( style = self._style )

        self.button_margin = {
            'x': 5,
            'y': 5
        }

        # Create buttons for script operations
        self.op_buttons = get_op_buttons( self.root, self )

        # Add tabs
        self.tabControl = ttk.Notebook( master = self.root )
        self.tabControl.grid( column = 0, columnspan = 2, row = 2, sticky = ( N, S, E, W ) )

        # Create output
        self.tabOutput, self.tbOutput = get_output_tab( tabcontrol = self.tabControl, translate_callback = self.app_context.language_manager.add_translatable_widget )

        set_output_styles( self.tbOutput )

        self.sequence_tab = self.app_context.sequence_manager.create_sequence_tab( tabcontrol = self.tabControl, sequence_callbacks = self.sequence_callbacks, translate_callback = self.app_context.language_manager.add_translatable_widget )

        # Manage output
        self.output_controller = AsyncOutputController( output_queue = self.app_context.output_queue,
                                                       text_widget = self.tbOutput,
                                                       breakpoint_button = self.op_buttons[ 'btnContinueBreakpoint' ],
                                                       history_manager = self.app_context.history_manager,
                                                       api_callbacks = self.api_callbacks
                                                       )
        self.output_controller.start()

        # Create settings
        self.tabSettings = get_settings_tab( tabcontrol = self.tabControl, settings = self.app_state.settings, main_self = self )

        # Create history tab
        self.tabHistory = self.app_context.history_manager.get_history_tab( tabcontrol = self.tabControl, translate_callback = self.app_context.language_manager.add_translatable_widget )

        # Create statusbar
        self.status_widgets = get_statusbar( master_root = self.root )

        self.root.columnconfigure( index = 0, weight = 1 )
        self.root.columnconfigure( index = 1, weight = 0 )
        self.root.rowconfigure( index = 0, weight = 0 ) # Op buttons
        self.root.rowconfigure( index = 1, weight = 0 ) # Input frame
        self.root.rowconfigure( index = 2, weight = 1 ) # Notebook tabs
        self.root.rowconfigure( index = 3, weight = 0 ) # Status bar

        # Shortcuts bindings
        self.root.bind( '<Control-m>', self._open_script_menu )

        self.root.protocol( 'WM_DELETE_WINDOW', self.on_closing )
        self.center_screen()
        self.root.focus()
        self.root.mainloop()


    def _confirm_close_process( self ) -> bool:
        """ Should the running script be terminated before closing application """

        from automation_menu.utils.localization import _

        line = _( 'There is a script running. Do you want to terminate the script process before closing the application?' )
        answ = messagebox.askyesno(
            title = _( 'Script still runnning' ),
            message = line,
            parent = self.root
        )

        if answ:
            self._stop_script()

        return answ


    def _continue_breakpoint( self ) -> None:
        """ Reset application debug mode """

        self.app_state.running_automation.continue_breakpoint()
        self.op_buttons[ 'btnContinueBreakpoint' ].state( [ "disabled" ] )


    def _minimize_hide_controls( self ) -> None:
        """ Hide UI control widgets when window is minimized during script execution """

        self.tabControl.config( style = 'HiddenTabs.TNotebook' )
        self.op_buttons[ 'op_buttons_frame' ].grid_remove()
        self.status_widgets[ 'status_bar' ].grid_remove()


    def _minimize_show_controls( self ) -> None:
        """ Show all hidden UI control widgets when script execution has finished """

        self.tabControl.config( style = 'TNotebook' )
        self.op_buttons[ 'op_buttons_frame' ].grid()
        self.status_widgets[ 'status_bar' ].grid()


    def _open_script_menu( self, event: Event = None ) -> None:
        """ Open script menu with shortcut """

        self.op_buttons[ 'script_menu' ].show_popup_menu()


    def _on_language_change( self, new_lang: str ) -> None:
        """ Eventhandler for when application changes by the user

        Args:
            new_lang (str): The new language to change to
        """

        self.app_state.settings.current_language = new_lang
        write_settingsfile( settings = self.app_state.settings, settings_file_path = self.settings_file_path )


    def _pause_resume_script( self ) -> None:
        """ Pause script execution """

        from automation_menu.utils.localization import _

        if self.app_context.execution_manager.is_paused():
            if self.app_context.execution_manager.resume_current_script():
                self.app_context.output_queue.put( { 'line': _( 'Process was resumed' ), 'tag': OutputStyleTags.SYSINFO } )
                self.op_buttons[ 'btnPauseResumeScript' ].config( text = _( 'Pause' ) )

                self._blink_active = False
                self.stop_pause_button_blinking()

        else:
            if self.app_context.execution_manager.pause_current_script():
                self.app_context.output_queue.put( { 'line': _( 'Process was paused' ), 'tag': OutputStyleTags.SYSINFO } )
                self.op_buttons[ 'btnPauseResumeScript' ].config( text = _( 'Resume' ) )
                self._blink_active = True
                self._pause_button_blinking()


    def _pause_button_blinking( self ) -> None:
        """ Initiate blinking effect of pause button during breakpoint pause """

        if not self._blink_active:
            return

        button = self.op_buttons[ 'btnPauseResumeScript' ]
        self._blink_state = not self._blink_state

        self.root.after( 100, lambda: button.config( style = 'BlinkBg.TButton' if self._blink_state else 'TButton' ) )
        self.root.update_idletasks()

        self._blink_job = self.root.after( 600, self._pause_button_blinking )


    def _stop_script( self ) -> None:
        """ Eventhandler for when user clicks button stop script """

        self.app_context.execution_manager.stop_current_script()
        self.stop_pause_button_blinking()


    def center_screen( self ) -> None:
        """ Center main window on screen """

        self.root.update_idletasks()
        width = self.root.winfo_width()
        frm_width = self.root.winfo_rootx() - self.root.winfo_x()
        win_width = width + 2 * frm_width
        height = self.root.winfo_height()
        titlebar_height = self.root.winfo_rooty() - self.root.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.root.winfo_screenwidth() // 2 - win_width // 2
        y = self.root.winfo_screenheight() // 2 - win_height // 2
        self.root.geometry( newGeometry = f'{ width }x{ height }+{ x }+{ y }' )


    def execution_post_work( self, disable_minimize: bool = False, is_sequence: bool = False ) -> None:
        """ Reset UI and controls after script/sequence execution """

        self.disable_pause_script_button()
        self.disable_stop_script_button()

        if self.app_state.settings.get( 'minimize_on_running' ) and not disable_minimize:
            self.min_max_on_running()

        self._minimize_show_controls()


    def execution_pre_work( self, disable_minimize: bool = False, is_sequence: bool = False ) -> None:
        """ Set UI and controls according to preferences before execution """

        from automation_menu.utils.localization import _

        self.tabControl.select( 0 )
        self._minimize_hide_controls()
        self.app_context.output_queue.put( SysInstructions.CLEAROUTPUT )
        self.app_context.input_manager.hide_input_frame()

        if self.app_state.settings.get( 'minimize_on_running' ):
            if disable_minimize:
                self.app_context.output_queue.put( {
                    'line': _( 'The script has \'DisableMinimizeOnRunning\', meaning the window will not be minimized.' ),
                    'tag': OutputStyleTags.SYSINFO
                } )

            else:
                old_geometry = {
                    'h': self.root.winfo_height(),
                    'w': self.root.winfo_width(),
                    'x': self.root.winfo_x(),
                    'y': self.root.winfo_y()
                }
                self.min_max_on_running( old_geometry )


    def on_closing( self ) -> None:
        """ Window close event. Handle if a script is still running """

        if not self._close_confirmed and self.app_context.execution_manager.is_running():
            if not self._confirm_close_process():
                return

        write_settingsfile( settings = self.app_state.settings, settings_file_path = self.app_state.secrets.get( 'settings_file_path' ) )

        if hasattr( self, 'output_controller' ):
            self.output_controller.closedown()

        self.root.destroy()


    def set_current_language( self, event: Event ) -> None:
        """ Change the language in the application

        Args:
            event: Event actualizing the function
        """

        self.app_state.settings.current_language = event.widget.get()
        self.app_context.language_manager.change_language( new_language = event.widget.get() )


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


    def min_max_on_running( self, old_geometry: dict = None ) -> None:
        """ Resize window during script execution

        Args:
            old_geometry (dict): Size values of main window before script execution
        """

        win_width = 400
        win_height = 200

        if old_geometry:
            self.old_window_geometry = old_geometry
            self._minimize_hide_controls()
            self.root.geometry( newGeometry = f'{ win_width }x{ win_height }+{ self.root.winfo_screenwidth() - win_width  }+{ self.root.winfo_screenheight() - win_height - 100 }' )

        else:
            self.root.geometry( newGeometry = f'{ self.old_window_geometry['w'] }x{ self.old_window_geometry['h'] }+{ self.old_window_geometry['x'] }+{ self.old_window_geometry['y'] }' )
            self._minimize_show_controls()

        self.root.update_idletasks()


    def set_on_top( self, new_value: bool ) -> None:
        """ Save setting to user_settings and set/unset the window as top most

        Args:
            new_value (bool): New value to set and save
        """

        self.app_state.settings.on_top = new_value
        self.root.focus_force()
        self.root.attributes( '-topmost', new_value )


    # region Button ops
    def enable_breakpoint_button( self ) -> None:
        """ Enable the breakpoint button """

        self.op_buttons[ 'btnContinueBreakpoint' ].state( [ '!disabled' ] )


    def enable_pause_script_button( self ) -> None:
        """ Enable the stop script button """

        self.op_buttons[ 'btnPauseResumeScript' ].state( [ '!disabled' ] )


    def disable_pause_script_button( self ) -> None:
        """ Enable the stop script button """

        from automation_menu.utils.localization import _

        self.op_buttons[ 'btnPauseResumeScript' ].state( [ 'disabled' ] )
        self.op_buttons[ 'btnPauseResumeScript' ].config( text = _( 'Pause' ) )


    def enable_stop_script_button( self ) -> None:
        """ Enable the stop script button """

        self.op_buttons[ 'btnStopScript' ].state( [ '!disabled' ] )


    def disable_stop_script_button( self ) -> None:
        """ Disable the stop script button """

        self.op_buttons[ 'btnStopScript' ].state( [ 'disabled' ] )
        self._pause_button_blinking()


    def stop_pause_button_blinking( self ) -> None:
        """ Stop blinking effect for button when script execution continues """

        self._blink_active = False

        if self._blink_job:
            self.root.after_cancel( self._blink_job )
            self._blink_job = None
    # endregion


    # region Sequence UI ops
    def op_add_sequence_step( self, *args: Tuple ) -> None:
        """ Call for view toggle of sequence step form """

        self.app_context.sequence_manager.toggle_step_form()


    def op_create_new_sequence( self, *args: Tuple ) -> None:
        """ Call for creation of new sequence """

        self.app_context.sequence_manager.create_new_sequence()


    def op_abort_add_sequence_step( self, *args: Tuple ) -> None:
        """ Call to hide step form, i.e. ending editing of step """

        self.app_context.sequence_manager.hide_step_form()


    def op_abort_sequence_edit( self, *args: Tuple ) -> None:
        """ Call to stop editing sequence """

        self.app_context.sequence_manager.abort_sequence_edit()


    def op_delete_sequence( self, *args: Tuple ) -> None:
        """ Call to delete sequence """

        self.app_context.sequence_manager.delete_sequence()


    def op_edit_sequence( self, *args: Tuple ) -> None:
        """ Call to edit selected sequence """

        self.app_context.sequence_manager.edit_sequence()


    def op_remove_sequence_step( self, *args: Tuple ) -> None:
        """ Call to remove step from sequence """

        self.app_context.sequence_manager.remove_sequence_step()


    def op_run_sequence( self, *args: Tuple ) -> None:
        """ Call to run selected sequence """

        def on_finished() -> None:
            """ Callback function to run after execution """

            self.execution_post_work( disable_minimize = False, is_sequence = True )

        self.execution_pre_work( disable_minimize = False, is_sequence = True )

        self.app_context.sequence_manager.run_sequence( on_finished = on_finished )


    def op_save_sequence( self, *args: Tuple ) -> None:
        """ Call to save sequence """

        self.app_context.sequence_manager.save_sequence()
    # endregion


    # region Progressbar API callbacks
    def hide_progress( self, *args: Tuple ) -> None:
        """ Hide execution progressbar """

        if self._progressbar_visible:
            self.status_widgets[ 'progressbar' ].grid_remove()
            self.status_widgets[ 'separator' ].grid_remove()
            self._progressbar_visible = False


    def set_progress_determined( self, *args: Tuple ) -> None:
        """ Set indetermined """

        self.status_widgets[ 'progressbar' ].config( mode = 'determinate' )
        self.status_widgets[ 'progressbar' ].stop()


    def set_progress_indetermined( self, *args: Tuple ) -> None:
        """ Set indetermined """

        self.status_widgets[ 'progressbar': Tuple ].start( interval = 10 )
        self.status_widgets[ 'progressbar': Tuple ].config( mode = 'indeterminate' )


    def show_progress( self, *args: Tuple ) -> None:
        """ Show execution progressbar """

        if not self._progressbar_visible:
            self.status_widgets[ 'progressbar' ].grid()
            self.status_widgets[ 'separator' ].grid()
            self._progressbar_visible = True


    def update_progress( self, update_data: Union[ float, int, dict ] ) -> None:
        """ Update progressbar

        Args:
            percent (float): Precalculated value to set in the progressbar
        """

        new_percentage = 0

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


    # region Textstatus API callbacks
    def clear_status( self, *args: Tuple ) -> None:
        """ Remove all statustext """

        self.status_widgets[ 'text_status' ].config( text = '' )


    def get_status( self, *args: Tuple ) -> None:
        """ Return current statustext """

        def _send_status() -> None:
            """ Return current status text """

            if self.app_context.execution_manager.current_runner:
                status = self.status_widgets[ 'text_status' ].cget( 'text' )
                msg = f'{ MESSAGE_START }{ status }{ MESSAGE_END }\n'

                try:
                    self.app_context.execution_manager.current_runner.current_process.stdin.write( msg )
                    self.app_context.execution_manager.current_runner.current_process.stdin.flush()

                except:
                    pass

        self.root.after( 10, _send_status )


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
