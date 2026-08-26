"""
Manage persistent GUI script sessions and their tab-level UI.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from __future__ import annotations

from tkinter.ttk import Frame, Notebook
from typing import TYPE_CHECKING, Callable
import uuid

from automation_menu.models.enums import ExecutionState
from automation_menu.models.persistent_execution_session import PersistentExecutionSession
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.types.persistent_manager_callbacks import PersistentManagerCallbacks
from automation_menu.utils.localization import translate

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.models.application_state import ApplicationState

from automation_menu.types.persistent_ui_callbacks import PersistentUiCallbacks
from automation_menu.ui.controllers.persistent_ui_controller import PersistentUiController
from automation_menu.ui.tabs.persistent_gui_tab import build_tab_content, create_persistent_tab
from automation_menu.ui.types.persistent_ui import PersistentUi


class PersistentGuiManager:
    """ Coordinate persistent script sessions with the persistent UI tab. """

    def __init__( self, app_state: ApplicationState, app_context: ApplicationContext ) -> None:
        """ Store shared state and initialize persistent UI management.

        Args:
            app_state (ApplicationState): Shared application state container.
            app_context (ApplicationContext): Shared application context and service
                registry.
        """

        self._app_state: ApplicationState = app_state
        self._app_context: ApplicationContext = app_context
        self._ui: PersistentUi
        self._ui_controller: PersistentUiController = PersistentUiController()

        self._translate_store_callback = self._app_context.LanguageManager.add_translatable_widget
        self._persistent_ui_callbacks: PersistentUiCallbacks

        self._running_scripts: dict[ str, PersistentExecutionSession ] = {}

        self._tab_content_built: bool = False


    def _add_callbacks( self ) -> None:
        """ Create callback containers shared between manager and controller. """

        self._persistent_ui_callbacks = PersistentUiCallbacks( treeview_click = self._ui_controller.treeview_click,
                                                              treeview_item_selected = self._ui_controller.treeview_item_selected,
                                                              pause_script = self._ui_controller.pause_script,
                                                              resume_script = self._ui_controller.resume_script,
                                                              show_script = self._ui_controller.show_script,
                                                              stop_script = self._ui_controller.stop_script,
                                                              force_stop_script = self._ui_controller.force_stop_script,
                                                              update_error = self._ui_controller.update_error,
                                                              update_output = self._ui_controller.update_output,
                                                              update_progress = self._ui_controller.update_progress,
                                                              update_state = self._ui_controller.update_state,
                                                              update_status = self._ui_controller.update_status,
                                                              update_ui = self._ui_controller.update_ui )

        self._manager_callbacks = PersistentManagerCallbacks( get_session_by_row_id = self.get_session_by_row_id )


    def _is_terminal_session( self, session: PersistentExecutionSession ) -> bool:
        """ Return whether a session has reached a terminal state.

        Args:
            session (PersistentExecutionSession): Session to inspect.

        Returns:
            (bool): True if the session is closed or stopped, otherwise False.
        """

        return session.state in { ExecutionState.CLOSED,
                                 ExecutionState.STOPPED, }


    def build_tab_content( self ) -> None:
        """ Build the persistent tab contents and repopulate running sessions. """

        build_tab_content( ui = self._ui, op_callbacks = self._persistent_ui_callbacks, translate_store_callback = self._translate_store_callback, translate_callback = translate )

        self._tab_content_built = True

        if len( self._running_scripts ) > 0:

            for k, v in self._running_scripts.items():
                self._ui_controller.add_session( v )

            self._ui_controller.select_list_item( list( self._running_scripts.values() )[ 0 ].row_id )


    def create_tab( self, parent_notebook: Notebook ) -> Frame:
        """ Create the ui for persistent GUI script display.

        Args:
            parent_notebook (Notebook): Parent widget to attach to

        Returns:
            (Frame): A frame to use as tab for persistent GUI scripts
        """

        self._ui = create_persistent_tab( tab_control = parent_notebook, translate_store_callback = self._translate_store_callback )
        self._ui.root = self._app_context.main_window.root
        self._add_callbacks()

        self._ui_controller.bind_ui( ui = self._ui,  manager_callbacks = self._manager_callbacks )


        return self._ui.main_frame


    def get_session_by_row_id( self, row_id: str ) -> PersistentExecutionSession:
        """ Return the tracked session matching a tree view row id.

        Args:
            row_id (str): Tree view row identifier.

        Returns:
            (PersistentExecutionSession): Matching persistent execution session.

        Raises:
            StopIteration: If no session matches the provided row id.
        """

        return next( session for key, session in self._running_scripts.items() if session.row_id == row_id )


    def is_tab_content_built( self ) -> bool:
        """ Return whether the persistent tab widgets have been built.

        Returns:
            (bool): True if the tab content has been created, otherwise False.
        """

        return self._tab_content_built


    def start_script( self, script_info: ScriptInfo, entered_input: list[ str ] ) -> None:
        """ Start a persistent script session or focus an existing active one.

        Args:
            script_info (ScriptInfo): Metadata for the script to run.
            entered_input (list[str]): Input arguments to pass to the script.
        """

        self._app_context.main_window.tab_control.select( 1 )

        if script_info.scriptmeta.persistent_gui:
            matching_sessions = [ session for session in self._running_scripts.values()
                                 if session.script_info.fullpath == script_info.fullpath ]

            active_sessions = [ session for session in matching_sessions
                               if not self._is_terminal_session( session ) ]

            if active_sessions:
                session_to_focus = active_sessions[-1 ]

                if self._tab_content_built and session_to_focus.row_id:
                    self._ui_controller.select_list_item( id = session_to_focus.row_id )
                    self._ui_controller.show_script()

                return


        session_id: str = str( uuid.uuid4() )

        new_session = PersistentExecutionSession( id = session_id,
                                                 script_info = script_info,
                                                 op_callbacks = self._persistent_ui_callbacks, )

        self._ui_controller.add_session( new_session )
        new_session.initiate_runner( entered_input = entered_input,
                                    python_exe_path = self._app_state.python_exe_path,
                                    run_state = self._app_state.run_state, )

        self._running_scripts[ session_id ] = new_session
        self._ui_controller.select_list_item( id = new_session.row_id )
