"""
Object representing a script
Contains script info and a runner

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-09-25
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from automation_menu.ui.main_window import AutomationMenuWindow

import logging
import threading

from tkinter import Event, Toplevel
from tkinter.ttk import Label
from automation_menu.models import ScriptInfo, SysInstructions
from automation_menu.models.enums import OutputStyleTags, ScriptState


class ScriptMenuItem:
    def __init__ ( self, script_menu: Toplevel, script_info: ScriptInfo, main_object: AutomationMenuWindow, menu_hide_callback: Callable ) -> None:
        """ Object for representing a script in the menu

        Args:
            script_menu (Menu): Menu widget to attach menu item to
            script_info (ScriptInfo): Information about the script
            main_object (AutomationMenuWindow): The main window
        """

        from automation_menu.utils.localization import _

        logging.basicConfig( level = logging.DEBUG )

        self.script_menu = script_menu
        self.script_info = script_info
        self.script_path = script_info.get_attr( 'fullpath' )
        self.master_self = main_object
        self._hide_menu = menu_hide_callback

        self.master_self.app_state.running_automation = self
        self.process = None
        self.label_text = ''
        self._in_debug = False

        if self.script_info.get_attr( 'synopsis' ):
            self.label_text = self.script_info.get_attr( 'synopsis' )

        else:
            self.label_text = self.script_info.get_attr( 'filename' )

        self._style_normal = 'ScriptNormal.TLabel'
        self._style_hover = 'ScriptHover.TLabel'

        if self.script_info.filename.startswith( 'AMTest_' ):
            self._style_normal = 'AppTestNormal.TLabel'
            self._style_hover = 'AppTestHover.TLabel'

        elif self.script_info.get_attr( 'state' ) == ScriptState.DEV:
            self.label_text = self.label_text + _( ' (Dev)' )
            self._style_normal = 'DevNormal.TLabel'
            self._style_hover = 'DevHover.TLabel'

        self.menu_button = Label( self.script_menu, text = self.label_text, style = self._style_normal, borderwidth = 1 )
        self.menu_button.bind( '<Button-1>' , lambda e: self._check_input_params() )

        # Add tooltip to this button
        if self.script_info.get_attr( 'description' ):
            from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip

            desc = self.script_info.get_attr( 'description' )
            dev = False
            app_test = False

            if self.script_info.get_attr( 'state' ) == ScriptState.DEV:
                desc += f'\n\n{ _( 'In development, and should only be run by its developer.' ) }'
                dev = True

            if self.script_info.filename.startswith( 'AMTest_' ):
                desc += f'\n\n{ _( 'Application test script, only used to test application functionality' ) }'
                app_test = True

            tt = AlwaysOnTopToolTip( widget = self.menu_button, msg = desc, delay = 0 )
            self.master_self.app_context.language_manager.add_translatable_widget( ( tt, self.script_info.get_attr( 'description' ), dev, app_test ) )


    def _check_input_params( self ) -> None:
        """ Verify if script takes input and if widgets are created """

        self._hide_menu()

        if len( self.script_info.scriptmeta.script_input_parameters ) > 0:
            self.master_self.app_context.input_manager.show_for_script( script_info = self.script_info, submit_input_callback = self.run_script )

        else:
            self.run_script()


    def continue_breakpoint( self ) -> None:
        """ Continue execution of the script after hitting a breakpoint """

        self.process.stdin.write( 'c\n' )
        self.process.stdin.flush()
        self.master_self.btnContinueBreakpoint.after( 0, self.master_self.enable_breakpoint_button() )
        self._in_debug = False


    def on_enter( self, event: Event ) -> None:
        """ Change label background on mouse enter

        Args:
            event: Event triggering the function
        """

        event.widget.configure( style = self._style_hover )


    def on_leave( self, event: Event ) -> None:
        """ Change label background on mouse leave

        Args:
            event: Event triggering the function
        """

        event.widget.configure( style = self._style_normal )


    def run_script( self ) -> None:
        """ Initiate script execution """

        from automation_menu.utils.localization import _

        def script_process_wrapper() -> None:
            """ Wrapper to execute script from separate thread """

            with self.master_self.app_context.execution_manager.create_runner() as runner:
                runner.run_script( script_info = self.script_info,
                                   main_window = self.master_self.root,
                                   api_callbacks = self.master_self.api_callbacks,
                                   enable_stop_button_callback = self.master_self.enable_stop_script_button,
                                   enable_pause_button_callback = self.master_self.enable_pause_script_button,
                                   stop_pause_button_blinking_callback = self.master_self.stop_pause_button_blinking,
                                   run_input = self.entered_input
                                 )

            self.master_self.execution_post_work( disable_minimize = disable_minimize )

        self.entered_input = self.master_self.app_context.input_manager.collect_entered_input()
        disable_minimize = self.script_info.scriptmeta.disable_minimize_on_running

        self.master_self.execution_pre_work( disable_minimize = disable_minimize )

        threading.Thread( target = script_process_wrapper, daemon = True ).start()
