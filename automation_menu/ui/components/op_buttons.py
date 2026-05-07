"""
Create a frame containing some buttons
to manage script execution process

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from tkinter import Tk
from tkinter.ttk import Button, Frame
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.ui.windows.main_window import AutomationMenuWindow

from automation_menu.ui.components.custom_menu import CustomMenu
from automation_menu.ui.types.op_buttons_ui import OpButtonsUi
from automation_menu.ui.i18n.widget_for_translation import WidgetForTranslation


def get_op_buttons( main_root: Tk, main_self: AutomationMenuWindow ) -> OpButtonsUi:
    """ Create the operation button UI used during script execution.

    Args:
        main_root (Tk): Main application window.
        main_self (AutomationMenuWindow): Main window object.

    Returns:
        widgets (OpButtonsUi): Created operation button UI widgets.
    """

    from automation_menu.utils.localization import _

    widgets: OpButtonsUi = OpButtonsUi()

    widgets.op_buttons_frame = Frame( master = main_root )
    widgets.op_buttons_frame.grid( columnspan = 2, row = 0, sticky = 'nwe' )

    col: int = 0

    widgets.menu_frame = Frame( master = widgets.op_buttons_frame )
    widgets.menu_frame.grid()
    widgets.menu_frame.grid_columnconfigure( index = 0, weight = 0 )
    widgets.menu_frame.grid_columnconfigure( index = 1, weight = 0 )

    # Add a custom menu for scripts
    widgets.script_menu = CustomMenu( parent = widgets.menu_frame, text = _( 'Script ...' ), exec_list = main_self.app_context.ScriptManager.get_script_list() , main_object = main_self )
    widgets.script_menu.menu_button.grid( column = 0, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = 'nw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = widgets.script_menu.menu_button, default_text = 'Script ...' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    # Add a custom menu for sequences
    widgets.sequence_menu = CustomMenu( parent = widgets.menu_frame, text = _( 'Sequence ...' ), exec_list = main_self.app_context.SequenceManager.get_sequence_list(), main_object = main_self )
    widgets.sequence_menu.menu_button.grid( column = 1, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = 'nw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = widgets.sequence_menu.menu_button, default_text = 'Sequence ...' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    col += 1

    widgets.btn_continue_breakpoint = Button( master = widgets.op_buttons_frame, text = _( 'Continue' ), command = main_self.continue_breakpoint )
    widgets.btn_continue_breakpoint.state( [ "disabled" ] )
    widgets.btn_continue_breakpoint.grid( column = col, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = 'se' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = widgets.btn_continue_breakpoint, default_text = 'Continue' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    col += 1

    widgets.btn_stop_script = Button( master = widgets.op_buttons_frame, text = _( 'Stop script' ), command = main_self.stop_script )
    widgets.btn_stop_script.state( [ "disabled" ] )
    widgets.btn_stop_script.grid( column = col, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = 'se' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = widgets.btn_stop_script, default_text = 'Stop script' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    col += 1

    widgets.btn_pause_resume_script = Button( master = widgets.op_buttons_frame, text = _( 'Pause script' ), command = main_self.pause_resume_script )
    widgets.btn_pause_resume_script.state( [ "disabled" ] )
    widgets.btn_pause_resume_script.grid( column = col, row = 0, padx = main_self.button_margin[ 'x' ], pady = main_self.button_margin[ 'y' ], sticky = 'se' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = widgets.btn_pause_resume_script, default_text = 'Pause script' )
    main_self.app_context.LanguageManager.add_translatable_widget( wft )

    widgets.op_buttons_frame.grid_columnconfigure( 0 , weight = 0 )
    widgets.op_buttons_frame.grid_columnconfigure( 1 , weight = 0 )
    widgets.op_buttons_frame.grid_columnconfigure( 2 , weight = 0 )
    widgets.op_buttons_frame.grid_columnconfigure( 3 , weight = 0 )

    return widgets
