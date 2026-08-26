"""
Create and configure the UI for persistent GUI scripts management.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Frame, Label, Notebook, Treeview
from typing import Callable, cast

from automation_menu.types.persistent_ui_callbacks import PersistentUiCallbacks
from automation_menu.ui.components import op_buttons
from automation_menu.ui.i18n.widget_for_translation import WidgetForTranslation
from automation_menu.ui.types.persistent_ui import PersistentUi


def build_tab_content( ui: PersistentUi, op_callbacks: PersistentUiCallbacks , translate_callback: Callable, translate_store_callback: Callable ) -> PersistentUi:
    """ Build the widgets shown inside the persistent scripts tab.

    Args:
        ui (PersistentUi): UI container to populate.
        op_callbacks (PersistentUiCallbacks): Callbacks for session actions and
            selection handling.
        translate_callback (Callable): Callback used to translate visible text.
        translate_store_callback (Callable): Callback used to register widgets for
            later translation updates.

    Returns:
        (PersistentUi): Populated persistent UI container.
    """

    create_treeview( ui = ui, op_callbacks = op_callbacks, translate_callback = translate_callback, translate_store_callback = translate_store_callback )
    create_info_frame( ui = ui, op_callbacks = op_callbacks, translate_store_callback = translate_store_callback )
    create_info_buttons( ui = ui, op_callbacks = op_callbacks, translate_store_callback = translate_store_callback )

    return ui


def create_info_buttons( ui: PersistentUi, op_callbacks: PersistentUiCallbacks, translate_store_callback: Callable ) -> None:
    """ Create action buttons used to control persistent script sessions.

    Args:
        ui (PersistentUi): UI container to populate.
        op_callbacks (PersistentUiCallbacks): Callbacks for button actions.
        translate_store_callback (Callable): Callback used to register widgets for
            translation.
    """

    ui.op_buttons = op_buttons.get_op_persistent_buttons( parent = ui.main_frame, translate_store_callback = translate_store_callback, op_callbacks = op_callbacks )

    ui.kill_btn = ui.op_buttons.btn_force_stop_script
    ui.show_btn = ui.op_buttons.btn_show
    ui.stop_btn =  ui.op_buttons.btn_stop_script
    ui.resume_btn = ui.op_buttons.btn_resume_script
    ui.pause_btn = ui.op_buttons.btn_pause_script


def create_info_frame( ui: PersistentUi, op_callbacks: PersistentUiCallbacks, translate_store_callback: Callable ) -> None:
    """ Create the detail panel for the selected persistent session.

    Args:
        ui (PersistentUi): UI container to populate.
        op_callbacks (PersistentUiCallbacks): Persistent UI callbacks.
        translate_store_callback (Callable): Callback used to register widgets for
            translation.
    """

    from automation_menu.utils.localization import _

    ui.info_display = Frame( master = ui.main_frame )
    ui.info_display.grid( column = 0, row = 1, sticky = 'we' )

    ui.info_display.grid_columnconfigure( index = 0, weight = 0, minsize = 70 )
    ui.info_display.grid_columnconfigure( index = 1, weight = 0, minsize = 300 )
    ui.info_display.grid_columnconfigure( index = 2, weight = 1 )
    ui.info_display.grid_columnconfigure( index = 3, weight = 1 )
    ui.info_display.grid_rowconfigure( index = 0, weight = 0 )
    ui.info_display.grid_rowconfigure( index = 1, weight = 0 )
    ui.info_display.grid_rowconfigure( index = 2, weight = 0 )
    ui.info_display.grid_rowconfigure( index = 3, weight = 0 )
    ui.info_display.grid_rowconfigure( index = 4, weight = 0 )
    ui.info_display.grid_rowconfigure( index = 5, weight = 0 )

    ui.info_name_title = Label( master = ui.info_display, text = _( 'Script name' ), style = 'BiggerTitle.TLabel' )
    ui.info_name_title.grid( column = 0, row = 0, sticky = 'we' )

    ui.info_name = Label( master = ui.info_display )
    ui.info_name.grid( column = 1, row = 0, sticky = 'we' )

    ui.info_state_title = Label( master = ui.info_display, text = _( 'State' ), style = 'BiggerTitle.TLabel' )
    ui.info_state_title.grid( column = 0, row = 1, sticky = 'we' )

    ui.info_state = Label( master = ui.info_display )
    ui.info_state.grid( column = 1, row = 1, sticky = 'we' )

    ui.info_progress_title = Label( master = ui.info_display, text = _( 'Progress' ), style = 'BiggerTitle.TLabel' )
    ui.info_progress_title.grid( column = 0, row = 2, sticky = 'we' )

    ui.info_progress = Label( master = ui.info_display )
    ui.info_progress.grid( column = 1, row = 2, sticky = 'we' )

    ui.info_status_title = Label( master = ui.info_display, text = _( 'Status' ), style = 'BiggerTitle.TLabel' )
    ui.info_status_title.grid( column = 0, row = 3, sticky = 'we' )

    ui.info_status = Label( master = ui.info_display )
    ui.info_status.grid( column = 1, row = 3, sticky = 'we' )

    ui.info_output_title = Label( master = ui.info_display, text = _( 'Output' ), style = 'BiggerTitle.TLabel' )
    ui.info_output_title.grid( column = 2, row = 0, sticky = 'we' )

    ui.info_output = ScrolledText( master = ui.info_display, state = 'disabled', height = 10 )
    ui.info_output.grid( column = 2, row = 1, rowspan = 5, sticky = 'nswe' )

    ui.info_error_title = Label( master = ui.info_display, text = _( 'Error' ), style = 'BiggerTitle.TLabel' )
    ui.info_error_title.grid( column = 3, row = 0, sticky = 'we' )

    ui.info_error = ScrolledText( master = ui.info_display, state = 'disabled', height = 10 )
    ui.info_error.grid( column = 3, row = 1, rowspan = 5, sticky = 'nswe' )


def create_persistent_tab( tab_control: Notebook, translate_store_callback: Callable ) -> PersistentUi:
    """ Create the persistent scripts tab container and register it for translation.

    Args:
        tab_control (Notebook): Notebook widget that owns the tab.
        translate_store_callback (Callable): Callback used to register widgets for
            translation.

    Returns:
        (PersistentUi): Created persistent UI container.
    """

    from automation_menu.utils.localization import _
    ui: PersistentUi = PersistentUi()
    ui.tab_control = tab_control

    ui.main_frame = Frame( master = tab_control )
    ui.main_frame.grid( sticky = 'nswe' )
    ui.main_frame.grid_columnconfigure( index = 0, weight = 1 )
    ui.main_frame.grid_rowconfigure( index = 0, weight = 1 )
    ui.main_frame.grid_rowconfigure( index = 1, weight = 0 )
    ui.main_frame.grid_rowconfigure( index = 2, weight = 0 )

    tab_control.add( child = ui.main_frame, text = _( 'Persistent GUI''s' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.main_frame, default_text = 'Persistent GUI''s' )
    translate_store_callback( wft )

    return ui


def create_treeview( ui: PersistentUi, translate_store_callback: Callable, translate_callback: Callable, op_callbacks: PersistentUiCallbacks ) -> None:
    """ Create the tree view listing persistent script sessions.

    Args:
        ui (PersistentUi): UI container to populate.
        translate_store_callback (Callable): Callback used to register widgets for
            translation.
        translate_callback (Callable): Callback used to translate visible text.
        op_callbacks (PersistentUiCallbacks): Callbacks for tree view interactions.
    """

    from automation_menu.utils.localization import _

    col_1: str = _( 'Name' )
    col_2: str = _( 'Status' )
    col_3: str = _( 'State' )
    col_4: str = _( 'Progress' )
    col_5: str = _( 'Started at' )

    columns: dict[ str, list[ str | int ] ] = { 'name': [ col_1, 105 ], 'last_status': [ col_2, 160 ], 'state': [ col_3, 160 ], 'progress': [ col_4, 90 ] , 'start_time': [ col_5, 160 ] }
    ui.running_scripts = Treeview( master = ui.main_frame,
                                  columns = list( columns.keys() ),
                                  show = [ 'headings' ] )
    ui.running_scripts.bind( '<<TreeviewSelect>>', op_callbacks.treeview_item_selected )
    ui.running_scripts.bind( '<ButtonRelease-1>', op_callbacks.treeview_click )

    for i, column_def in columns.items():
        ui.running_scripts.column( i, minwidth = cast( int, column_def[ 1 ] ), width = cast( int, column_def[ 1 ] ) )
        ui.running_scripts.heading( i, text = translate_callback( text = column_def[ 0 ] ) )

    ui.running_scripts.grid( column = 0, row = 0, sticky = 'nswe' )

    ui.running_scripts.tag_configure( 'unlaunched',
                                     background = '#EEF3F8',
                                     foreground = '#5B6570',
                                     font = ( 'Calibri', 12, 'italic' ) )
    ui.running_scripts.tag_configure( 'starting',
                                     background = '#D9ECFF',
                                     foreground = 'black',
                                     font = ( 'Calibri', 12, 'bold' ) )
    ui.running_scripts.tag_configure( 'running',
                                     background = '#CFF5D2',
                                     foreground = 'black',
                                     font = ( 'Calibri', 12, 'bold' ) )
    ui.running_scripts.tag_configure( 'paused',
                                     background = '#FFE7A3',
                                     foreground = 'black',
                                     font = ( 'Calibri', 12, 'italic' ) )
    ui.running_scripts.tag_configure( 'stopping',
                                     background = '#FFD6A5',
                                     foreground = 'black',
                                     font = ( 'Calibri', 12, 'bold' ) )
    ui.running_scripts.tag_configure( 'forced_stopping',
                                     background = '#FFB3A7',
                                     foreground = 'black',
                                     font = ( 'Calibri', 12, 'bold' ) )
    ui.running_scripts.tag_configure( 'stopped',
                                     background = 'white',
                                     foreground = 'gray50',
                                     font = ( 'Calibri', 12, 'italic' ) )
    ui.running_scripts.tag_configure( 'stop_failed',
                                     background = '#FFD6D6',
                                     foreground = '#7A0000',
                                     font = ( 'Calibri', 12, 'bold' ) )
    ui.running_scripts.tag_configure( 'forced_stopping_failed',
                                     background = '#FF8A8A',
                                     foreground = 'black',
                                     font = ( 'Calibri', 12, 'bold' ) )
    ui.running_scripts.tag_configure( 'idle',
                                     background = 'white',
                                     foreground = 'black',
                                     font = ( 'Calibri', 12, 'normal' ) )
    ui.running_scripts.tag_configure( 'closed',
                                     background = "#E2DFDF",
                                     foreground = 'black',
                                     font = ( 'Calibri', 12, 'italic' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.running_scripts, default_text = columns )
    translate_store_callback( wft )
