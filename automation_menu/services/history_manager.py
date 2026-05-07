"""
Create a Frame widget for displaying execution history

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from datetime import timedelta
from logging import Logger
from tkinter.ttk import Frame, Notebook
from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext

from automation_menu.models import ExecHistory
from automation_menu.ui.controllers.history_ui_controller import HistoryUiController
from automation_menu.ui.tabs.history_tab import build_tab_content, create_history_tab
from automation_menu.ui.types.history_ui import HistoryUi


class HistoryManager:
    def __init__( self, app_context: ApplicationContext ) -> None:
        """ Manage execution history items UI widgets for display

        Args:
            app_context (ApplicationContext): Context and manager container for the application.
        """

        self.app_context = app_context
        self._logger: Logger = app_context.debug_logger

        self._historylist: list[ ExecHistory ] = []
        self._history_callbacks: dict = {}

        self._history_widgets: HistoryUi
        self._history_ui_controller: HistoryUiController = HistoryUiController( app_context = self.app_context,
                                                                               history_manager = self,
                                                                               logger = self.app_context.debug_logger )


    def _add_callbacks( self ) -> None:
        """ Context and manager container for the application. """

        self._history_callbacks[ 'history_item_selected' ] = self._history_ui_controller.history_item_selected


    def format_duration( self, duration: timedelta ) -> str:
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

        self._add_callbacks()
        self._history_widgets = build_tab_content( tab_control = self._tab,
                                                  op_callbacks = self._history_callbacks,
                                                  translate_store_callback = translate_store_callback,
                                                  translate_callback = translate_callback )
        self._history_ui_controller.bind_ui( ui = self._history_widgets )

        for item in self._historylist:
            tree_id: str = self._history_widgets.history_tree.insert( parent = '',
                                                                     index = 0,
                                                                     text = f'{ item.start.strftime( '%m / %d : %H:%M:%S' ) }',
                                                                     values = ( item.script_info.get_attr( 'filename' ) ) )

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


    def get_history_item( self, list_id: str ) -> ExecHistory:
        """ Return the execution history item associated with a tree view item id.

        Args:
            list_id (str): Tree view item identifier for the history entry.

        Returns:
            (ExecHistory): Matching execution history item.

        Raises:
            ValueError: If no history item exists for the provided tree view id.
        """

        items = [ a for a in self._historylist if a.list_id == list_id ]

        if not items:

            from automation_menu.utils.localization import _

            self._logger.warning( _( 'No history item for {i}' ).format( i = list_id ) )

            raise ValueError( _( 'Couldn\'t find history item from list id \'{ id }\'' ).format( id = list_id ) )

        return items[ 0 ]


    def get_history_list( self ) -> list[ dict ]:
        """ Get the stored execution history as dictionaries.

        Returns:
            (list[dict]): Execution history items converted to dictionaries.
        """

        return [ item.to_dict() for item in self._historylist ]
