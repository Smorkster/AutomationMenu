"""
Create a frame containing some buttons
to manage script execution process

Author: Smorkster
GitHub:
License: MIT
Version: 1.0.0
Created: 2025-09-25
"""

from tkinter import E, N, S, W, ttk

from automation_menu.core.script_discovery import get_scripts
from automation_menu.ui.custom_menu import CustomMenu


def get_op_buttons( main_root, main_self ):
    """ Create a frame to contain buttons for operations during script execution

    Args:
        main_root (Tk): Main window
        main_self (AutomationMenuWindow): Main object
    """

    from automation_menu.utils.localization import _

    widgets = {}

    op_buttons_frame = ttk.Frame( master = main_root )
    op_buttons_frame.grid( columnspan = 2, row = 0, sticky = ( N, W, E ) )

    widgets[ 'op_buttons_frame' ] = op_buttons_frame

    # Add a custom menu
    script_list = get_scripts( app_state = main_self.app_state )

    custom_menu = CustomMenu( parent = op_buttons_frame, text = _( 'Script ...' ), scripts = script_list , main_object = main_self )
    custom_menu.menu_button.grid( column = 0, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = ( N, W ) )
    main_self.language_manager.add_translatable_widget( ( custom_menu.menu_button, 'Script ...' ) )

    widgets[ 'script_menu' ] = custom_menu

    btnContinueBreakpoint = ttk.Button( master = op_buttons_frame, text = _( 'Continue' ), command = main_self._continue_breakpoint )
    btnContinueBreakpoint.state( [ "disabled" ] )
    btnContinueBreakpoint.grid( column = 1, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = ( S, E ) )
    main_self.language_manager.add_translatable_widget( ( btnContinueBreakpoint, 'Continue' ) )

    widgets[ 'btnContinueBreakpoint' ] = btnContinueBreakpoint

    btnStopScript = ttk.Button( master = op_buttons_frame, text = _( 'Stop script' ), command = main_self._stop_script )
    btnStopScript.state( [ "disabled" ] )
    btnStopScript.grid( column = 2, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = ( S, E ) )
    main_self.language_manager.add_translatable_widget( ( btnStopScript, 'Stop script' ) )

    widgets[ 'btnStopScript' ] = btnStopScript

    op_buttons_frame.grid_columnconfigure( 0 , weight = 0 )
    op_buttons_frame.grid_columnconfigure( 1 , weight = 0 )
    op_buttons_frame.grid_columnconfigure( 2 , weight = 0 )

    return widgets
