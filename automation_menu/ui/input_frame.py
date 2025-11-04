"""
Create widgts for each input parameter

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-31
"""


from tkinter import E, N, S, W, Canvas, StringVar
from tkinter.ttk import Button, Entry, Frame, Label, Labelframe, Scrollbar

from automation_menu.models.scriptinputparameter import ScriptInputParameter

#from automation_menu.ui.main_window import AutomationMenuWindow
#def get_input_widgets( master_self: AutomationMenuWindow ):
def get_input_widgets( master_self ):
    """ Create container for input parameters

    Args:
        master_self (AutomationMenuWindow): Master object
    """

    from automation_menu.utils.localization import _

    def _on_mousewheel( event ):
        """ Bind mouse wheel scrolling """

        container_canvas.yview_scroll( int( -1 * ( event.delta / 120 ) ), 'units' )


    def _script_name_set( *args ):
        """ Set title for input labelframe """

        frame_scriptname.config( text = var_script_name.get() )


    input_widgets = {}

    var_script_name = StringVar( master = master_self.root )
    var_script_name.trace_add( mode = 'write', callback = _script_name_set )
    title_frame = Frame()
    title_frame.grid_columnconfigure( index = 0, weight = 1 )
    title_frame.grid_columnconfigure( index = 1, weight = 1 )
    frame_title = Label( master = title_frame, style = 'LabelFrameTitle.TLabel', text = _( 'Input parameters for ' ) )
    frame_title.grid( column = 0, row = 0, sticky = ( N, W ) )
    frame_scriptname = Label( master = title_frame, style = 'LabelFrameTitle.TLabel' )
    frame_scriptname.grid( column = 1, row = 0, sticky = ( N, W ) )
    master_self.language_manager.add_translatable_widget( ( frame_title, 'Input parameters for ' ) )

    input_frame = Labelframe( master = master_self.root, labelwidget = title_frame )
    input_frame.grid( column = 0, columnspan = 2, row = 1, sticky = ( N, S, W, E ) )
    input_frame.grid_columnconfigure( index = 0, weight = 1 )
    input_frame.grid_rowconfigure( index = 0, weight = 1 )
    input_frame.grid_rowconfigure( index = 1, weight = 0 )

    send_input_btn = Button( master = input_frame, text = _( 'Send to script' ) )
    send_input_btn.grid( column = 0, columnspan = 2, row = 1, sticky = ( S, E ) )

    input_widgets[ 'input_send_btn' ] = send_input_btn
    input_widgets[ 'input_frame' ] = input_frame
    input_widgets[ 'script_name' ] = var_script_name

    param_frame = Frame( master = input_frame, borderwidth = 0.1, relief = 'solid' )
    param_frame.grid( column = 0, row = 0, sticky = ( N, S, W, E ) )
    param_frame.grid_columnconfigure( index = 0, weight = 1 )
    param_frame.grid_columnconfigure( index = 1, weight = 0 )

    container_canvas = Canvas( master = param_frame, height = 150 )
    container_canvas.grid( column = 0, row = 0, sticky = ( N, W, E ) )
    container_canvas.grid_columnconfigure( index = 0, weight = 1 )
    container_canvas.bind_all( '<MouseWheel>' , _on_mousewheel )

    input_widgets[ 'container_canvas' ] = container_canvas

    container_scrollbar = Scrollbar( master = param_frame, orient = 'vertical', command = container_canvas.yview )
    container_scrollbar.grid( column = 1, row = 0, sticky = ( N, S ) )

    container_frame = Frame( master = container_canvas )
    container_frame.grid( column = 0, row = 0, columnspan = 2, sticky = ( W, E ) )
    container_frame.grid_columnconfigure( index = 0, weight = 1 )
    container_frame.grid_columnconfigure( index = 1, weight = 1 )
    container_frame.bind( '<Configure>', lambda e: container_canvas.configure( scrollregion = container_canvas.bbox( 'all' ) ) )

    container_canvas.create_window( ( 0, 0 ), window = container_frame, anchor = 'nw', )
    container_canvas.configure( yscrollcommand = container_scrollbar.set )

    input_widgets[ 'input_container' ] = container_frame

    return input_widgets


def _on_key_press( event ):
    """ Prevent new line characters """

    if event.keysym == 'Return':
        return 'break'


def _on_keyboard_focus( widget: Entry, canvas: Canvas ):
    """ Focus on entry widget when tabbing """

    canvas.update_idletasks()

    param_frame = widget.master

    widget_y = param_frame.winfo_y()
    widget_height = param_frame.winfo_height()

    canvas_height = canvas.winfo_height()

    bbox = canvas.bbox( 'all' )

    if not bbox:
        return

    total_height = bbox[ 3 ] - bbox[ 1 ]

    if total_height <= canvas_height:
        return
    
    target_y = widget_y - 10

    scroll_fraction = target_y / total_height
    scroll_fraction = max( 0.0, min( 1.0, scroll_fraction ) )

    canvas.yview_moveto( scroll_fraction )


def fill_frame( param_input_frame: Frame, container_canvas: Canvas, parameters: list[ ScriptInputParameter ] ):
    """ Create input widgets for each parameter
    
    Args:
        param_input_frame (ttk.Frame): Container to place the widgets
        container_canvas (tk.Canvas): The canvas containing all input widgets
        parameters (): List of parameters to set up
    """

    from alwaysontop_tooltip.alwaysontop_tooltip import AlwaysOnTopToolTip
    from automation_menu.utils.localization import _

    column = 0
    row = 0
    input_widgets = []

    for param in parameters:
        if param.type == 'str':
            type = _( 'Text string' )

        elif param.type == 'int':
            type = _( 'Integer number' )

        elif param.type == 'float':
            type = _( 'Float number' )

        param_title_frame = Frame( )
        param_title_frame.grid_columnconfigure( index = 0, weight = 1 )
        param_title_frame.grid_columnconfigure( index = 1, weight = 1 )
        param_name = Label( master = param_title_frame, text = param.name )
        param_name.grid( column = 0, row = 0, sticky = ( N, W ) )
        param_type = Label( master = param_title_frame, text = type )
        param_type.grid( column = 1, row = 0, sticky = ( N, W ) )

        param_frame = Labelframe( master = param_input_frame, labelwidget = param_title_frame, width = 60, height = 40 )
        param_frame.grid( column = column, row = row, padx = 10, sticky = ( W, E ) )

        param_input = Entry( master = param_frame, width = 60 )
        param_input.grid( column = 0, row = 0, sticky = ( W, E ) )
        param_input.bind( '<FocusIn>', lambda e: _on_keyboard_focus( e.widget, container_canvas ) )
        param_input.bind( '<Key>', _on_key_press )

        AlwaysOnTopToolTip( widget = param_frame, msg = param.description )

        column += 1
        if column == 2:
            row = row + 1
            param_input_frame.grid_rowconfigure( index = row, weight = 1 )
            column = 0

        input_widgets.append( param_frame )


    return input_widgets

