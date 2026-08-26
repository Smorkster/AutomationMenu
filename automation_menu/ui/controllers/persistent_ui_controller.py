"""
Control persistent GUI-related UI behavior and interactions.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from __future__ import annotations
from tkinter import END, Event
from tkinter.ttk import Treeview
from typing import Callable, Literal, cast

from automation_menu.models.enums import ExecutionState
from automation_menu.models.persistent_execution_session import PersistentExecutionSession
from automation_menu.types.persistent_manager_callbacks import PersistentManagerCallbacks
from automation_menu.ui.types.persistent_ui import PersistentUi
from automation_menu.utils.decorators import ui_guard_method


class PersistentUiController:
    """ Control the persistent scripts UI and its user interactions. """

    def __init__( self ) -> None:
        """ Initialize controller state and button availability rules. """

        self._execution_ui: PersistentUi
        self._list_item_selected: str
        self._manager_callbacks: PersistentManagerCallbacks

        self._BUTTON_NAMES = ( 'show_btn', 'stop_btn', 'kill_btn', 'resume_btn', 'pause_btn' )
        self._BUTTON_STATES_BY_EXECUTION_STATE = { ExecutionState.UNLAUNCHED: frozenset( { 'show_btn', 'stop_btn', 'kill_btn', 'pause_btn' } ),
                                                  ExecutionState.STARTING: frozenset( { 'show_btn', 'stop_btn', 'kill_btn' } ),
                                                  ExecutionState.IDLE: frozenset( { 'show_btn', 'stop_btn', 'kill_btn', 'pause_btn' } ),
                                                  ExecutionState.RUNNING: frozenset( { 'show_btn', 'stop_btn', 'kill_btn', 'pause_btn' } ),
                                                  ExecutionState.PAUSED: frozenset( { 'show_btn', 'stop_btn', 'kill_btn', 'resume_btn' } ),
                                                  ExecutionState.PAUSED_BY_SCRIPT: frozenset( { 'show_btn', 'stop_btn', 'kill_btn' } ),
                                                  ExecutionState.STOPPING: frozenset( { 'show_btn', 'kill_btn' } ),
                                                  ExecutionState.FORCED_STOPPING: frozenset(),
                                                  ExecutionState.STOPPED: frozenset(),
                                                  ExecutionState.STOP_FAILED: frozenset( { 'show_btn', 'stop_btn', 'kill_btn' } ),
                                                  ExecutionState.FORCED_STOPPING_FAILED: frozenset( { 'show_btn', 'kill_btn' } ),
                                                  ExecutionState.CLOSED: frozenset(), }


    def _set_op_button_states( self, state: ExecutionState | None ) -> None:
        """ Enable or disable action buttons for the selected session state.

        Args:
            state (ExecutionState | None): Execution state used to determine which
                actions should be available.
        """

        enabled: frozenset = self._BUTTON_STATES_BY_EXECUTION_STATE.get( state, frozenset() ) if state else frozenset()

        for button_name in self._BUTTON_NAMES:
            getattr( self._execution_ui, button_name ).config( state = '!disabled' if button_name in enabled else 'disabled' )


    def add_session( self, session: PersistentExecutionSession ) -> bool:
        """ Insert a session into the tree view when the tab is ready.

        Args:
            session (PersistentExecutionSession): Session to display in the tree view.

        Returns:
            (bool): True if the session was added, otherwise False.
        """

        if not self.has_content():

            return False

        try:
            id: str = self._execution_ui.running_scripts.insert( '', 'end', values = session.get_list_data() )

            session.row_id = id

            return True

        except Exception as e:

            return False


    def bind_ui( self, ui: PersistentUi, manager_callbacks: PersistentManagerCallbacks ) -> None:
        """ Bind UI widgets and manager callbacks to this controller.

        Args:
            ui (PersistentUi): Persistent UI widget container.
            manager_callbacks (PersistentManagerCallbacks): Manager callbacks used to
                resolve and act on sessions.
        """

        self._execution_ui = ui
        self._manager_callbacks = manager_callbacks


    def force_stop_script( self ) -> bool:
        """ Force stop the currently selected persistent session.

        Returns:
            (bool): True after the stop request has been issued.
        """

        s: PersistentExecutionSession = self._manager_callbacks.get_session_by_row_id( self._list_item_selected )
        s.force_stop_runner()

        return True


    def has_content( self ) -> bool:
        """ Return whether the controller has been bound to a built UI.

        Returns:
            (bool): True if the required widgets are available, otherwise False.
        """

        return ( hasattr( self, '_execution_ui' ) and
                hasattr( self._execution_ui, 'running_scripts' ) and
                hasattr( self._execution_ui, 'info_name' ) )


    def pause_script( self ) -> None:
        """ Pause the currently selected persistent session. """

        s: PersistentExecutionSession = self._manager_callbacks.get_session_by_row_id( self._list_item_selected )
        s.pause_runner()


    def resume_script( self ) -> None:
        """ Resume the currently selected persistent session. """

        s: PersistentExecutionSession = self._manager_callbacks.get_session_by_row_id( self._list_item_selected )
        s.resume_runner()


    def select_list_item( self, id: str ) -> None:
        """ Select and focus a session row in the tree view.

        Args:
            id (str): Tree view row identifier to focus.
        """

        self._list_item_selected = id

        if not self.has_content():

            return

        self._execution_ui.running_scripts.focus( id )
        self._execution_ui.running_scripts.selection_set( id )


    def show_script( self ) -> None:
        """ Show the main window for the selected persistent session. """

        s: PersistentExecutionSession = self._manager_callbacks.get_session_by_row_id( self._list_item_selected )
        s.show_main_window()


    def stop_script( self ) -> bool:
        """ Request a graceful stop for the selected persistent session.

        Returns:
            (bool): True after the stop request has been issued.
        """

        s: PersistentExecutionSession = self._manager_callbacks.get_session_by_row_id( self._list_item_selected )
        s.stop_runner()

        return True


    def treeview_click( self, event: Event ) -> None:
        """ Handle mouse clicks in the sessions tree view.

        Args:
            event (Event): Tkinter event describing the mouse interaction.
        """

        tree = cast( Treeview, event.widget )
        item_id: str = tree.focus()

        if not tree.identify_element( event.x, event.y ):
            if len( tree.selection() ) > 0:
                tree.selection_remove( tree.selection() )


    def treeview_item_selected( self, event: Event | None = None ) -> None:
        """ Refresh the detail panel when the selected tree item changes.

        Args:
            event (Event | None): Tree view selection event, if one was provided.
        """

        if not event or not self.has_content():

            return

        tree = cast( Treeview, event.widget )
        item_id: tuple[ str, ... ] = tree.selection()

        if not item_id:
            self._execution_ui.info_name.config( text = '' )
            self._execution_ui.info_status.config( text = '' )
            self._execution_ui.info_state.config( text = '' )
            self._execution_ui.info_progress.config( text = '' )
            self._execution_ui.info_error.config( state = 'normal' )
            self._execution_ui.info_error.delete( '1.0', END )
            self._execution_ui.info_error.config( state = 'disabled' )
            self._execution_ui.info_output.config( state = 'normal' )
            self._execution_ui.info_output.delete( '1.0', END )
            self._execution_ui.info_output.config( state = 'disabled' )

            self._set_op_button_states( None )

        else:
            self._list_item_selected = item_id[ 0 ]
            item: list | Literal[ '' ] = tree.item( item_id[ 0 ] ).get( 'values', [] )

            s: PersistentExecutionSession = self._manager_callbacks.get_session_by_row_id( item_id[ 0 ] )

            self._execution_ui.info_name.config( text = s.script_info.filename ) # item[ 0 ] )
            self._execution_ui.info_status.config( text = s.status ) #item[ 1 ] )
            self._execution_ui.info_state.config( text = s.state ) #item[ 2 ] )
            self._execution_ui.info_progress.config( text = s.progress ) #item[ 3 ] )

            self._execution_ui.info_error.config( state = 'normal' )
            self._execution_ui.info_error.delete( '1.0', END )
            self._execution_ui.info_error.insert( 'end', s.get_all_error() )
            self._execution_ui.info_error.config( state = 'disabled' )
            self._execution_ui.info_output.config( state = 'normal' )
            self._execution_ui.info_output.delete( '1.0', END )
            self._execution_ui.info_output.insert( 'end', s.get_all_output() )
            self._execution_ui.info_output.config( state = 'disabled' )

            self._set_op_button_states( s.state )


    def update_error( self, row_id: str, error: str ) -> None:
        """ Append error text to the selected session's error display.

        Args:
            row_id (str): Tree view row id for the updated session.
            error (str): Error text to append.
        """

        if not self.has_content() or not row_id:

            return

        if self._execution_ui.running_scripts.focus() == row_id:
            self._execution_ui.info_error.config( state = 'normal' )
            self._execution_ui.info_error.insert( 'end', error )
            self._execution_ui.info_error.config( state = 'disabled' )


    def update_output( self, row_id: str, output: str ) -> None:
        """ Append output text to the selected session's output display.

        Args:
            row_id (str): Tree view row id for the updated session.
            output (str): Output text to append.
        """

        if not self.has_content() or not row_id:

            return

        if self._execution_ui.running_scripts.focus() == row_id:
            self._execution_ui.info_output.config( state = 'normal' )
            self._execution_ui.info_output.insert( 'end', output )
            self._execution_ui.info_output.config( state = 'disabled' )


    def update_progress( self, row_id: str, progress: float ) -> None:
        """ Update progress values in the list and detail panel.

        Args:
            row_id (str): Tree view row id for the updated session.
            progress (float): New progress value.
        """

        if not self.has_content() or not row_id:

            return

        list_item = self._execution_ui.running_scripts.item( row_id )
        values = list( list_item.get( 'values' ) )

        if len( values ) >= 3:

            values[ 3 ] = str( progress )
            self._execution_ui.running_scripts.item( row_id, values = values )

        if self._execution_ui.running_scripts.focus() == row_id:
            self._execution_ui.info_progress.config( text = str( progress ) )


    def update_state( self, row_id: str, state: ExecutionState ) -> None:
        """ Update state values in the list and detail panel.

        Args:
            row_id (str): Tree view row id for the updated session.
            state (ExecutionState): New execution state.
        """

        if not self.has_content() or not row_id:

            return

        list_item = self._execution_ui.running_scripts.item( row_id )
        values = list( list_item.get( 'values' ) )

        if len( values ) >= 3:

            values[ 2 ] = state.name
            self._execution_ui.running_scripts.item( row_id, values = values, tags = ( state.value, ) )

        if self._execution_ui.running_scripts.focus() == row_id:
            self._execution_ui.info_state.config( text = state.name )

        self._set_op_button_states( state )


    def update_status( self, row_id: str, status: str ) -> None:
        """ Update status values in the list and detail panel.

        Args:
            row_id (str): Tree view row id for the updated session.
            status (str): New status text.
        """

        if not self.has_content() or not row_id:

            return

        list_item = self._execution_ui.running_scripts.item( row_id )
        values = list( list_item.get( 'values' ) )

        if len( values ) >= 3:

            values[ 1 ] = status
            self._execution_ui.running_scripts.item( row_id, values = values )

        if self._execution_ui.running_scripts.focus() == row_id:
            self._execution_ui.info_status.config( text = status )


    def update_ui( self, callback: Callable ) -> None:
        """ Schedule a UI update callback on the Tkinter main loop.

        Args:
            callback (Callable): UI update function to run on the main thread.
        """

        self._execution_ui.root.after( 0, callback )
