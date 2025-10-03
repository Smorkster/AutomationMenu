"""
Create and manage main GUI window

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import asyncio
import threading
from tkinter import E, N, S, W, Tk, ttk

from automation_menu.core.script_discovery import get_scripts
from automation_menu.core.script_runner import ScriptMenuItem
from automation_menu.core.state import ApplicationState
from automation_menu.ui.custom_menu import CustomMenu
from automation_menu.ui.async_output_controller import AsyncOutputController
from automation_menu.ui.output_tab import get_output_tab
from automation_menu.ui.settings_tab import get_settings_tab
from automation_menu.utils.language_manager import LanguageManager
from automation_menu.utils.config import write_settingsfile

class AutomationMenuWindow:
    def __init__( self, app_state: ApplicationState ):
        from automation_menu.utils.localization import _

        self.app_state = app_state
        self.settings_file_path = self.app_state.secrets.get( 'settings_file_path' )
        self.dev_controls = []
        self.widgets = {}
        self.language_manager = LanguageManager( current_language = self.app_state.settings.current_language )

        # Create main GUI
        self.root = Tk()
        self.root.title( string = self.app_state.secrets.get( 'mainwindowtitle' ) )

        style = ttk.Style()
        style.configure( 'Script.TLabel',
                        font = ( 'Calibri', 12, 'normal' ),
                        relief = 'flat',
                        )
        style.configure( 'Dev.TLabel',
                        font = ( 'Calibri', 12, 'bold' ),
                        relief = 'flat',
                        )

        # Add tabs
        self.tabControl = ttk.Notebook( master = self.root )
        self.tabControl.grid( column = 0 , columnspan = 2 , row = 1, sticky = ( N, S, E, W ) )

        # Add Op buttons
        self.op_buttons_frame = ttk.Frame( master = self.root )
        self.op_buttons_frame.grid( columnspan = 2, row = 2, sticky = ( S, W, E ) )

        self.btnContinueBreakpoint = ttk.Button( master = self.op_buttons_frame, text = _( 'Continue' ), command = self._continue_breakpoint )
        self.btnContinueBreakpoint.state( [ "disabled" ] )
        self.btnContinueBreakpoint.grid( column = 1, row = 0, pady = 0, sticky = ( E, S ) )
        self.language_manager.add_translatable_widget( ( self.btnContinueBreakpoint, 'Continue' ) )

        self.btnStopScript = ttk.Button( master = self.op_buttons_frame, text = _( 'Stop script' ), command = self._stop_script )
        self.btnStopScript.state( [ "disabled" ] )
        self.btnStopScript.grid( column = 0, row = 0, pady = 0, sticky = ( E, S ) )
        self.language_manager.add_translatable_widget( ( self.btnStopScript, 'Stop script' ) )

        self.op_buttons_frame.grid_columnconfigure( 0 , weight = 0 )
        self.op_buttons_frame.grid_columnconfigure( 1 , weight = 0 )

        # Create output
        self.tabOutput, self.tbOutput = get_output_tab( tabcontrol = self.tabControl )
        self.tabOutput.grid( sticky = ( N, S, E, W ) )
        self.tabControl.add( child = self.tabOutput, text = _( 'Script output' ) )

        # Manage output
        self.output_controller = AsyncOutputController( output_queue = self.app_state.output_queue, text_widget = self.tbOutput , breakpoint_button = self.btnContinueBreakpoint )
        self.output_controller.start()

        # Add a custom menu
        self.script_list = get_scripts( app_state = self.app_state )
        scriptswithbreakpoint = [ s for s
                                 in self.script_list
                                 if s.get_attr( 'UsingBreakpoint' ) ]
        if len( scriptswithbreakpoint ) > 0:
            line = _( 'Some script have an active breakpoint in the code, handling this has not been implemented and these will not be available:' )
            self.app_state.output_queue.put( { 'line': line , 'tag': 'suite_sysinfo' } )
            self.app_state.output_queue.put( { 'line': ', '.join( [ script.get_attr( 'filename' ) for script in scriptswithbreakpoint ] ) , 'tag': 'suite_sysinfo' } )

        self.custom_menu = CustomMenu( parent = self.root, text = _( 'Script ...' ), scripts = self.script_list , main_object = self )
        self.language_manager.add_translatable_widget( ( self.custom_menu.menu_button, 'Script ...' ) )

        # Create settings
        self.tabSettings = get_settings_tab( tabcontrol = self.tabControl, settings = self.app_state.settings, main_object = self )
        self.tabSettings.grid( sticky = ( N, S, E, W ) )
        self.tabControl.add( child = self.tabSettings, text = _( 'Settings' ) )

        self.language_manager.add_translatable_widget( ( self.tabControl, ( 'Script output', 'Settings' ) ) )

        self.center_screen()

        self.tabOutput.columnconfigure( index = 0, weight = 1 )
        self.tabOutput.columnconfigure( index = 1, weight = 0 )
        self.tabOutput.rowconfigure( index = 0, weight = 1 )
        self.root.columnconfigure( index = 0, weight = 1 )
        self.root.columnconfigure( index = 1, weight = 0 )
        self.root.rowconfigure( index = 0, weight = 0 )
        self.root.rowconfigure( index = 1, weight = 1 )
        self.root.rowconfigure( index = 2, weight = 0 )

        self.root.protocol( 'WM_DELETE_WINDOW', self.on_closing )
        self.root.mainloop()

    def _continue_breakpoint( self ):
        """ Reset application debug mode """

        self.app_state.running_automation.continue_breakpoint()
        self.btnContinueBreakpoint.state( [ "disabled" ] )

    def _on_language_change( self, old_lang: str, new_lang: str ):
        self._update_ui_text()

        self.app_state.settings.current_language = new_lang
        write_settingsfile( settings = self.app_state.settings, settings_file_path = self.settings_file_path )

    def _stop_script( self ):

        self.app_state.script_manager.stop_current_script()

    def _update_settings_tab_text( self ):
        if hasattr( self, 'settings_widgets' ):
            self.settings_widgets[ '' ]

    def center_screen( self ):
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
 
    def create_script_controls( self ):
        """ Create menuitems for each script and set grid information for window """

        from automation_menu.utils.localization import _

        for scriptinfo in sorted( self.indexed_files , key = lambda script: getattr( script, 'Synopsis', getattr( script, 'filename', '' ) ).lower() ):
            if hasattr( scriptinfo, 'NoScriptBlock' ):
                line = _( 'File {file} does not contain a ScriptInfo-block. Some settings will be ignored.' ).format( file = scriptinfo.fullpath )
                self.app_state.output_queue.put( { 'line': line, 'tag': 'suite_sysinfo' } )
            ScriptMenuItem( script_menu = self.script_menu, script_info = scriptinfo, main_object = self )

    def enable_breakpoint_button( self ):
        """ Enable the breakpoint button """

        self.btnContinueBreakpoint.state( [ '!disabled' ] )

    def enable_stop_script_button( self ):
        """ Enable the stop script button """

        self.btnStopScript.state( [ '!disabled' ] )

    def disable_stop_script_button( self ):
        """ Disable the stop script button """

        self.btnStopScript.state( [ 'disabled' ] )

    def on_closing( self ):
        """ Handle the window close event """

        write_settingsfile( settings = self.app_state.settings, settings_file_path = self.app_state.secrets.get( 'settings_file_path' ) )
        self.root.destroy()

    def set_current_language( self, event ):
        """ Change the language in the application """

        self.app_state.settings.current_language = event.widget.get()
        self.language_manager.change_language( new_language = event.widget.get() )

    def set_display_dev( self ):
        """ Show or hide developer controls based on the checkbox state

            To be implemented
        """
        return

    def set_include_ss_in_error_mail( self, new_value: bool ):
        """ Save setting to user_settings """

        self.app_state.settings.include_ss_in_error_mail = new_value

    def set_minimize_on_running( self, new_value: bool ):
        """ Save data of mainwindow position and size from when the setting is set """

        self.app_state.settings.minimize_on_running = new_value
        self.old_window_geometry = {
            'h': self.root.winfo_height(),
            'w': self.root.winfo_width(),
            'x': self.root.winfo_x(),
            'y': self.root.winfo_y()
        }

    def set_on_top( self, new_value: bool ):
        """ Set the window as top most """

        self.app_state.settings.on_top = new_value
        self.root.focus_force()
        self.root.attributes( '-topmost', new_value )

