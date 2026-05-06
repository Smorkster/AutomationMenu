"""
Create and configure the UI for automation sequence management.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from functools import partial
from tkinter import BooleanVar, Canvas, Event
from tkinter.ttk import Button, Checkbutton, Combobox, Entry, Frame, Label, Notebook, Scrollbar, Treeview
from typing import Callable

from automation_menu.models.sequence import Sequence
from automation_menu.ui.types.sequence_ui import SequenceUi
from automation_menu.ui.types.widget_for_translation import WidgetForTranslation


def on_canvas_config( canvas: Canvas, window_id: int | None, event: Event ) -> None:
    """ Update the sequence step canvas window width when the canvas is resized.

    Args:
        canvas (Canvas): Canvas containing the embedded window.
        window_id (int | None): Canvas window ID to resize.
        event (Event): Event that triggered the handler.
    """

    canvas.after_idle( lambda: canvas.itemconfig( window_id, width = event.width ) if window_id else '' )


def on_mousewheel( canvas: Canvas, event: Event ) -> None:
    """ Scroll the sequence step canvas with the mouse wheel.

    Args:
        canvas (Canvas): Canvas to scroll.
        event (Event): Event that triggered the handler.
    """

    canvas.yview_scroll( int( -1 * ( event.delta / 120 ) ), 'units' )


def on_steps_container_frame_config( canvas: Canvas, event: Event ) -> None:
    """ Update the sequence step canvas scroll region when the container changes size.

    Args:
        canvas (Canvas): Canvas containing the steps container.
        event (Event): Event that triggered the handler.
    """

    canvas.after_idle( lambda: canvas.configure( scrollregion = canvas.bbox( 'all' ) ) )


def build_tab_content( ui: SequenceUi, add_translatable: Callable, op_callbacks: dict[ str, Callable ] ) -> SequenceUi:
    """ Create the widgets used to display and edit sequence data.

    Args:
        ui (SequenceUi): Sequence UI widget collection to populate.
        add_translatable (Callable): Callback used to register translatable widgets.
        op_callbacks (dict[str, Callable]): Callback functions used by the sequence UI.

    Returns:
        ui (SequenceUi): Populated sequence UI widget collection.
    """

    create_sequence_list( ui = ui, op_callbacks = op_callbacks )
    create_sequence_list_op_buttons( ui = ui, add_translatable = add_translatable, op_callbacks = op_callbacks )
    create_sequence_form( ui = ui, add_translatable = add_translatable )
    create_steps_display( ui = ui, add_translatable = add_translatable, op_callbacks = op_callbacks )
    create_sequence_editing_op_buttons( ui = ui, add_translatable = add_translatable, op_callbacks = op_callbacks )
    create_step_form( ui = ui, add_translatable = add_translatable, op_callbacks = op_callbacks )

    return ui


def create_sequence_editing_op_buttons( ui: SequenceUi, add_translatable: Callable, op_callbacks: dict[ str, Callable ] ) -> None:
    """ Create the buttons used while editing a sequence.

    Args:
        ui (SequenceUi): Sequence UI widget collection.
        add_translatable (Callable): Callback used to register translatable widgets.
        op_callbacks (dict[str, Callable]): Callback functions used by the buttons.
    """

    from automation_menu.utils.localization import _

    sequence_ops: Frame = Frame( master = ui.sequence_form )
    sequence_ops.grid( column = 0, columnspan = 2, row = 4, sticky = 'se' )
    ui.sequence_ops = sequence_ops

    col: int = 0

    sequence_ops.grid_columnconfigure( index = col, weight = 0 )
    add_step_button: Button = Button( master = sequence_ops, text = _( 'Add step' ) , command = op_callbacks[ 'add_sequence_step' ] )
    add_step_button.grid( column = col, row = 0 )
    ui.add_step_btn = add_step_button

    wft: WidgetForTranslation = WidgetForTranslation( widget = add_step_button, default_text = 'Add step' )
    add_translatable( wft )

    col += 1

    sequence_ops.grid_columnconfigure( index = col, weight = 0 )
    save_sequence: Button = Button( master = sequence_ops, text = _( 'Save sequence' ), command = op_callbacks[ 'save_sequence' ] )
    save_sequence.grid( column = col, row = 0 )
    ui.save_sequence_btn = save_sequence

    wft: WidgetForTranslation = WidgetForTranslation( widget = save_sequence, default_text = 'Save sequence' )
    add_translatable( wft )

    col += 1

    sequence_ops.grid_columnconfigure( index = col, weight = 0 )
    delete_sequence: Button = Button( master = sequence_ops, text = _( 'Delete sequence' ), command = op_callbacks[ 'delete_sequence' ] )
    delete_sequence.grid( column = col, row = 0, sticky = 'nw' )
    ui.delete_sequence_btn = delete_sequence

    wft: WidgetForTranslation = WidgetForTranslation( widget = delete_sequence, default_text = 'Delete' )
    add_translatable( wft )

    col += 1

    sequence_ops.grid_columnconfigure( index = col, weight = 0 )
    abort_sequence_edit: Button = Button( master = sequence_ops, text = _( 'Abort edit' ), command = op_callbacks[ 'abort_sequence_edit' ] )
    abort_sequence_edit.grid( column = col, row = 0, sticky = 'nw' )
    ui.abort_sequence_edit_btn = abort_sequence_edit

    wft: WidgetForTranslation = WidgetForTranslation( widget = abort_sequence_edit, default_text = 'Abort edit' )
    add_translatable( wft )

    sequence_ops.grid_remove()


def create_sequence_form( ui: SequenceUi, add_translatable: Callable ) -> None:
    """ Create the form used to display and edit sequence information.

    Args:
        ui (SequenceUi): Sequence UI widget collection.
        add_translatable (Callable): Callback used to register translatable widgets.
    """

    from automation_menu.utils.localization import _

    sequence_form: Frame = Frame( master = ui.main_frame )
    sequence_form.grid( column = 0, row = 2, rowspan = 2, sticky = 'nswe' )
    sequence_form.grid_columnconfigure( index = 0, weight = 0 )
    sequence_form.grid_columnconfigure( index = 1, weight = 1 )
    sequence_form.grid_columnconfigure( index = 2, weight = 0 )
    sequence_form.grid_rowconfigure( index = 0, weight = 0 ) # Name
    sequence_form.grid_rowconfigure( index = 1, weight = 0 ) # Description
    sequence_form.grid_rowconfigure( index = 2, weight = 0 ) # Stop on error
    sequence_form.grid_rowconfigure( index = 3, weight = 1 ) # Empty
    sequence_form.grid_rowconfigure( index = 4, weight = 1 ) # Sequence op buttons
    ui.sequence_form = sequence_form

    row: int = 0

    name_title: Label = Label( master = sequence_form, text = _( 'Name' ), style = 'History.TLabel' )
    name_title.grid( column = 0, row = row, sticky = 'w' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = name_title, default_text = 'Name' )
    add_translatable( wft )

    name_field: Entry = Entry( master = sequence_form )
    name_field.grid( column = 1, columnspan = 2, row = row, sticky = 'we' )
    ui.name_field = name_field

    row += 1

    description_title: Label = Label( master = sequence_form, text = _( 'Description' ), style = 'History.TLabel' )
    description_title.grid( column = 0, row = row, sticky = 'w' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = description_title, default_text = 'Description' )
    add_translatable( wft )

    description_field: Entry = Entry( master = sequence_form )
    description_field.grid( column = 1, columnspan = 2, row = row, sticky = 'we' )
    ui.description_field = description_field

    row += 1

    stop_on_error_title: Label = Label( master = sequence_form, text = _( 'Stop on error' ), style = 'History.TLabel' )
    stop_on_error_title.grid( column = 0, row = row, sticky = 'w' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = stop_on_error_title, default_text = 'Stop on error' )
    add_translatable( wft )

    ui.stop_sequence_on_error_var = BooleanVar( master = sequence_form, value = False )
    stop_on_error_field: Checkbutton = Checkbutton( master = sequence_form, variable = ui.stop_sequence_on_error_var )
    stop_on_error_field.grid( column = 1, columnspan = 2, row = row, sticky = 'we' )
    ui.stop_sequence_on_error_field = stop_on_error_field


def create_sequence_list( ui: SequenceUi, op_callbacks: dict[ str, Callable ] ) -> None:
    """ Create the list used to display available sequences.

    Args:
        ui (SequenceUi): Sequence UI widget collection.
        op_callbacks (dict[str, Callable]): Callback functions used by the sequence list.
    """

    sequence_list: Treeview = Treeview( master = ui.main_frame, columns = ( 'name', 'id' ), displaycolumns = 'name', show = '', selectmode = 'browse' )
    sequence_list.column( 'name', anchor = 'w' )
    sequence_list.column( 'id', anchor = 'w' )
    sequence_list.bind( '<ButtonRelease-1>', op_callbacks[ 'on_listbox_click' ] )
    sequence_list.grid( column = 0, row = 0, sticky = 'nswe' )

    list_scrollbar: Scrollbar = Scrollbar( master = ui.main_frame )
    list_scrollbar.grid( column = 0, row = 0, sticky = 'nse' )

    sequence_list.config( yscrollcommand = list_scrollbar.set )

    list_scrollbar.config( command = sequence_list.yview )

    ui.sequence_list = sequence_list

    op_callbacks[ 'list_sequences' ]( main_self = op_callbacks[ 'main_self' ])


def create_sequence_list_op_buttons( ui: SequenceUi, add_translatable: Callable, op_callbacks: dict[ str, Callable ] ) -> None:
    """ Create the buttons used for sequence list operations.

    Args:
        ui (SequenceUi): Sequence UI widget collection.
        add_translatable (Callable): Callback used to register translatable widgets.
        op_callbacks (dict[str, Callable]): Callback functions used by the buttons.
    """

    from automation_menu.utils.localization import _

    sequence_op_frame: Frame = Frame( master = ui.main_frame )
    sequence_op_frame.grid( column = 0, row = 1, sticky = 'we' )

    col: int = 0

    sequence_op_frame.grid_columnconfigure( index = col, weight = 0 )
    create_new_sequence: Button = Button( master = sequence_op_frame, text = _( 'Create new sequence' ), command = op_callbacks[ 'create_new_sequence' ] )
    create_new_sequence.grid( column = col, row = 0, sticky = 'nw' )
    ui.new_sequence_btn = create_new_sequence

    wft: WidgetForTranslation = WidgetForTranslation( widget = create_new_sequence, default_text = 'Create new sequence' )
    add_translatable( wft )

    col += 1

    sequence_op_frame.grid_columnconfigure( index = col, weight = 0 )
    edit_sequence: Button = Button( master = sequence_op_frame, text = _( 'Edit' ), command = op_callbacks[ 'edit_sequence' ], state = 'disable' )
    edit_sequence.grid( column = col, row = 0, sticky = 'nw' )
    ui.edit_sequence_btn = edit_sequence

    wft: WidgetForTranslation = WidgetForTranslation( widget = edit_sequence, default_text = 'Edit' )
    add_translatable( wft )

    col += 1

    sequence_op_frame.grid_columnconfigure( index = col, weight = 1 )

    col += 1

    sequence_op_frame.grid_columnconfigure( index = col, weight = 0 )
    run_sequence: Button = Button( master = sequence_op_frame, text = _( 'Run selected' ), command = op_callbacks[ 'run_sequence' ], state = 'disable' )
    run_sequence.grid( column = col, row = 0, sticky = 'nw' )
    ui.run_sequence_btn = run_sequence

    wft: WidgetForTranslation = WidgetForTranslation( widget = run_sequence, default_text = 'Run selected' )
    add_translatable( wft )


def create_sequence_tab( tabcontrol: Notebook, translate_callback: Callable ) -> SequenceUi:
    """ Create the root tab for automation sequence management.

    Args:
        tabcontrol (Notebook): Notebook widget to attach the sequence tab to.
        translate_callback (Callable): Callback used to register widgets for translation.

    Returns:
        ui (SequenceUi): Created sequence UI widget collection.
    """

    from automation_menu.utils.localization import _

    ui: SequenceUi = SequenceUi()

    ui.main_frame = Frame( master = tabcontrol, name = 'sequence' )
    ui.main_frame.grid( sticky = "nswe" )
    ui.main_frame.grid_columnconfigure( index = 0, weight = 0 ) # Sequence list/op buttons/editing
    ui.main_frame.grid_columnconfigure( index = 1, weight = 1 ) # Sequence steps
    ui.main_frame.grid_rowconfigure( index = 0, weight = 0 ) # Sequence list / Sequence steps
    ui.main_frame.grid_rowconfigure( index = 1, weight = 0 ) # Sequence op buttons
    ui.main_frame.grid_rowconfigure( index = 2, weight = 1 ) # Sequence editing
    ui.main_frame.grid_rowconfigure( index = 3, weight = 0 ) # Sequence editing / Steps op buttons

    tabcontrol.add( child =  ui.main_frame, text = _( 'Automation sequence' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.main_frame, default_text = 'Automation sequence' )
    translate_callback( wft )

    return ui


def create_steps_display( ui: SequenceUi, add_translatable: Callable, op_callbacks: dict[ str, Callable ] ) -> None:
    """ Create the display area used to show sequence steps.

    Args:
        ui (SequenceUi): Sequence UI widget collection.
        add_translatable (Callable): Callback used to register translatable widgets.
        op_callbacks (dict[str, Callable]): Callback functions used by the step display.
    """

    from automation_menu.utils.localization import _

    steps_display_frame: Frame = Frame( master = ui.main_frame )
    steps_display_frame.grid( column = 1, row = 0, rowspan = 3, sticky = 'nswe' )
    steps_display_frame.grid_columnconfigure( index = 0, weight = 1 )
    steps_display_frame.grid_columnconfigure( index = 1, weight = 0 )
    steps_display_frame.grid_rowconfigure( index = 0, weight = 0 )
    steps_display_frame.grid_rowconfigure( index = 1, weight = 1 )
    steps_display_frame.grid_rowconfigure( index = 2, weight = 0 )
    ui.steps_display_frame = steps_display_frame

    steps_title: Label = Label( master = steps_display_frame, text = _( 'Steps in sequence' ), style = 'BiggerTitle.TLabel' )
    steps_title.grid( column = 0, row = 0, sticky = 'w' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = steps_title, default_text = 'Steps in sequence' )
    add_translatable( wft )

    display_container: Frame = Frame( master = steps_display_frame )
    display_container.grid( column = 0, columnspan = 2, row = 1, sticky = 'nswe' )
    display_container.grid_columnconfigure( index = 0, weight = 1 )
    display_container.grid_rowconfigure( index = 0, weight = 1 )
    ui.display_container = display_container

    container_canvas: Canvas = Canvas( master = display_container, highlightthickness = 0 )
    container_canvas.grid( sticky = 'nswe' )
    container_canvas.grid_columnconfigure( index = 0, weight = 1 )
    ui.steps_list_container_canvas = container_canvas

    container_scrollbar: Scrollbar = Scrollbar( master = display_container, orient = 'vertical', command = container_canvas.yview )
    container_scrollbar.grid( column = 1, row = 0, sticky = 'ns' )
    ui.container_scrollbar = container_scrollbar

    container_canvas.configure( yscrollcommand = container_scrollbar.set )

    steps_container: Frame = Frame( master = container_canvas )
    steps_container.grid_columnconfigure( index = 0, weight = 1 )
    steps_container.grid_rowconfigure( index = 0, weight = 1 )
    ui.steps_container = steps_container

    window_id = container_canvas.create_window( ( 0, 0 ), window = steps_container, anchor = 'nw' )
    ui.steps_list_input_window_id = window_id

    container_canvas.bind( '<Configure>', partial( on_canvas_config, ui.steps_list_container_canvas, ui.steps_list_input_window_id ) )
    container_canvas.bind_all( '<MouseWheel>' , partial( on_mousewheel, ui.steps_list_container_canvas ) )
    steps_container.bind( '<Configure>', partial( on_steps_container_frame_config, ui.steps_list_container_canvas ) )


def create_step_form( ui: SequenceUi, add_translatable: Callable, op_callbacks: dict[ str, Callable ] ) -> None:
    """ Create the form used to add or edit a sequence step.

    Args:
        ui (SequenceUi): Sequence UI widget collection.
        add_translatable (Callable): Callback used to register translatable widgets.
        op_callbacks (dict[str, Callable]): Callback functions used by the step form.
    """

    from automation_menu.utils.localization import _

    step_form: Frame = Frame( master = ui.main_frame, style = 'SequenceStep.TFrame', borderwidth = 2, relief = 'solid' )
    step_form.grid( column = 1, row = 3, sticky = 'we' )
    step_form.grid_columnconfigure( index = 0, weight = 0 )
    step_form.grid_columnconfigure( index = 1, weight = 1 )
    ui.step_form = step_form

    row: int = 0

    step_form.grid_rowconfigure( index = row, weight = 0 ) # Script title
    script_title: Label = Label( master = step_form, text = _( 'Script for this step' ), style = 'History.TLabel' )
    script_title.grid( column = 0, row = row, sticky = 'nw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = script_title, default_text = 'Script for this step' )
    add_translatable( wft )

    script_names: list[ str ] = sorted( [ s.filename for s in op_callbacks[ 'get_script_list' ]() ] )
    script_list: Combobox = Combobox( master = step_form, values = script_names, state = 'readonly' )
    script_list.bind( '<<ComboboxSelected>>', op_callbacks[ '_on_step_script_selected' ] )
    script_list.grid( column = 1, row = row, padx = 5, sticky = 'nw' )
    ui.step_script_list = script_list

    row += 1

    step_form.grid_rowconfigure( index = row, weight = 0 ) # Stop on error
    stop_on_error_title: Label = Label( master = step_form, text = _( 'Stop on error' ), style = 'History.TLabel' )
    stop_on_error_title.grid( column = 0, row = row, sticky = 'w' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = stop_on_error_title, default_text = 'Stop on error' )
    add_translatable( wft )

    ui.stop_step_on_error_var = BooleanVar( master = step_form, value = False )
    stop_on_error_field: Checkbutton = Checkbutton( master = step_form, variable = ui.stop_step_on_error_var )
    stop_on_error_field.grid( column = 1, row = row, sticky = 'w' )

    row += 1

    step_form.grid_rowconfigure( index = row, weight = 0 ) # Input title
    input_title: Label = Label( master = step_form, text = _( 'Script input parameters' ), style = 'History.TLabel' )
    input_title.grid( column = 0, row = row, sticky = 'nw' )
    ui.step_input_title = input_title

    wft: WidgetForTranslation = WidgetForTranslation( widget = input_title, default_text = 'Script input parameters' )
    add_translatable( wft )

    row += 1

    step_form.grid_rowconfigure( index = row, weight = 0 ) # Input parameters
    input_container: Frame = Frame( master = step_form )
    input_container.grid( column = 0, columnspan = 2, row = row, sticky = 'we' )
    input_container.grid_columnconfigure( index = 0, weight = 1 )
    input_container.grid_columnconfigure( index = 1, weight = 0 )
    input_container.grid_rowconfigure( index = 0, weight = 0 )

    container_canvas: Canvas = Canvas( master = input_container, height = 150, highlightthickness = 0 )
    container_canvas.grid( column = 0, row = 0, sticky = 'we' )
    container_canvas.grid_columnconfigure( index = 0, weight = 1 )

    container_scrollbar: Scrollbar = Scrollbar( master = input_container, orient = 'vertical', command = container_canvas.yview )
    container_scrollbar.grid( column = 1, row = 0, sticky = 'ns' )

    container_canvas.configure( yscrollcommand = container_scrollbar.set )

    input_frame: Frame = Frame( master = container_canvas )
    window_id: int = container_canvas.create_window( ( 0, 0 ), window = input_frame, anchor = 'nw' )

    ui.step_input_container = input_container
    ui.step_form_container_canvas = container_canvas
    ui.step_input_window_id = window_id
    ui.step_input_frame = input_frame

    input_frame.bind(
        '<Configure>',
        lambda e: container_canvas.configure(
            scrollregion = container_canvas.bbox( 'all' )
            )
    )

    container_canvas.bind(
        '<Configure>',
        lambda e: container_canvas.itemconfig( window_id, width = e.width )
    )

    row += 1

    step_form.grid_rowconfigure( index = row, weight = 0 ) # Step op buttons

    step_op_buttons_frame: Frame = Frame( master = step_form )
    step_op_buttons_frame.grid( column = 1, row = row, sticky = 'se' )

    col = 0

    step_op_buttons_frame.grid_columnconfigure( index = col, weight = 0 )
    step_add: Button = Button( master = step_op_buttons_frame, text = _( 'Save step' ), command = op_callbacks[ '_save_edited_step' ] )
    step_add.grid( column = col, row = 0, sticky = 'e' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = step_add, default_text = 'Save step' )
    add_translatable( wft )

    col += 1

    step_op_buttons_frame.grid_columnconfigure( index = col, weight = 0 )
    step_remove: Button = Button( master = step_op_buttons_frame, text = _( 'Remove step' ), command = op_callbacks[ 'remove_sequence_step' ] )
    step_remove.grid( column = col, row = 0, sticky = 'e' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = step_remove, default_text = 'Remove step' )
    add_translatable( wft )

    col += 1

    step_op_buttons_frame.grid_columnconfigure( index = col, weight = 0 )
    step_abort: Button = Button( master = step_op_buttons_frame, text = _( 'Abort' ), command = op_callbacks[ 'abort_add_sequence_step' ] )
    step_abort.grid( column = col, row = 0, sticky = 'e' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = step_abort, default_text = 'Abort' )
    add_translatable( wft )

    step_form.grid_remove()
