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
from typing import TYPE_CHECKING, TypedDict

from automation_menu.models.widget_for_translation import WidgetForTranslation

if TYPE_CHECKING:
    from automation_menu.ui.main_window import AutomationMenuWindow

from tkinter import Tk
from tkinter.ttk import Button, Frame

from automation_menu.ui.custom_menu import CustomMenu


class ButtonDict( TypedDict ):
    """ Defined dict for op button widgets """

    op_buttons_frame: Frame
    menu_frame: Frame
    script_menu: CustomMenu
    sequence_menu: CustomMenu

    btnContinueBreakpoint: Button
    btnStopScript: Button
    btnPauseResumeScript: Button


def get_op_buttons( main_root: Tk, main_self: AutomationMenuWindow ) -> ButtonDict:
    """ Create a frame to contain buttons for operations during script execution

    Args:
        main_root (Tk): Main window
        main_self (AutomationMenuWindow): Main object
    """

    from automation_menu.utils.localization import _

    #widgets: dict[ str, Button | CustomMenu | Frame ] = {}

    op_buttons_frame: Frame = Frame( master = main_root )
    op_buttons_frame.grid( columnspan = 2, row = 0, sticky = 'nwe' )

    col: int = 0

    menu_frame: Frame = Frame( master = op_buttons_frame )
    menu_frame.grid()
    menu_frame.grid_columnconfigure( index = 0, weight = 0 )
    menu_frame.grid_columnconfigure( index = 1, weight = 0 )

    # Add a custom menu for scripts
    script_menu: CustomMenu = CustomMenu( parent = menu_frame, text = _( 'Script ...' ), exec_list = main_self.app_context.ScriptManager.get_script_list() , main_object = main_self )
    script_menu.menu_button.grid( column = 0, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = 'nw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = script_menu.menu_button, default_text = 'Script ...' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    # Add a custom menu for sequences
    sequence_menu: CustomMenu = CustomMenu( parent = menu_frame, text = _( 'Sequence ...' ), exec_list = main_self.app_context.SequenceManager.get_sequence_list(), main_object = main_self )
    sequence_menu.menu_button.grid( column = 1, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = 'nw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = sequence_menu.menu_button, default_text = 'Sequence ...' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    col += 1

    btnContinueBreakpoint: Button = Button( master = op_buttons_frame, text = _( 'Continue' ), command = main_self._continue_breakpoint )
    btnContinueBreakpoint.state( [ "disabled" ] )
    btnContinueBreakpoint.grid( column = col, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = 'se' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = btnContinueBreakpoint, default_text = 'Continue' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    col += 1

    btnStopScript: Button = Button( master = op_buttons_frame, text = _( 'Stop script' ), command = main_self._stop_script )
    btnStopScript.state( [ "disabled" ] )
    btnStopScript.grid( column = col, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = 'se' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = btnStopScript, default_text = 'Stop script' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    col += 1

    btnPauseResumeScript: Button = Button( master = op_buttons_frame, text = _( 'Pause script' ), command = main_self._pause_resume_script )
    btnPauseResumeScript.state( [ "disabled" ] )
    btnPauseResumeScript.grid( column = col, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = 'se' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = btnPauseResumeScript, default_text = 'Pause script' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )


    op_buttons_frame.grid_columnconfigure( 0 , weight = 0 )
    op_buttons_frame.grid_columnconfigure( 1 , weight = 0 )
    op_buttons_frame.grid_columnconfigure( 2 , weight = 0 )
    op_buttons_frame.grid_columnconfigure( 3 , weight = 0 )

    widgets: ButtonDict = {
        'btnStopScript': btnStopScript,
        'btnPauseResumeScript': btnPauseResumeScript,
        'btnContinueBreakpoint': btnContinueBreakpoint,
        'sequence_menu': sequence_menu,
        'script_menu': script_menu,
        'menu_frame': menu_frame,
        'op_buttons_frame': op_buttons_frame
    }

    return widgets
