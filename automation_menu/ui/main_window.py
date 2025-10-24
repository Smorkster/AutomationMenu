"""
Create and manage main GUI window

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from tkinter import E, N, S, W, Tk, messagebox, ttk

from automation_menu.core.script_menu_item import ScriptMenuItem
from automation_menu.core.application_state import ApplicationState
from automation_menu.models.enums import OutputStyleTags
from automation_menu.ui.async_output_controller import AsyncOutputController
from automation_menu.ui.config_ui_style import set_output_styles, set_ui_style
from automation_menu.ui.op_buttons import get_op_buttons
from automation_menu.ui.output_tab import get_output_tab
from automation_menu.ui.settings_tab import get_settings_tab
from automation_menu.utils.language_manager import LanguageManager
from automation_menu.filehandling.settings_handler import write_settingsfile


class AutomationMenuWindow:
    def __init__( self, app_state: ApplicationState ):
        """ Creates the main window

        Args:
            app_state (ApplicationState): State object for various application states
        """

        from automation_menu.utils.localization import _

        self.app_state = app_state
        self.settings_file_path = self.app_state.secrets.get( 'settings_file_path' )
        self.dev_controls = []
        self.widgets = {}
        self.old_window_geometry = {}
        self._blink_active = False
        self._blink_job = None
        self._blink_state = False
        self._close_confirmed = False
        self.language_manager = LanguageManager( current_language = self.app_state.settings.current_language )

        # Create main GUI
        self.root = Tk()
        self.root.title( string = self.app_state.secrets.get( 'mainwindowtitle' ) )

        # Setup styles
        style = ttk.Style()
        set_ui_style( style = style, main_window = self.root )

        self.button_margin = {
            'x': 5,
            'y': 5
        }

        self.op_buttons = get_op_buttons( self.root, self )

        # Add tabs
        self.tabControl = ttk.Notebook( master = self.root )
        self.tabControl.grid( column = 0 , columnspan = 2 , row = 1, sticky = ( N, S, E, W ) )

        # Create output
        self.tabOutput, self.tbOutput = get_output_tab( tabcontrol = self.tabControl )
        self.tabOutput.grid( sticky = ( N, S, E, W ) )
        self.tabControl.add( child = self.tabOutput, text = _( 'Script output' ) )

        set_output_styles( self.tbOutput )

        # Manage output
        self.output_controller = AsyncOutputController(
                                    output_queue = self.app_state.output_queue,
                                    text_widget = self.tbOutput ,
                                    breakpoint_button = self.op_buttons[ 'btnContinueBreakpoint' ],
                                    history_manager = self.app_state.history_manager )
        self.output_controller.start()

        # Create settings
        self.tabSettings = get_settings_tab( tabcontrol = self.tabControl, settings = self.app_state.settings, main_self = self )
        self.tabSettings.grid( sticky = ( N, S, E, W ) )
        self.tabControl.add( child = self.tabSettings, text = _( 'Settings' ) )

        # Create history tab
        self.tabHistory = self.app_state.history_manager.get_history_tab( tabcontrol = self.tabControl, main_self = self )
        self.tabControl.add( child = self.tabHistory, text = _( 'Execution history' ) )

        self.language_manager.add_translatable_widget( ( self.tabControl, ( 'Script output', 'Settings', 'Execution history' ) ) )

        self.center_screen()

        self.root.columnconfigure( index = 0, weight = 1 )
        self.root.columnconfigure( index = 1, weight = 0 )
        self.root.rowconfigure( index = 0, weight = 0 )
        self.root.rowconfigure( index = 0, weight = 0 )
        self.root.rowconfigure( index = 1, weight = 1 )
        self.root.rowconfigure( index = 2, weight = 0 )
        self.root.rowconfigure( index = 2, weight = 0 )

        self.root.protocol( 'WM_DELETE_WINDOW', self.on_closing )
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

        if self.app_state.script_manager.is_paused():
            if self.app_state.script_manager.resume_current_script():
                self.app_state.output_queue.put( { 'line': _( 'Process was resumed' ), 'tag': OutputStyleTags.SYSINFO } )
                self.op_buttons[ 'btnPauseResumeScript' ].config( text = _( 'Pause' ) )

                self._blink_active = False
                self.stop_pause_button_blinking()

        else:
            if self.app_state.script_manager.pause_current_script():
                self.app_state.output_queue.put( { 'line': _( 'Process was paused' ), 'tag': OutputStyleTags.SYSINFO } )
                self.op_buttons[ 'btnPauseResumeScript' ].config( text = _( 'Resume' ) )
                self._blink_active = True
                self._pause_button_blinking()


    def _pause_button_blinking( self ):
        """ """

        if not self._blink_active:
            return

        button = self.op_buttons[ 'btnPauseResumeScript' ]
        self._blink_state = not self._blink_state

        self.root.after( 100, lambda: button.config( style = 'BlinkBg.TButton' if self._blink_state else 'TButton' ) )
        self.root.update_idletasks()

        self._blink_job = self.root.after( 600, self._pause_button_blinking )


    def stop_pause_button_blinking( self ):
        """ """

        self._blink_active = False

        if self._blink_job:
            self.root.after_cancel( self._blink_job )
            self._blink_job = None


    def _stop_script( self ) -> None:
        """ Eventhandler for when user clicks button stop script """

        self.app_state.script_manager.stop_current_script()
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


    def on_closing( self ) -> None:
        """ Window close event. Handle if a script is still running """

        if not self._close_confirmed and self.app_state.script_manager.is_running():
            if not self._confirm_close_process():
                return

        write_settingsfile( settings = self.app_state.settings, settings_file_path = self.app_state.secrets.get( 'settings_file_path' ) )

        if hasattr( self, 'output_controller' ):
            self.output_controller.closedown()

        self.root.destroy()


    def set_current_language( self, event ) -> None:
        """ Change the language in the application

        Args:
            event: Event actualizing the function
        """

        self.app_state.settings.current_language = event.widget.get()
        self.language_manager.change_language( new_language = event.widget.get() )


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


    def set_min_max_on_running( self, old_geometry: dict = None ) -> None:
        """ Resize window during script execution

        Args:
            old_geometry (dict): Size values of main window before script execution
        """

        win_width = 400
        win_height = 200

        if old_geometry:
            self.old_window_geometry = old_geometry
            self.root.geometry( newGeometry = f'{ win_width }x{ win_height }+{ self.root.winfo_screenwidth() - win_width  }+{ self.root.winfo_screenheight() - win_height - 100 }' )

        else:
            self.root.geometry( newGeometry = f'{ self.old_window_geometry['w'] }x{ self.old_window_geometry['h'] }+{ self.old_window_geometry['x'] }+{ self.old_window_geometry['y'] }' )

        self.root.update_idletasks()


    def set_on_top( self, new_value: bool ) -> None:
        """ Save setting to user_settings and set/unset the window as top most

        Args:
            new_value (bool): New value to set and save
        """

        self.app_state.settings.on_top = new_value
        self.root.focus_force()
        self.root.attributes( '-topmost', new_value )
