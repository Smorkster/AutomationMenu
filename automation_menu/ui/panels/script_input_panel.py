"""
Create and manage the root panel for script input parameters.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter import Canvas, Event, StringVar, Tk
from tkinter.ttk import Button, Frame, Label, Labelframe, Scrollbar
from typing import Callable

from automation_menu.ui.types.input_ui import InputUi
from automation_menu.ui.types.widget_for_translation import WidgetForTranslation


def on_canvas_config( ui: InputUi, event: Event ) -> None:
    """ Update the canvas window width when the canvas is resized.

    Args:
        ui (InputUi): Input UI widget collection.
        event (Event): Event that triggered the handler.
    """

    ui.container_canvas.after_idle( lambda: ui.container_canvas.itemconfig( ui.window_id, width = event.width ) )


def on_frame_config( ui: InputUi, event: Event ) -> None:
    """ Update the canvas scroll region when the input frame changes size.

    Args:
        ui (InputUi): Input UI widget collection.
        event (Event): Event that triggered the handler.
    """

    ui.container_canvas.after_idle( lambda: ui.container_canvas.configure( scrollregion = ui.container_canvas.bbox( 'all' ) ) )


def on_mousewheel( ui: InputUi, event: Event ) -> None:
    """ Scroll the input canvas with the mouse wheel.

    Args:
        ui (InputUi): Input UI widget collection.
        event (Event): Event that triggered the handler.
    """

    ui.container_canvas.yview_scroll( int( -1 * ( event.delta / 120 ) ), 'units' )


def script_name_set( ui: InputUi, name: str ) -> None:
    """ Set the displayed script name for the input panel.

    Args:
        ui (InputUi): Input UI widget collection.
        name (str): Name of the script for the current input frame.
    """

    ui.current_script_name.set( name )


def create_input_root( add_translate_callback: Callable, parent: Tk ) -> InputUi:
    """ Create the root UI container for script input parameters.

    Args:
        add_translate_callback (Callable): Callback used to register translatable widgets.
        parent (Tk): Parent window to attach the input panel to.

    Returns:
        ui (InputUi): Created input UI widget collection.
    """

    from automation_menu.utils.localization import _

    ui: InputUi = InputUi()

    ui.title_frame = Frame()
    ui.title_frame.grid_columnconfigure( index = 0, weight = 1 )
    ui.title_frame.grid_columnconfigure( index = 1, weight = 1 )

    ui.frame_title = Label( master = ui.title_frame, style = 'LabelFrameTitle.TLabel', text = _( 'Input parameters for ' ) )
    ui.frame_title.grid( column = 0, row = 0, sticky = 'nw' )

    ui.frame_scriptname = Label( master = ui.title_frame, style = 'LabelFrameTitle.TLabel' )
    ui.frame_scriptname.grid( column = 1, row = 0, sticky = 'nw' )
    ui.current_script_name = StringVar( master = ui.frame_scriptname )
    ui.frame_scriptname.config( textvariable = ui.current_script_name )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.frame_title, default_text = 'Input parameters for ' )
    add_translate_callback( wft )

    ui.root_input_frame = Labelframe( master = parent, labelwidget = ui.title_frame )
    ui.root_input_frame.grid( column = 0, columnspan = 2, row = 1, sticky = 'nswe' )
    ui.root_input_frame.grid_columnconfigure( index = 0, weight = 1 )
    ui.root_input_frame.grid_columnconfigure( index = 1, weight = 1 )
    ui.root_input_frame.grid_rowconfigure( index = 0, weight = 1 )
    ui.root_input_frame.grid_rowconfigure( index = 1, weight = 0 )

    ui.abort_btn = Button( master = ui.root_input_frame, text = _( 'Abort' ) )
    ui.abort_btn.grid( column = 0, row = 1, sticky = 'sw' )

    ui.send_input_btn = Button( master = ui.root_input_frame, text = _( 'Send to script' ) )
    ui.send_input_btn.grid( column = 1, row = 1, sticky = 'se' )

    ui.param_list_frame = Frame( master = ui.root_input_frame, borderwidth = 0.1, relief = 'solid' )
    ui.param_list_frame.grid( column = 0, columnspan = 2, row = 0, sticky = 'nswe' )
    ui.param_list_frame.grid_columnconfigure( index = 0, weight = 1 )
    ui.param_list_frame.grid_columnconfigure( index = 1, weight = 0 )
    ui.param_list_frame.grid_rowconfigure( index = 0, weight = 1 )

    ui.container_canvas = Canvas( master = ui.param_list_frame, height = 150, highlightthickness = 0 )
    ui.container_canvas.grid( sticky = 'nswe' )
    ui.container_canvas.grid_columnconfigure( index = 0, weight = 1 )

    ui.container_scrollbar = Scrollbar( master = ui.param_list_frame, orient = 'vertical', command = ui.container_canvas.yview )
    ui.container_scrollbar.grid( column = 1, row = 0, sticky = 'ns' )

    ui.container_canvas.configure( yscrollcommand = ui.container_scrollbar.set )

    ui.input_container = Frame( master = ui.container_canvas )
    ui.window_id = ui.container_canvas.create_window( ( 0, 0 ), window = ui.input_container, anchor = 'nw' )

    return ui
