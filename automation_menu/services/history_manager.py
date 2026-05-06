"""
Create a Frame widget for displaying execution history

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from datetime import timedelta
from logging import Logger
from tkinter import END, Event
from tkinter.ttk import Frame, Notebook, Treeview
from typing import Callable, cast

from automation_menu.models import ExecHistory
from automation_menu.ui.tabs.history_tab import build_tab_content, create_history_tab
from automation_menu.ui.types.history_ui import HistoryUi


class HistoryManager:
    def __init__( self, logger: Logger ) -> None:
        """ Manage execution history items UI widgets for display

        Args:
            logger (Logger): Logging object
        """

        self._historylist: list[ ExecHistory ] = []
        self._logger: Logger = logger
        self._history_widgets: HistoryUi


    def _format_duration( self, duration: timedelta ) -> str:
        """ Format a script execution duration as a readable string.

        Current format is `x d x h x m x s`, meaning days, hours,
        minutes, and seconds.

        Args:
            duration (timedelta): Time difference between script start and finish.

        Returns:
            (str): Formatted duration string.
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
        """ Handle selection of a history item in the tree view.

        Args:
            event (Event): Event that triggered the handler.
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
        self._history_widgets.item_start.config( state = 'normal' )
        self._history_widgets.item_start.delete( '1.0', END )

        self._history_widgets.item_start.insert( 'end', item.start.strftime( '%Y-%m-%d : %H:%M:%S' ) )

        self._history_widgets.item_start.config( state = 'disabled' )

        # Display end
        self._history_widgets.item_end.config( state = 'normal' )
        self._history_widgets.item_end.delete( '1.0', END )

        self._history_widgets.item_end.insert( 'end', item.end.strftime( '%Y-%m-%d : %H:%M:%S' ) )

        self._history_widgets.item_end.config( state = 'disabled' )

        # Display duration
        self._history_widgets.duration.config( state = 'normal' )
        self._history_widgets.duration.delete( '1.0', END )

        duration = self._format_duration( duration = ( item.end - item.start ) )
        self._history_widgets.duration.insert( 'end', duration )

        self._history_widgets.duration.config( state = 'disabled' )

        # Display execution output
        self._history_widgets.item_output.config( state = 'normal' )
        self._history_widgets.item_output.delete( '1.0', END )

        for o in item.output:
            self._history_widgets.item_output.insert( 'end', f'{ str( o ) }\n' )

        self._history_widgets.item_output.config( state = 'disabled' )


    def add_history_item( self, item: ExecHistory ) -> None:
        """ Add an execution history item to the UI and internal list.

        Args:
            item (ExecHistory): Execution history to add
        """

        if hasattr( self, '_history_widgets' ) and hasattr( self._history_widgets, 'history_tree' ):
            tree_id: str = self._history_widgets.history_tree.insert( parent = '',
                                    index = 0,
                                    text = f'{ item.start.strftime( '%m / %d : %H:%M:%S' ) }',
                                    values = ( item.script_info.get_attr( 'filename' ) )
                                    )
            item.list_id = tree_id

        else:
            tree_id = '0'

        self._historylist.append( item )


    def build_tab_content( self, translate_store_callback: Callable, translate_callback: Callable ) -> None:
        """ Create widgets for displaying execution history content.

        Args:
            translate_store_callback (Callable): Function callback to store widgets for later translation
            translate_callback (Callable): Function callback to translate text
        """

        self._history_widgets = build_tab_content( tab_control = self._tab, translate_store_callback = translate_store_callback, translate_callback = translate_callback )

        self._history_widgets.history_tree.bind( '<<TreeviewSelect>>', self._history_item_selected )

        for item in self._historylist:
            tree_id: str = self._history_widgets.history_tree.insert( parent = '',
                        index = 0,
                        text = f'{ item.start.strftime( '%m / %d : %H:%M:%S' ) }',
                        values = ( item.script_info.get_attr( 'filename' ) )
                        )

            item.list_id = tree_id


    def create_tab( self, parent_tab: Notebook, translate_store_callback: Callable ) ->  Frame:
        """ Create the frame used to display execution history.

        Args:
            parent_tab (Notebook): Notebook widget to attach the history tab to.
            translate_store_callback (Callable): Callback used to register widgets for translation.

        Returns:
            (Frame): Frame containing the history UI.
        """

        from automation_menu.utils.localization import _

        self._tab: Frame = create_history_tab( tab_control = parent_tab, translate_store_callback = translate_store_callback )

        return self._tab


    def get_history_list( self ) -> list[ dict ]:
        """ Get the stored execution history as dictionaries.

        Returns:
            (list[dict]): Execution history items converted to dictionaries.
        """

        return [ item.to_dict() for item in self._historylist ]
