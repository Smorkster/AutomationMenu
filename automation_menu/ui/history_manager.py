"""
Create a Frame widget for displaying execution history

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0
Created: 2025-10-08
"""

from __future__ import annotations

from datetime import timedelta
from logging import Logger
from tkinter import END, N, S, W, E, Event, Text
from tkinter.ttk import Frame, Label, Notebook, Treeview
from typing import Any, Callable, cast

from automation_menu.models import ExecHistory
from automation_menu.models.widget_for_translation import WidgetForTranslation


class HistoryManager:
    def __init__( self, logger: Logger ) -> None:
        """ Manage execution history items UI widgets for display

        Args:
            logger (Logger): Logging object
        """

        self._historylist: list[ ExecHistory ] = []
        self._logger: Logger = logger


    def _format_duration( self, duration: timedelta ) -> str:
        """ Format duration of script execution
        Current format is: x d x h x m x s
        Meanin days, hours, minutes, seconds

        Args:
            duration (timedelta): Time difference between start and finish
        """

        from automation_menu.utils.localization import _

        text_parts: list[ str ] = []
        days: int = duration.days
        hours, remainder = divmod( duration.seconds, 3600 )
        minutes, seconds = divmod( remainder, 60 )

        if days > 0:
            text_parts.append( _( '{d} d' ).format( d = days ) )

        if hours > 0:
            text_parts.append( _( '{h} h' ).format( h = hours ) )

        if minutes > 0:
            text_parts.append( _( '{m} m' ).format( m = minutes ) )

        if seconds > 0:
            text_parts.append( _( '{s} s' ).format( s = seconds ) )

        return " ".join( text_parts )


    def _history_item_selected( self, event: Event ) -> None:
        """ Eventhandler for when tree item has been selected

        Args:
            event (Event): Event triggering handler
        """

        selection: tuple[ str, ... ] = cast( Treeview, event.widget ).selection()
        if not selection:

            return

        from automation_menu.utils.localization import _

        id: str = selection[ 0 ]

        list_item: list[ ExecHistory ] = [ a for a in self._historylist if a.list_id == id ]

        if not list_item:
            self._logger.warning( _( 'No history item for {i}' ).format( i = id ) )

            return

        item: ExecHistory = list_item[ 0 ]

        # Display start
        self.item_start.config( state = 'normal' )
        self.item_start.delete( '1.0', END )

        self.item_start.insert( 'end', item.start.strftime( '%Y-%m-%d : %H:%M:%S' ) )

        self.item_start.config( state = 'disabled' )

        # Display end
        self.item_end.config( state = 'normal' )
        self.item_end.delete( '1.0', END )

        self.item_end.insert( 'end', item.end.strftime( '%Y-%m-%d : %H:%M:%S' ) )

        self.item_end.config( state = 'disabled' )

        # Display duration
        self.duration.config( state = 'normal' )
        self.duration.delete( '1.0', END )

        duration = self._format_duration( duration = ( item.end - item.start ) )
        self.duration.insert( 'end', duration )

        self.duration.config( state = 'disabled' )

        # Display execution output
        self.item_output.config( state = 'normal' )
        self.item_output.delete( '1.0', END )

        for o in item.output:
            self.item_output.insert( 'end', f'{ str( o ) }\n' )

        self.item_output.config( state = 'disabled' )


    def add_history_item( self, item: ExecHistory ) -> None:
        """ Adds a new item to the treewidget, and history list

        Args:
            item (ExecHistory): Execution history to add
        """

        if hasattr( self, 'history_tree' ):
            tree_id: str = self.history_tree.insert( parent = '',
                                    index = 0,
                                    text = f'{ item.start.strftime( '%m / %d : %H:%M:%S' ) }',
                                    values = ( item.script_info.get_attr( 'filename' ) )
                                    )
            item.list_id = tree_id

        else:
            tree_id = '0'

        self._historylist.append( item )


    def get_history_list( self ) -> list[ dict ]:
        """ Summarize execution history list to a string"""

        return [ item.to_dict() for item in self._historylist ]


    def get_history_tab( self, tabcontrol: Notebook, translate_store_callback: Callable ) ->  Frame:
        """ Creates the widgets to display execution history

        Args:
            tabcontrol (Notebook): A notebook widget to attach the widgets to
            translate_store_callback (Callable): Function callback to add widget for translation
            translate_callback (Callable): Function callback to translate string

        Returns:
            tabHistory (Frame): Frame containing history UI
        """

        from automation_menu.utils.localization import _

        self.tabHistory: Frame = Frame( master = tabcontrol, name = 'history' )
        self.tabHistory.grid( column = 0, row = 0, sticky = 'nswe' )
        self.tabHistory.columnconfigure( index = 0, weight = 0 )
        self.tabHistory.columnconfigure( index = 1, weight = 1 )
        self.tabHistory.rowconfigure( index = 0, weight = 1 )

        tabcontrol.add( child = self.tabHistory, text = _( 'Execution history' ) )

        wft: WidgetForTranslation = WidgetForTranslation( widget = self.tabHistory, default_text = 'Execution history' )
        translate_store_callback( wft )

        return self.tabHistory


    def build_tab_content( self, translate_store_callback: Callable, translate_callback: Callable ) -> None:
        """ Create widgets for displaying execution history content

        Args:
            translate_store_callback (Callable): Function callback to store widgets for later translation
            translate_callback (Callable): Function callback to translate text
        """

        from automation_menu.utils.localization import _

        columns: dict[ str, list[ str | int ] ] = { '#0': [ 'Started', 105 ], 'name': [ 'Name', 160 ] }
        self.history_tree: Treeview = Treeview( self.tabHistory, columns = [ *columns.keys() ][ 1: ] )

        for i, s in columns.items():
            self.history_tree.column( i, minwidth = cast( int, s[ 1 ] ), width = cast( int, s[ 1 ] ) )
            self.history_tree.heading( i, text = translate_callback( text = s[ 0 ] ) )


        self.history_tree.grid( column = 0, rowspan = 3, sticky = 'nsw' )
        self.history_tree.bind( '<<TreeviewSelect>>', self._history_item_selected )

        wft: WidgetForTranslation = WidgetForTranslation( widget = self.history_tree, default_text = columns )
        translate_store_callback( wft )

        for item in self._historylist:
            tree_id: str = self.history_tree.insert( parent = '',
                        index = 0,
                        text = f'{ item.start.strftime( '%m / %d : %H:%M:%S' ) }',
                        values = ( item.script_info.get_attr( 'filename' ) )
                        )

            item.list_id = tree_id

        self.history_item_display: Frame = Frame( self.tabHistory )
        self.history_item_display.grid( column = 1, row = 0, sticky = 'nswe' )
        self.history_item_display.columnconfigure( index = 0, weight = 0 )
        self.history_item_display.columnconfigure( index = 1, weight = 1 )
        self.history_item_display.rowconfigure( index = 0, weight = 0 )
        self.history_item_display.rowconfigure( index = 1, weight = 0 )
        self.history_item_display.rowconfigure( index = 2, weight = 0 )
        self.history_item_display.rowconfigure( index = 3, weight = 0 )
        self.history_item_display.rowconfigure( index = 4, weight = 1 )

        item_start_title: Label = Label( master = self.history_item_display, text = _( 'Started' ), style = 'History.TLabel' )
        item_start_title.grid( column = 0, row = 0, padx = 5, pady = 5, sticky = 'nw' )

        wft: WidgetForTranslation = WidgetForTranslation( widget = item_start_title, default_text = 'Started' )
        translate_store_callback( wft )

        self.item_start: Text = Text( master = self.history_item_display, height = 1, state = 'disabled', font = ( 'Calibri', 12, 'normal' ) )
        self.item_start.grid( column = 1, row = 0, padx = 5, pady = 5, sticky = 'we' )

        item_end_title: Label = Label( master = self.history_item_display, text = _( 'Ended' ), style = 'History.TLabel' )
        item_end_title.grid( column = 0, row = 1, padx = 5, pady = 5, sticky = 'nw' )

        wft: WidgetForTranslation = WidgetForTranslation( widget = item_end_title, default_text = 'Ended' )
        translate_store_callback( wft )

        self.item_end: Text = Text( master = self.history_item_display, height = 1, state = 'disabled', font = ( 'Calibri', 12, 'normal' ) )
        self.item_end.grid( column = 1, row = 1, padx = 5, pady = 5, sticky = 'we' )

        duration_title: Label = Label( master = self.history_item_display, text = _( 'Duration' ), style = 'History.TLabel' )
        duration_title.grid( column = 0, row = 2, padx = 5, pady = 5, sticky = 'nw' )

        wft: WidgetForTranslation = WidgetForTranslation( widget = duration_title, default_text = 'Duration' )
        translate_store_callback( wft )

        self.duration: Text = Text( master = self.history_item_display, height = 1, state = 'disabled', font = ( 'Calibri', 12, 'normal' ) )
        self.duration.grid( column = 1, row = 2, padx = 5, pady = 5, sticky = 'we' )

        item_output_title: Label = Label( master = self.history_item_display, text = _( 'Generated output' ), style = 'History.TLabel' )
        item_output_title.grid( column = 0, columnspan = 2, row = 3, padx = 5, pady = 5, sticky = 'nw' )

        wft: WidgetForTranslation = WidgetForTranslation( widget = item_output_title, default_text= 'Generated output' )
        translate_store_callback( wft )

        self.item_output: Text = Text( master = self.history_item_display, state = 'disabled', font = ( 'Calibri', 12, 'normal' ) )
        self.item_output.grid( column = 0, columnspan = 2, row = 4, padx = 5, pady = 5, sticky = 'nswe' )
