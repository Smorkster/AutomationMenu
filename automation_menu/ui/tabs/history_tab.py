"""
Create a Frame and a Text widget for displaying output from a running script

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from tkinter import Text
from tkinter.ttk import Frame, Label, Notebook, Treeview
from typing import Callable, cast

from automation_menu.ui.types.history_ui import HistoryUi
from automation_menu.ui.types.widget_for_translation import WidgetForTranslation


def build_tab_content( tab_control: Frame, translate_store_callback: Callable, translate_callback: Callable ) -> HistoryUi:
    """ Create widgets for displaying execution history content.

    Args:
        tab_control (Frame): Frame to build the history tab content inside.
        translate_store_callback (Callable): Callback used to register widgets for later translation.
        translate_callback (Callable): Callback used to translate displayed text.

    Returns:
        ui (HistoryUi): Created history UI widget collection.
    """

    from automation_menu.utils.localization import _

    ui: HistoryUi = HistoryUi()
    ui.tabHistory = tab_control

    columns: dict[ str, list[ str | int ] ] = { '#0': [ 'Started', 105 ], 'name': [ 'Name', 160 ] }
    ui.history_tree = Treeview( tab_control, columns = [ *columns.keys() ][ 1: ], )

    for i, s in columns.items():
        ui.history_tree.column( i, minwidth = cast( int, s[ 1 ] ), width = cast( int, s[ 1 ] ) )
        ui.history_tree.heading( i, text = translate_callback( text = s[ 0 ] ) )

    ui.history_tree.grid( column = 0, rowspan = 3, sticky = 'nsw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = ui.history_tree, default_text = columns )
    translate_store_callback( wft )

    ui.history_item_display = Frame( ui.tabHistory )
    ui.history_item_display.grid( column = 1, row = 0, sticky = 'nswe' )
    ui.history_item_display.columnconfigure( index = 0, weight = 0 )
    ui.history_item_display.columnconfigure( index = 1, weight = 1 )
    ui.history_item_display.rowconfigure( index = 0, weight = 0 )
    ui.history_item_display.rowconfigure( index = 1, weight = 0 )
    ui.history_item_display.rowconfigure( index = 2, weight = 0 )
    ui.history_item_display.rowconfigure( index = 3, weight = 0 )
    ui.history_item_display.rowconfigure( index = 4, weight = 1 )

    item_start_title: Label = Label( master = ui.history_item_display, text = _( 'Started' ), style = 'History.TLabel' )
    item_start_title.grid( column = 0, row = 0, padx = 5, pady = 5, sticky = 'nw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = item_start_title, default_text = 'Started' )
    translate_store_callback( wft )

    ui.item_start = Text( master = ui.history_item_display, height = 1, state = 'disabled', font = ( 'Calibri', 12, 'normal' ) )
    ui.item_start.grid( column = 1, row = 0, padx = 5, pady = 5, sticky = 'we' )

    item_end_title: Label = Label( master = ui.history_item_display, text = _( 'Ended' ), style = 'History.TLabel' )
    item_end_title.grid( column = 0, row = 1, padx = 5, pady = 5, sticky = 'nw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = item_end_title, default_text = 'Ended' )
    translate_store_callback( wft )

    ui.item_end = Text( master = ui.history_item_display, height = 1, state = 'disabled', font = ( 'Calibri', 12, 'normal' ) )
    ui.item_end.grid( column = 1, row = 1, padx = 5, pady = 5, sticky = 'we' )

    duration_title: Label = Label( master = ui.history_item_display, text = _( 'Duration' ), style = 'History.TLabel' )
    duration_title.grid( column = 0, row = 2, padx = 5, pady = 5, sticky = 'nw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = duration_title, default_text = 'Duration' )
    translate_store_callback( wft )

    ui.duration = Text( master = ui.history_item_display, height = 1, state = 'disabled', font = ( 'Calibri', 12, 'normal' ) )
    ui.duration.grid( column = 1, row = 2, padx = 5, pady = 5, sticky = 'we' )

    item_output_title: Label = Label( master = ui.history_item_display, text = _( 'Generated output' ), style = 'History.TLabel' )
    item_output_title.grid( column = 0, columnspan = 2, row = 3, padx = 5, pady = 5, sticky = 'nw' )

    wft: WidgetForTranslation = WidgetForTranslation( widget = item_output_title, default_text= 'Generated output' )
    translate_store_callback( wft )

    ui.item_output = Text( master = ui.history_item_display, state = 'disabled', font = ( 'Calibri', 12, 'normal' ) )
    ui.item_output.grid( column = 0, columnspan = 2, row = 4, padx = 5, pady = 5, sticky = 'nswe' )

    return ui


def create_history_tab( tab_control: Notebook, translate_store_callback: Callable ) ->  Frame:
    """ Create the execution history tab container.

    Args:
        tab_control (Notebook): Notebook widget to attach the history tab to.
        translate_store_callback (Callable): Callback used to register widgets for translation.

    Returns:
        tabHistory (Frame): Frame containing the history UI.
    """

    from automation_menu.utils.localization import _

    tabHistory: Frame = Frame( master = tab_control, name = 'history' )
    tabHistory.grid( column = 0, row = 0, sticky = 'nswe' )
    tabHistory.columnconfigure( index = 0, weight = 0 )
    tabHistory.columnconfigure( index = 1, weight = 1 )
    tabHistory.rowconfigure( index = 0, weight = 1 )

    tab_control.add( child = tabHistory, text = _( 'Execution history' ) )

    wft: WidgetForTranslation = WidgetForTranslation( widget = tabHistory, default_text = 'Execution history' )
    translate_store_callback( wft )

    return tabHistory

