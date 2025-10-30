"""
Object representing a script
Contains script info and a runner

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

import threading
from tkinter import Menu
from tkinter.ttk import Label
from automation_menu.models import ScriptInfo, SysInstructions
from automation_menu.models.enums import OutputStyleTags, ScriptState
#from automation_menu.ui.main_window import AutomationMenuWindow


class ScriptMenuItem:
#    def __init__ ( self, script_menu: Menu, script_info: ScriptInfo, main_object: AutomationMenuWindow ):
    def __init__ ( self, script_menu: Menu, script_info: ScriptInfo, main_object ):
        """ Object for representing a script in the menu

        Args:
            script_menu (Menu): Menu widget to attach menu item to
            script_info (ScriptInfo): Information about the script
            main_object (AutomationMenuWindow): The main window
        """

        from automation_menu.utils.localization import _

        self.script_menu = script_menu
        self.script_info = script_info
        self.script_path = script_info.get_attr( 'fullpath' )
        self.master_self = main_object
        self.master_self.app_state.running_automation = self
        self.process = None
        self.label_text = ''
        self._in_debug = False
        style = 'TButton'

        if self.script_info.get_attr( 'synopsis' ):
            self.label_text = self.script_info.get_attr( 'synopsis' )

        else:
            self.label_text = self.script_info.get_attr( 'filename' )

        if self.script_info.get_attr( 'state' ) == ScriptState.DEV:
            self.label_text = self.label_text + _( ' (Dev)' )
            style = 'DevNormal.TLabel'

        else:
            style = 'ScriptNormal.TLabel'

        self.script_button = Label( self.script_menu, text = self.label_text, style = style, borderwidth = 1 )
        self.script_button.bind( '<Button-1>' , lambda e: self.run_script() )

        # Add tooltip to this button
        if self.script_info.get_attr( 'description' ):
            from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip

            desc = self.script_info.get_attr( 'description' )
            dev = False

            if self.script_info.get_attr( 'state' ) == ScriptState.DEV:
                desc += f'\n\n{ _( 'In development, and should only be run by its developer.' ) }'
                dev = True

            tt = AlwaysOnTopToolTip( widget = self.script_button, msg = desc )
            self.master_self.language_manager.add_translatable_widget( ( tt, self.script_info.get_attr( 'description' ), dev ) )


    def on_enter( self, event ):
        """ Change label background on mouse enter

        Args:
            event: Event triggering the function
        """

        if self.script_info.get_attr( 'state' ) == ScriptState.DEV:
            event.widget.configure( style = 'DevHover.TLabel' )

        else:
            event.widget.configure( style = 'ScriptHover.TLabel' )


    def on_leave( self, event ):
        """ Change label background on mouse leave

        Args:
            event: Event triggering the function
        """

        if self.script_info.get_attr( 'state' ) == ScriptState.DEV:
            event.widget.configure( style = 'DevNormal.TLabel' )

        else:
            event.widget.configure( style = 'ScriptNormal.TLabel' )


    def continue_breakpoint( self ):
        """ Continue execution of the script after hitting a breakpoint """

        self.process.stdin.write( 'c\n' )
        self.process.stdin.flush()
        self.master_self.btnContinueBreakpoint.after( 0, self.master_self.enable_breakpoint_button() )
        self._in_debug = False


    def run_script( self ):
        """ Initiate script execution """

        from automation_menu.utils.localization import _

        def script_process_wrapper():
            """ Wrapper to execute script from separate thread """

            with self.master_self.app_state.script_manager.create_runner() as runner:
                runner.run_script( script_info = self.script_info,
                                   enable_stop_button_callback = self.master_self.enable_stop_script_button,
                                   main_window = self.master_self.root,
                                   api_callbacks = self.master_self.api_callbacks
                                 )

            self.master_self.disable_stop_script_button()
            self.master_self.disable_pause_script_button()

            if self.master_self.app_state.settings.get( 'minimize_on_running' ) and not self.script_info.get_attr( 'disable_minimize_on_running' ):
                self.master_self.set_min_max_on_running()

        self.script_menu.withdraw()
        self.master_self.tabControl.select( 0 )
        self.master_self.app_state.output_queue.put( SysInstructions.CLEAROUTPUT )

        if self.master_self.app_state.settings.get( 'minimize_on_running' ):
            if self.script_info.get_attr( 'disable_minimize_on_running' ):
                self.master_self.app_state.output_queue.put( {
                    'line': _( 'The script has \'DisableMinimizeOnRunning\', meaning the window will not be minimized.' ),
                    'tag': OutputStyleTags.SYSINFO
                } )

            else:
                old_geometry = {
                    'h': self.master_self.root.winfo_height(),
                    'w': self.master_self.root.winfo_width(),
                    'x': self.master_self.root.winfo_x(),
                    'y': self.master_self.root.winfo_y()
                }
                self.master_self.set_min_max_on_running( old_geometry )

        threading.Thread( target = script_process_wrapper, daemon = True ).start()
