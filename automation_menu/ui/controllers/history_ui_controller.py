"""
Handle history tab UI interactions and selection-driven detail updates.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from logging import Logger
from tkinter import END, Event
from tkinter.ttk import Treeview
from typing import cast

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.services.history_manager import HistoryManager

from automation_menu.models.exechistory import ExecHistory
from automation_menu.ui.types.history_ui import HistoryUi


class HistoryUiController:
    """ Handle history tab interactions and update the bound history UI."""

    def __init__( self, app_context: 'ApplicationContext', history_manager: HistoryManager, logger: Logger ) -> None:
        """ Initialize the history UI controller.

        Args:
            app_context (ApplicationContext): Shared application context.
            history_manager (HistoryManager): Manager providing history data and helpers.
            logger (Logger): Logger used for controller warnings and diagnostics.
        """

        self.app_context: ApplicationContext = app_context
        self._history_manager: HistoryManager = history_manager
        self._logger: Logger = logger

        self._history_ui: HistoryUi


    def bind_ui( self, ui: HistoryUi ) -> None:
        """ Bind the history tab widgets to the controller.

        Args:
            ui (HistoryUi): Widget collection used for displaying history details.
        """

        self._history_ui = ui


    def history_item_selected( self, event: Event ) -> None:
        """ Display details for the selected history entry.

        Args:
            event (Event): Tree view selection event that triggered the handler.
        """

        selection: tuple[ str, ... ] = cast( Treeview, event.widget ).selection()
        if not selection:

            return

        from automation_menu.utils.localization import _

        id: str = selection[ 0 ]

        item: ExecHistory = self._history_manager.get_history_item( list_id = id )

        # Display start
        self._history_ui.item_start.config( state = 'normal' )
        self._history_ui.item_start.delete( '1.0', END )

        self._history_ui.item_start.insert( 'end', item.start.strftime( '%Y-%m-%d : %H:%M:%S' ) )

        self._history_ui.item_start.config( state = 'disabled' )

        # Display end
        self._history_ui.item_end.config( state = 'normal' )
        self._history_ui.item_end.delete( '1.0', END )

        self._history_ui.item_end.insert( 'end', item.end.strftime( '%Y-%m-%d : %H:%M:%S' ) )

        self._history_ui.item_end.config( state = 'disabled' )

        # Display duration
        self._history_ui.duration.config( state = 'normal' )
        self._history_ui.duration.delete( '1.0', END )

        duration = self._history_manager.format_duration( duration = ( item.end - item.start ) )
        self._history_ui.duration.insert( 'end', duration )

        self._history_ui.duration.config( state = 'disabled' )

        # Display execution output
        self._history_ui.item_output.config( state = 'normal' )
        self._history_ui.item_output.delete( '1.0', END )

        for o in item.output:
            self._history_ui.item_output.insert( 'end', f'{ str( o ) }\n' )

        self._history_ui.item_output.config( state = 'disabled' )
