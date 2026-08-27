"""
Create and manage script input form widgets.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter import Canvas, Event
from tkinter.ttk import Checkbutton, Combobox, Entry, Frame, Label
from typing import cast

from automation_menu.models.custom_exceptions import InvalidInputError
from automation_menu.models.presetparam import PreSetParam
from automation_menu.models.script_input_argument import InputArgument
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


def on_input_key_press_no_new_line( event: Event ) -> str | None:
    """ Prevent newline characters from being entered.

    Args:
        event (Event): Event that triggered the handler.

    Returns:
        (str | None): Tkinter break instruction for the Return key, otherwise None.
    """

    if event.keysym == 'Return':

        return 'break'

    return


def on_input_key_press_type_float( event: Event ) -> str | None:
    """ Prevent anything but numbers to be entered.
    Used when input type is int or float

    Args:
        event (Event): Event that triggered the handler.

    Returns:
        (str | None): Tkinter break instruction for the Return key, otherwise None.
    """

    if event.keysym not in [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'period', 'BackSpace', 'Tab' ]:

        return 'break'

    if event.keysym == 'period' and cast( Entry, event.widget ).get().count( '.' ) >= 1:

        return 'break'

    return


def on_input_entry_entered( event: Event, required: bool, required_label: Label ) -> None:
    """ If input is required, verify that input is entered

    Args:
        event (Event): Event triggering the handler
        required (bool): True if input is required
        required_label (Label): Label widget to notified valid input
    """

    fg: str = "#70AC6E"

    if required:
        if len( cast( Entry, event.widget ).get() ) == 0:
            fg = '#FF0000'

    required_label.config( foreground = fg )


def on_input_combobox_selected( event: Event, required: bool, required_label: Label ) -> None:
    """ If input is required, verify that input is entered

    Args:
        event (Event): Event triggering the handler
        required (bool): True if input is required
        required_label (Label): Label widget to notified valid input
    """

    fg: str = "#70AC6E"

    if required:
        box: Combobox = cast( Combobox, event.widget )
        entered: str = box.get()

        if len( entered ) == 0 or entered not in box.cget( 'values' ):
            fg = '#FF0000'

    required_label.config( foreground = fg )


def on_input_key_press_type_int( event: Event ) -> str | None:
    """ Prevent anything but numbers to be entered.
    Used when input type is int or float

    Args:
        event (Event): Event that triggered the handler.

    Returns:
        (str | None): Tkinter break instruction for the Return key, otherwise None.
    """

    if event.keysym not in [ '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'BackSpace', 'Tab' ]:

        return 'break'

    return


def collect_entered_input( frame_to_search: Frame ) -> list[ InputArgument ]:
    """ Collect entered parameter values from the input form.

    Args:
        frame_to_search (Frame): Frame containing parameter input widgets.

    Returns:
        entered_input (list[PreSetParam]): Entered input values as preset parameters.
    """

    entered_input: list[ InputArgument ] = []
    missing_required_input: list[ str ] = []
    invalid_input: list[ str ] = []

    for widget in frame_to_search.winfo_children():
        children = widget.winfo_children()
        param_name = widget.children[ '!label' ].cget( 'text' )

        if len( children ) < 3:

            continue

        candidate = children[ 2 ]

        if not isinstance( candidate, ( Checkbutton, Combobox, Entry ) ):

            continue

        if isinstance( candidate, Checkbutton ):

            param_input_given = 'True' if 'selected' in candidate.state() else 'False'

        else:
            if children[ 1 ].cget( 'foreground' ) and children[ 1 ].cget( 'foreground' ).string == '#FF0000':
                missing_required_input.append( param_name )

                continue

            param_input_given = str( candidate.get() ).strip()

            if not param_input_given:

                continue

            if isinstance( candidate, Combobox ):

                if param_input_given not in candidate.cget( 'values' ):
                    invalid_input.append( f'{ param_name }: { param_input_given }\n' )

        entered_input.append( InputArgument( name = param_name, value = param_input_given ) )

    if len( invalid_input ) > 0:

        raise InvalidInputError( '\n'.join( invalid_input ) )

    if len( missing_required_input ) > 0:

        raise ValueError( ', '.join( missing_required_input ) )

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
    preset_by_name: dict[ str, PreSetParam ] = { p.name: p for p in pre_set_parameters or [] }
    tt_description: str = ''
    required_style: str = ''
    require_fg: str = ''
    require_text: str = ''

    target_canvas: Canvas = canvas

    input_container = container

    # Clear any old widgets (from previous script)
    for child in input_container.winfo_children():
        child.destroy()

    # Layout config for the grid of parameter frames
    for i in range( number_of_columns ):
        input_container.grid_columnconfigure( index = i,
                                             weight = 1,
                                             uniform = 'params' )

    for param in parameters:
        tt_description = param.description
        current_pre_set_param: PreSetParam | None = preset_by_name.get( param.name )
        use_pre_set_param_value: bool = current_pre_set_param is not None

        if use_pre_set_param_value:
            param_value = current_pre_set_param.set

        else:
            param_value = param.default

        if param_value != '':
            tt_description += '\n' + _( 'Default value: {d}' ).format( d = param_value )

        parameter_frame: Frame = Frame( master = input_container )
        parameter_frame.grid( column = column_count,
                             row = row,
                             sticky = 'nswe',
                             padx = 2,
                             pady = 2 )
        parameter_frame.grid_columnconfigure( index = 0, weight = 0, uniform = 'name' )
        parameter_frame.grid_columnconfigure( index = 1, weight = 0, uniform = 'required' )
        parameter_frame.grid_columnconfigure( index = 2, weight = 1 )

        param_name: Label = Label( master = parameter_frame,
                                  text = param.name,
                                  style = 'LabelFrameTitle.TLabel',
                                  width = 15 )
        param_name.grid( column = 0,
                        row = 0,
                        sticky = 'nw' )

        if param.required:
            required_style = 'InputArgRequired.TLabel'
            require_fg = '#FF0000'
            require_text = '*'

        else:
            required_style ='LabelArgNotRequired.TLabel'
            require_fg = ''
            require_text = ' '

        param_required_label: Label = Label( master = parameter_frame,
                                            text = require_text,
                                            style = required_style,
                                            foreground = require_fg,
                                            width = 1 )
        param_required_label.grid( column = 1,
                                  row = 0,
                                  sticky = 'nw' )

        # Create input widget
        param_input: Checkbutton | Combobox | Entry

        if param.type == 'bool':
            param_input = Checkbutton( master = parameter_frame )

            if param_value == 'True':
                param_input.state( [ 'selected' ] )

            else:
                param_input.state( [ '!selected' ] )

        else:
            if param.alternatives and len( param.alternatives ) > 0:
                param_input = Combobox( master = parameter_frame,
                                       style = 'Input.TCombobox',
                                       values = param.alternatives,
                                       state = 'readonly' )

                if param.required:
                    param_input.bind( '<<ComboboxSelected>>',
                                     lambda e, r = param.required, r1 = param_required_label: on_input_combobox_selected( e, r, r1 ),
                                     add = '+' )

                param_input.set( param_value )

            else:
                param_input = Entry( master = parameter_frame,
                                    style = 'Input.TEntry' )

                if param.required:
                    param_input.bind( '<KeyRelease>',
                                     lambda e, r = param.required, rl = param_required_label: on_input_entry_entered( e, r, rl ),
                                     add = '+' )

                if len( param_value ) > 0:
                    param_input.delete( 0, 'end' )
                    param_input.insert( 'end', param_value )
                    param_input.event_generate( '<KeyRelease>' )

            if param.type == 'int':
                param_input.bind( '<Key>', on_input_key_press_type_int )
                tt_description += '\n' + _( 'Only whole numbers are allowed' )

            elif param.type == 'float':
                param_input.bind( '<Key>', on_input_key_press_type_float )
                tt_description += '\n' + _( 'Only numbers are allowed' )

            else:
                param_input.bind( '<Key>', on_input_key_press_no_new_line )

        param_input.bind( '<FocusIn>',
                         lambda e, c = target_canvas:
                         on_keyboard_focus( e.widget, c ) )
        param_input.grid( column = 2,
                         row = 0,
                         padx = 5,
                         pady = 5,
                         sticky = 'nswe' )

        AlwaysOnTopToolTip( widget = parameter_frame, msg = tt_description )
        AlwaysOnTopToolTip( widget = param_name, msg = tt_description )
        AlwaysOnTopToolTip( widget = param_required_label, msg = tt_description )
        AlwaysOnTopToolTip( widget = param_input, msg = tt_description )

        column_count += 1
        if column_count == number_of_columns:
            row += 1
            input_container.grid_rowconfigure( index = row, weight = 1 )
            column_count = 0

    input_container.update_idletasks()

    required_height: int = input_container.winfo_reqheight()
    target_canvas.configure( height = min( required_height, 150 ) )

    return input_container
