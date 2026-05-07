"""
Control lazy initialization and switching of main application tabs.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

from tkinter import Event
from tkinter.ttk import Frame, Notebook
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext

from automation_menu.ui.types.exec_tab_refs import ExecutionTabUiRefs
from automation_menu.utils.decorators import ui_guard_method
from automation_menu.utils.localization import translate


class ExecutionTabUiController:
    """ Control creation and lazy loading of execution-related tabs."""

    def __init__( self, app_context: 'ApplicationContext', exec_bindings: ExecutionTabUiRefs ) -> None:
        """ Initialize the tab UI controller.

        Args:
            app_context ('ApplicationContext'): Shared application context.
            exec_bindings (ExecutionTabUiRefs): Widget references used for tab management.
        """

        self.app_context = app_context
        self.tab_ui_bindings = exec_bindings

        self._tabs_build = {}


    def init_tabs( self ) -> None:
        """ Create the main tabs and register tab change handling."""

        tab_index = 0

        # Create sequence tab
        tab_index += 1
        self.sequence_tab: Frame = self.app_context.SequenceManager.create_tab( parent_tab = self.tab_ui_bindings.tab_control )
        self._tabs_build[ tab_index ] = { 'idx': tab_index, 'built': False }

        # Create settings tab
        tab_index += 1
        self.tabSettings: Frame = self.app_context.SettingsManager.create_tab( parent_tab = self.tab_ui_bindings.tab_control )
        self._tabs_build[ tab_index ] = { 'idx': tab_index, 'built': False }

        # Create history tab
        tab_index += 1
        self.tabHistory: Frame = self.app_context.HistoryManager.create_tab( parent_tab = self.tab_ui_bindings.tab_control, translate_store_callback = self.app_context.LanguageManager.add_translatable_widget )
        self._tabs_build[ tab_index ] = { 'idx': tab_index, 'built': False }

        self.tab_ui_bindings.tab_control.bind( '<<NotebookTabChanged>>', self._on_tab_change )
        self.tab_ui_bindings.tab_control.grid( column = 0, columnspan = 2, row = 2, sticky = 'nswe' )


    @ui_guard_method( when_message = 'Tab change' )
    def _on_tab_change( self, event: Event | None = None ) -> None:
        """ Handle notebook tab changes and lazily build tab content.

        Args:
            event (Event | None): Event that triggered the handler.
        """

        if event is None or not isinstance( event.widget, Notebook ):

            return

        idx = event.widget.index( 'current' )

        if not self._tabs_build.get( idx, {} ).get( 'built', True ):
            if idx == 1:
                self.app_context.SequenceManager.build_tab_content()

            elif idx == 2:
                self.app_context.SettingsManager.build_tab_content()

            elif idx == 3:
                self.app_context.HistoryManager.build_tab_content( translate_store_callback = self.app_context.LanguageManager.add_translatable_widget, translate_callback = translate )

            self._tabs_build[ idx ][ 'built' ] = True
