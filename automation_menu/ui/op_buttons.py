"""
Create a frame containing some buttons
to manage script execution process

Author: Smorkster
GitHub:
License: MIT
Version: 1.0.0
Created: 2025-09-25
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.ui.main_window import AutomationMenuWindow

from tkinter import E, N, S, W, Tk
from tkinter.ttk import Button, Frame

from automation_menu.ui.custom_menu import CustomMenu


def get_op_buttons( main_root: Tk, main_self: AutomationMenuWindow ) -> dict:
    """ Create a frame to contain buttons for operations during script execution

    Args:
        main_root (Tk): Main window
        main_self (AutomationMenuWindow): Main object
    """

    from automation_menu.utils.localization import _

    widgets = {}

    op_buttons_frame = Frame( master = main_root )
    op_buttons_frame.grid( columnspan = 2, row = 0, sticky = ( N, W, E ) )

    widgets[ 'op_buttons_frame' ] = op_buttons_frame

    col = 0

    menu_frame = Frame( master = op_buttons_frame )
    menu_frame.grid()
    menu_frame.grid_columnconfigure( index = 0, weight = 0 )
    menu_frame.grid_columnconfigure( index = 1, weight = 0 )
    widgets[ 'menu_frame' ] = menu_frame

    # Add a custom menu for scripts
    script_menu = CustomMenu( parent = menu_frame, text = _( 'Script ...' ), exec_list = main_self.app_context.script_manager.get_script_list() , main_object = main_self )
    script_menu.menu_button.grid( column = 0, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = ( N, W ) )
    main_self.app_context.language_manager.add_translatable_widget( ( script_menu.menu_button, 'Script ...' ) )

    widgets[ 'script_menu' ] = script_menu

    # Add a custom menu for sequences
    sequence_menu = CustomMenu( parent = menu_frame, text = _( 'Sequence ...' ), exec_list = main_self.app_context.sequence_manager.get_sequence_list(), main_object = main_self )
    sequence_menu.menu_button.grid( column = 1, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = ( N, W ) )
    main_self.app_context.language_manager.add_translatable_widget( ( sequence_menu.menu_button, 'Sequence ...' ) )

    widgets[ 'sequence_menu' ] = sequence_menu

    col += 1

    btnContinueBreakpoint = Button( master = op_buttons_frame, text = _( 'Continue' ), command = main_self._continue_breakpoint )
    btnContinueBreakpoint.state( [ "disabled" ] )
    btnContinueBreakpoint.grid( column = col, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = ( S, E ) )
    main_self.app_context.language_manager.add_translatable_widget( ( btnContinueBreakpoint, 'Continue' ) )

    widgets[ 'btnContinueBreakpoint' ] = btnContinueBreakpoint

    col += 1

    btnStopScript = Button( master = op_buttons_frame, text = _( 'Stop script' ), command = main_self._stop_script )
    btnStopScript.state( [ "disabled" ] )
    btnStopScript.grid( column = col, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = ( S, E ) )
    main_self.app_context.language_manager.add_translatable_widget( ( btnStopScript, 'Stop script' ) )

    widgets[ 'btnStopScript' ] = btnStopScript

    col += 1

    btnPauseResumeScript = Button( master = op_buttons_frame, text = _( 'Pause script' ), command = main_self._pause_resume_script )
    btnPauseResumeScript.state( [ "disabled" ] )
    btnPauseResumeScript.grid( column = col, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = ( S, E ) )
    main_self.app_context.language_manager.add_translatable_widget( ( btnPauseResumeScript, 'Pause script' ) )

    widgets[ 'btnPauseResumeScript' ] = btnPauseResumeScript

    op_buttons_frame.grid_columnconfigure( 0 , weight = 0 )
    op_buttons_frame.grid_columnconfigure( 1 , weight = 0 )
    op_buttons_frame.grid_columnconfigure( 2 , weight = 0 )
    op_buttons_frame.grid_columnconfigure( 3 , weight = 0 )

    return widgets
