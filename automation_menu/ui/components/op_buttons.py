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
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from automation_menu.ui.windows.main_window import AutomationMenuWindow

from automation_menu.types.persistent_ui_callbacks import PersistentUiCallbacks
from automation_menu.ui.types.menu_buttons_ui import MenuButtonsUi
from automation_menu.ui.types.op_persistent_buttons_ui import OpPersistentButtonsUi
from automation_menu.ui.components.custom_menu import CustomMenu
from automation_menu.ui.types.op_buttons_ui import OpButtonsUi
from automation_menu.ui.i18n.widget_for_translation import WidgetForTranslation

margin_x: int = 5
margin_y: int = 5


def get_menu_buttons( main_root: Tk, main_self: AutomationMenuWindow, frame_style: str ) -> MenuButtonsUi:
    """ Create the operation button UI used during script execution.

    Args:
        main_root (Tk): Main application window.
        main_self (AutomationMenuWindow): Main window object.
        frame_style (str): Style name, depending on application state, to use for frames

    Returns:
        widgets (OpButtonsUi): Created operation button UI widgets.
    """

    from automation_menu.utils.localization import _

    widgets: MenuButtonsUi = MenuButtonsUi()

    widgets.menu_frame = Frame( master = main_root, style = frame_style )
    widgets.menu_frame.grid( columnspan = 2, row = 0, sticky = 'nwe' )

    widgets.menu_frame = Frame( master = widgets.menu_frame, style = frame_style )
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

    return widgets


def get_op_buttons( parent_frame: Frame, translate_store_callback: Callable, op_callbacks: dict ) -> OpButtonsUi:
    """ Create the standard execution control buttons for one-time scripts.

    Args:
        parent_frame (Frame): Parent frame to place the buttons in.
        translate_store_callback (Callable): Callback used to register widgets for
            translation.
        op_callbacks (dict): Mapping of button actions used by the created buttons.

    Returns:
        (OpButtonsUi): Container holding the created execution control widgets.
    """

    from automation_menu.utils.localization import _

    ui: OpButtonsUi = OpButtonsUi()
    ui.op_buttons_frame = Frame( master = parent_frame )
    ui.op_buttons_frame.grid( column = 0, columnspan = 3, row = 1, sticky = 'we' )

    ui.btn_continue_breakpoint = Button( master = ui.op_buttons_frame, text = _( 'Continue' ), command = op_callbacks[ 'continue_breakpoint' ] )
    ui.btn_continue_breakpoint.state( [ 'disabled' ] )
    ui.btn_continue_breakpoint.grid( column = 0, row = 0, padx = margin_x, pady = margin_y, sticky = 'se' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.btn_continue_breakpoint, default_text = 'Continue' )
    translate_store_callback( wft )

    ui.btn_stop_script = Button( master = ui.op_buttons_frame, text = _( 'Stop script' ), command = op_callbacks[ 'stop_script' ] )
    ui.btn_stop_script.state( [ 'disabled' ] )
    ui.btn_stop_script.grid( column = 1, row = 0, padx = margin_x, pady = margin_y, sticky = 'se' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.btn_stop_script, default_text = 'Stop script' )
    translate_store_callback( wft )

    ui.btn_pause_resume_script = Button( master = ui.op_buttons_frame, text = _( 'Pause script' ), command = op_callbacks[ 'pause_resume_script' ] )
    ui.btn_pause_resume_script.state( [ 'disabled' ] )
    ui.btn_pause_resume_script.grid( column = 2, row = 0, padx = margin_x, pady = margin_y, sticky = 'se' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.btn_pause_resume_script, default_text = 'Pause script' )
    translate_store_callback( wft )

    ui.op_buttons_frame.grid_columnconfigure( 0 , weight = 0 )
    ui.op_buttons_frame.grid_columnconfigure( 1 , weight = 0 )
    ui.op_buttons_frame.grid_columnconfigure( 2 , weight = 0 )
    ui.op_buttons_frame.grid_columnconfigure( 3 , weight = 0 )

    return ui


def get_op_persistent_buttons( parent: Frame, translate_store_callback: Callable, op_callbacks: PersistentUiCallbacks ) -> OpPersistentButtonsUi:
    """ Create the operation buttons used by persistent script sessions.

    Args:
        parent (Frame): Parent frame to place the buttons in.
        translate_store_callback (Callable): Callback used to register widgets for
            translation.
        op_callbacks (PersistentUiCallbacks): Callbacks invoked by the created
            buttons.

    Returns:
        (OpPersistentButtonsUi): Container holding the created persistent-session
            control widgets.
    """

    from automation_menu.utils.localization import _

    ui: OpPersistentButtonsUi = OpPersistentButtonsUi()

    ui.op_buttons_frame = Frame( master = parent )
    ui.op_buttons_frame.grid( column = 0, row = 2, sticky = 'nswe' )
    ui.op_buttons_frame.grid_columnconfigure( index = 0, weight = 0 )
    ui.op_buttons_frame.grid_columnconfigure( index = 1, weight = 0 )
    ui.op_buttons_frame.grid_columnconfigure( index = 2, weight = 0 )
    ui.op_buttons_frame.grid_columnconfigure( index = 3, weight = 0 )
    ui.op_buttons_frame.grid_columnconfigure( index = 4, weight = 0 )

    ui.btn_show = Button( master = ui.op_buttons_frame, text = _( 'Show' ), command = op_callbacks.show_script, state = 'disabled' )
    ui.btn_show.state( [ 'disabled' ] )
    ui.btn_show.grid( column = 0, row = 0, padx = margin_x, pady = margin_y, sticky = 'we' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.btn_show, default_text = 'Show' )
    translate_store_callback( wft )

    ui.btn_stop_script = Button( master = ui.op_buttons_frame, text = _( 'Stop' ), command = op_callbacks.stop_script, state = 'disabled' )
    ui.btn_stop_script.state( [ 'disabled' ] )
    ui.btn_stop_script.grid( column = 1, row = 0, padx = margin_x, pady = margin_y, sticky = 'we' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.btn_stop_script, default_text = 'Stop' )
    translate_store_callback( wft )

    ui.btn_force_stop_script = Button( master = ui.op_buttons_frame, text = _( 'Force stop' ), command = op_callbacks.force_stop_script, state = 'disabled' )
    ui.btn_force_stop_script.state( [ 'disabled' ] )
    ui.btn_force_stop_script.grid( column = 2, row = 0, padx = margin_x, pady = margin_y, sticky = 'we' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.btn_force_stop_script, default_text = 'Force stop' )
    translate_store_callback( wft )

    ui.btn_pause_script = Button( master = ui.op_buttons_frame, text = _( 'Pause' ), command = op_callbacks.pause_script, state = 'disabled' )
    ui.btn_pause_script.state( [ 'disabled' ] )
    ui.btn_pause_script.grid( column = 3, row = 0, padx = margin_x, pady = margin_y, sticky = 'we' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.btn_pause_script, default_text = 'Pause' )
    translate_store_callback( wft )

    ui.btn_resume_script = Button( master = ui.op_buttons_frame, text = _( 'Resume' ), command = op_callbacks.resume_script, state = 'disabled' )
    ui.btn_resume_script.state( [ 'disabled' ] )
    ui.btn_resume_script.grid( column = 4, row = 0, padx = margin_x, pady = margin_y, sticky = 'we' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.btn_resume_script, default_text = 'Resume' )
    translate_store_callback( wft )

    return ui
