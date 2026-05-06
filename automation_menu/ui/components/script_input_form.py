"""
Create and manage script input form widgets.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter import Canvas, Event
from tkinter.ttk import Combobox, Entry, Frame, Label
from typing import cast

from automation_menu.models.presetparam import PreSetParam
from automation_menu.models.scriptinputparameter import ScriptInputParameter


def clear_previous_values( input_frame: Frame ) -> None:
    """ Remove any entered values from existing input widgets.

    Args:
        input_frame (Frame): Frame containing input widgets to clear.
    """

    for w in input_frame.winfo_children():

        if isinstance( w, Entry ):
            w.delete( 0, 'end' )

        elif isinstance( w, Combobox ):
            w.set( '' )


def on_keyboard_focus( widget: Entry, canvas: Canvas ) -> None:
    """ Scroll the canvas to keep the focused entry widget visible.

    Args:
        widget (Entry): Entry widget receiving keyboard focus.
        canvas (Canvas): Canvas containing the entry widget.
    """

    canvas.update_idletasks()

    param_frame: Frame = cast( Frame, widget.master )
    widget_y: int = param_frame.winfo_y()
    canvas_height: int = canvas.winfo_height()
    bbox: tuple[ int, int, int, int ] = canvas.bbox( 'all' )

    if not bbox:

        return

    total_height: int = bbox[ 3 ] - bbox[ 1 ]

    if total_height <= canvas_height:

        return

    target_y: int = widget_y - 10

    scroll_fraction: float = target_y / total_height
    scroll_fraction: float = max( 0.0, min( 1.0, scroll_fraction ) )

    canvas.yview_moveto( scroll_fraction )


def on_key_press( event: Event ) -> str | None:
    """ Prevent newline characters from being entered.

    Args:
        event (Event): Event that triggered the handler.

    Returns:
        (str | None): Tkinter break instruction for the Return key, otherwise None.
    """

    if event.keysym == 'Return':

        return 'break'

    return


def collect_entered_input( frame_to_search: Frame ) -> list[ PreSetParam ]:
    """ Collect entered parameter values from the input form.

    Args:
        frame_to_search (Frame): Frame containing parameter input widgets.

    Returns:
        entered_input (list[PreSetParam]): Entered input values as preset parameters.
    """

    entered_input: list[ PreSetParam ] = []

    for widget in frame_to_search.winfo_children():
        children = widget.winfo_children()

        if len( children ) < 2:

            continue

        candidate = children[ 1 ]

        if not isinstance( candidate, ( Combobox, Entry ) ):

            continue

        param_text = str( candidate.get() ).strip()

        if not param_text:

            continue

        param_name = widget.children[ '!label' ].cget( 'text' )
        entered_input.append( PreSetParam( name = param_name, set = param_text ) )

        #input.delete( 0, 'end' )

    return entered_input


def create_input_widgets( parameters: list[ ScriptInputParameter ], container: Frame, pre_set_parameters: list[ PreSetParam ] | None, canvas: Canvas ) -> Frame:
    """ Create input widgets for script parameters.

    Args:
        parameters (list[ScriptInputParameter]): Input parameters requested by the script.
        container (Frame): Frame to attach the created input widgets to.
        pre_set_parameters (list[PreSetParam] | None): Predefined values for parameters.
        canvas (Canvas): Canvas containing the input widgets.

    Returns:
        input_container (Frame): Frame containing the created input widgets.
    """

    from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
    from automation_menu.utils.localization import _

    column_count: int = 0
    input_container: Frame
    number_of_columns: int = 2
    row: int = 0

    target_canvas: Canvas = canvas

    input_container = container

    # Clear any old widgets (from previous script)
    for child in input_container.winfo_children():
        child.destroy()

    # Layout config for the grid of parameter frames
    for i in range( number_of_columns ):
        input_container.grid_columnconfigure( index = i, weight = 1, uniform = 'params' )

    for param in parameters:
        parameter_frame: Frame = Frame( master = input_container )
        parameter_frame.grid( column = column_count, row = row, sticky = 'nswe', padx = 2, pady = 2 )
        parameter_frame.grid_columnconfigure( index = 0, weight = 0, uniform = 'name' )
        parameter_frame.grid_columnconfigure( index = 1, weight = 1 )

        param_name: Label = Label( master = parameter_frame, text = param.name, style = 'LabelFrameTitle.TLabel', width = 15 )
        param_name.grid( column = 0, row = 0, sticky = 'nw' )

        param_input: Combobox | Entry
        # Create input widget
        if param.alternatives and len( param.alternatives ) > 0:
            param_input = Combobox(
                master = parameter_frame,
                style = 'Input.TCombobox',
                values = param.alternatives,
                state = 'readonly'
            )

            if pre_set_parameters and param.name in [ k.name for k in pre_set_parameters ]:
                param_input.set( next( k for k in pre_set_parameters if k.name == param.name ).set )

        else:
            param_input = Entry(
                master = parameter_frame,
                style = 'Input.TEntry'
            )

            if pre_set_parameters and param.name in [ k.name for k in pre_set_parameters ]:
                param_input.delete( 0, 'end' )
                param_input.insert( 'end', next( k for k in pre_set_parameters if k.name == param.name ).set )

        param_input.bind(
            '<FocusIn>',
            lambda e, c = target_canvas:
                on_keyboard_focus( e.widget, c )
        )
        param_input.bind( '<Key>', on_key_press )
        param_input.grid( column = 1, row = 0, padx = 5, pady = 5, sticky = 'nswe' )

        AlwaysOnTopToolTip( widget = param_name, msg = param.description )

        column_count += 1
        if column_count == number_of_columns:
            row += 1
            input_container.grid_rowconfigure( index = row, weight = 1 )
            column_count = 0

    input_container.update_idletasks()

    required_height: int = input_container.winfo_reqheight()
    target_canvas.configure( height = min( required_height, 150 ) )

    return input_container
