"""
Manager class for displaying and managing automatic
run sequences

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""

from __future__ import annotations

import threading
import uuid

from tkinter.ttk import Frame, Notebook
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.models.application_state import ApplicationState

from automation_menu.models.enums import OutputStyleTags, SysInstructions
from automation_menu.models.presetparam import PreSetParam
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.sequence import Sequence
from automation_menu.models.sequencestep import SequenceStep
from automation_menu.services.sequence_runner import sequence_runner
from automation_menu.ui.components.script_input_form import collect_entered_input
from automation_menu.ui.controllers.sequence_ui_controller import SequenceUiController
from automation_menu.ui.tabs.sequence_tab import build_tab_content, create_sequence_tab, create_step_form
from automation_menu.ui.types.sequence_ui import SequenceUi


class SequenceManager:
    """ Manage saved sequences for editing, persistence, and execution."""

    def __init__( self, app_state: 'ApplicationState', app_context: 'ApplicationContext', saved_sequences: list[ dict ] ) -> None:
        """ Initialize the sequence manager.

        Args:
            app_state ('ApplicationState'): State container for the application.
            app_context ('ApplicationContext'): Context and manager container for the application.
            saved_sequences (list[dict]): Saved sequence data to load.
        """

        from automation_menu.utils.localization import _

        self._app_state: ApplicationState = app_state
        self._app_context: ApplicationContext = app_context

        normalized_sequences: list[ Sequence ] = []

        for item in saved_sequences or []:
            if isinstance( item, Sequence ):
                normalized_sequences.append( item )

            elif isinstance( item, dict ):
                normalized_sequences.append( Sequence().from_dict( data = item ) )

            else:
                app_context.OutputQueue.put( {
                            "line": _( 'Unsupported saved sequence format, type: {t}' ).format( t = type( item ) ),
                            "tag": OutputStyleTags.SYSINFO,
                            "exec_item": None
                        } )

        self.current_sequence: Sequence | None = None
        self.current_step_for_edit: SequenceStep | None = None
        self._sequences: dict[ str, Sequence ] = {}
        self._sequence_widgets: SequenceUi
        self.sequence_callbacks: dict = {}
        self.sequence_ui_controller: SequenceUiController

        for s in sorted( normalized_sequences, key = lambda x: x.name.lower() ):
            for step in s.steps:
                step.script_info = self._app_context.ScriptManager.get_script_info_by_path( path = step.script_file )

            self._sequences[ s.id ] = s


    def _add_callbacks( self ) -> None:
        """ Register sequence-related callbacks used by the UI controller."""

        # In controller
        self.sequence_callbacks[ '_clear_sequence_info' ] = self.sequence_ui_controller.clear_sequence_info
        self.sequence_callbacks[ '_clear_sequence_steps' ] = self.sequence_ui_controller.clear_sequence_steps
        self.sequence_callbacks[ '_get_selected_sequence_id' ] = self.sequence_ui_controller.get_selected_sequence_id
        self.sequence_callbacks[ 'on_listbox_click' ] = self.sequence_ui_controller.on_listbox_click
        self.sequence_callbacks[ '_on_step_click' ] = self.sequence_ui_controller.on_step_click
        self.sequence_callbacks[ '_on_step_script_selected' ] = self.sequence_ui_controller.on_step_script_selected
        self.sequence_callbacks[ '_populate_sequence_form' ] = self.sequence_ui_controller.populate_sequence_form
        self.sequence_callbacks[ '_populate_sequence_steps' ] = self.sequence_ui_controller.populate_sequence_steps
        self.sequence_callbacks[ 'create_new_sequence' ] = self.sequence_ui_controller.create_new_sequence
        self.sequence_callbacks[ 'edit_sequence' ] = self.sequence_ui_controller.edit_sequence
        self.sequence_callbacks[ 'run_sequence' ] = self.sequence_ui_controller.run_sequence
        self.sequence_callbacks[ 'add_sequence_step' ] = self.sequence_ui_controller.add_sequence_step
        self.sequence_callbacks[ 'save_sequence' ] = self.sequence_ui_controller.save_sequence
        self.sequence_callbacks[ 'delete_sequence' ] = self.sequence_ui_controller.delete_sequence
        self.sequence_callbacks[ 'abort_sequence_edit' ] = self.sequence_ui_controller.abort_sequence_edit
        self.sequence_callbacks[ 'remove_sequence_step' ] = self.sequence_ui_controller.remove_sequence_step
        self.sequence_callbacks[ 'abort_add_sequence_step' ] = self.sequence_ui_controller.abort_add_sequence_step

        # Inhouse
        self.sequence_callbacks[ 'list_sequences' ] = self.sequence_ui_controller.list_sequences
        self.sequence_callbacks[ 'main_self' ] = self._app_context.main_window
        self.sequence_callbacks[ '_show_step_form' ] = self.sequence_ui_controller.show_step_form
        self.sequence_callbacks[ '_show_step_form_input' ] = self.sequence_ui_controller.show_step_form_input
        self.sequence_callbacks[ '_save_edited_step' ] = self.sequence_ui_controller.save_current_step

        self.sequence_callbacks[ 'get_script_list' ] = self._app_context.ScriptManager.get_script_list


    def _persist_sequences( self ) -> None:
        """ Transform sequence data to dictionaries and save them to settings."""

        from automation_menu.utils.localization import _

        sequences_dict_list: list[ dict ] = []

        for s in self._sequences.values():

            jsoned_sequence: dict = s.to_dict()
            sequences_dict_list.append( jsoned_sequence )

        self._app_state.settings.saved_sequences = sequences_dict_list


    def _recalculate_step_indexes( self ) -> None:
        """ Recalculate the list index for each step in the current sequence."""

        if self.current_sequence is None:

            return

        for step in [ ( i, s ) for i, s in enumerate( self.current_sequence.steps ) ]:
            step[ 1 ].step_index = step[ 0 ]


    def save_edited_step( self, selected_script_name: str, selected_stop_on_error: bool, step_input_frame: Frame | None ) -> None:
        """ Save the currently edited sequence step.

        Args:
            selected_script_name (str): Name of the script selected for the step.
            selected_stop_on_error (bool): Whether sequence execution should stop if this step fails.
            step_input_frame (Frame | None): Frame containing preset input widgets for the step.
        """

        if self.current_sequence is None:

            return

        if not self.current_step_for_edit:
            self.current_step_for_edit = SequenceStep()
            self.current_sequence.steps.append( self.current_step_for_edit )
            self.current_step_for_edit.step_index = self.current_sequence.steps.index( self.current_step_for_edit )

        selected_script: ScriptInfo = self._app_context.ScriptManager.get_script_info_by_filename( filename = selected_script_name )
        self.current_step_for_edit.script_file = selected_script.fullpath
        self.current_step_for_edit.script_info = selected_script
        self.current_step_for_edit.stop_on_error = selected_stop_on_error

        index: int | None = next(
            (
                i for i, step in enumerate( self.current_sequence.steps )
                if step.id == self.current_step_for_edit.id
            ),
            None
        )

        if index is None:
            self.current_sequence.steps.append( self.current_step_for_edit )
            index = len( self.current_sequence.steps ) - 1

        else:
            self.current_sequence.steps[ index ] = self.current_step_for_edit

        self.current_step_for_edit.step_index = index

        if step_input_frame and step_input_frame.winfo_exists():
            step_input: list[ PreSetParam ] = collect_entered_input( frame_to_search = step_input_frame )
            self.current_step_for_edit.pre_set_parameters = step_input

        self.sequence_ui_controller.hide_step_form()
        self.sequence_ui_controller.populate_sequence_steps( sequence = self.current_sequence )
        self._persist_sequences()


    def abort_sequence_edit( self ) -> None:
        """ Clear sequence edit state and stop the current edit session."""

        self.current_sequence = None
        self.current_step_for_edit = None

        self.sequence_ui_controller.abort_sequence_edit()


    def build_tab_content( self ) -> None:
        """ Create the widgets used to display sequence tab content."""

        build_tab_content( ui = self._sequence_widgets, add_translatable = self._app_context.LanguageManager.add_translatable_widget, op_callbacks = self.sequence_callbacks )


    def create_new_sequence( self ) -> None:
        """ Create and load a new empty sequence for editing."""

        new_id: str = str( uuid.uuid4() )
        self.current_sequence = Sequence( id = new_id, description = '', name = '', stop_on_error = False, steps = [] )
        self._sequences[ new_id ] = self.current_sequence

        self.sequence_ui_controller.populate_sequence_form( self.current_sequence )


    def create_tab( self, parent_tab: Notebook ) -> Frame:
        """ Create the sequence tab UI and bind it to the controller.

        Args:
            parent_tab (Notebook): Notebook widget to attach the sequence tab to.

        Returns:
            (Frame): Frame containing the sequence UI.
        """

        self._add_callbacks()

        self._sequence_widgets = create_sequence_tab( tabcontrol = parent_tab, translate_callback = self._app_context.LanguageManager.add_translatable_widget )
        self.sequence_ui_controller.bind_ui( sequence_ui = self._sequence_widgets )

        return self._sequence_widgets.main_frame


    def delete_sequence( self ) -> None:
        """ Delete the currently edited sequence.

        Raises:
            ValueError: If the current sequence is missing.
        """

        from automation_menu.utils.localization import _

        if self.current_sequence is None:

            raise ValueError( _( '\'Current sequence\' was lost, can\'t remove sequence' ) )

        sequence_id: str = self.current_sequence.id

        del self._sequences[ sequence_id ]

        self.abort_sequence_edit()
        self._persist_sequences()
        self.sequence_ui_controller.list_sequences( main_self = self._app_context.main_window )


    def edit_sequence( self ) -> None:
        """ Load the selected sequence into the edit form."""

        id: str | None = self.sequence_ui_controller.get_selected_sequence_id()

        if id is None:

            return

        self.current_sequence = Sequence().from_sequence( seq =  self._sequences[ id ] )

        self.sequence_ui_controller.populate_sequence_form( sequence = self.current_sequence )


    def get_current_sequence( self ) -> Sequence:
        """ Get the currently selected sequence.

        Returns:
            (Sequence): Currently selected sequence.

        Raises:
            ValueError: If no sequence is currently selected.
        """

        if self.current_sequence is None:

            from automation_menu.utils.localization import _

            raise ValueError( _( 'No sequence is selected' ) )

        return self.current_sequence


    def get_sequence_list( self ) -> dict[ str, Sequence ]:
        """ Get the saved sequence mapping.

        Returns:
            (dict[str, Sequence]): Saved sequences keyed by sequence ID.
        """

        return self._sequences


    def get_sequence_name_list( self ) -> list[ str ]:
        """ Get a sorted list of saved sequence names.

        Returns:
            list (list[str]): Sorted names of available sequences.
        """

        list: list[ str ] = []

        for i, s in [ ( i , s ) for i, s in self._sequences.items() ]:
            list.append( s.name )

        return sorted( list )


    def load_step_for_edit( self, step_id: str ) -> None:
        """ Load a sequence step into the current edit state.

        Args:
            step_id (str): ID of the step to load for editing.
        """

        if self.current_sequence is None:

            return

        step: SequenceStep | None = next(
            ( s for s in self.current_sequence.steps if s.id == step_id ),
            None
        )
        self.current_step_for_edit = step


    def remove_sequence_step( self ) -> None:
        """ Remove the currently edited step from the current sequence.

        Raises:
            ValueError: If the current sequence or current step is missing.
        """

        from automation_menu.utils.localization import _

        if self.current_sequence is None:

            raise ValueError( _( '\'Current sequence\' was lost, can\'t remove step' ) )

        if self.current_step_for_edit is None:

            raise ValueError( _( '\'Current step\' was lost, can\'t remove step' ) )

        to_remove_index: int | None = next( ( i for i, step in enumerate( self.current_sequence.steps ) if step.id == self.current_step_for_edit.id ), None )

        if to_remove_index is not None:
            to_remove: SequenceStep = self.current_sequence.steps[ to_remove_index ]
            self.current_sequence.steps.remove( to_remove )
            self._recalculate_step_indexes()
            self.sequence_ui_controller.populate_sequence_steps( sequence = self.current_sequence )
            self.sequence_ui_controller.hide_step_form()

            self._persist_sequences()


    def run_sequence( self, on_finished: Callable[ [], None] | None = None, sequence_id: str | None = None ) -> None:
        """ Run a sequence asynchronously.

        Args:
            on_finished (Callable[[], None] | None): Callback to run after sequence execution finishes.
            sequence_id (str | None): ID of the sequence to run. If not provided, the selected sequence is used.
        """

        from automation_menu.utils.localization import _

        # Use the sequence selected in list
        sid = sequence_id if sequence_id is not None else self.sequence_ui_controller.get_selected_sequence_id()

        if sid is None:

            return

        main_window = self._app_context.main_window

        if main_window is None:

            return

        seq: Sequence = self._sequences[ sid ]
        finished_callback = on_finished or ( lambda: None )

        self._app_context.OutputQueue.put( SysInstructions.CLEAROUTPUT )
        self._app_context.OutputQueue.put( {
            'line': _( 'Starting sequence ''{name}'', with {step_count} steps' ).format( name = seq.name, step_count = len( seq.steps ) ),
            'tag': OutputStyleTags.SYSINFO,
            'exec_item': None
        } )

        def _mini_runner() -> None:
            """ Run the selected sequence in a background worker thread."""

            try:
                sequence_runner( sequence = seq,
                                execution_mgr = self._app_context.ExecutionManager,
                                output_queue = self._app_context.OutputQueue,
                                root = self._app_context.main_window.root,
                                api_callbacks = self._app_context.main_window.api_callbacks,
                                enable_stop = self._app_context.main_window.enable_stop_script_button,
                                enable_pause = self._app_context.main_window.enable_pause_script_button,
                                stop_pause = self._app_context.main_window.execution_controller.stop_pause_button_blinking
                                )

            finally:
                main_window.root.after( 0, finished_callback )

        threading.Thread( target = _mini_runner, daemon = True ).start()


    def save_sequence( self ) -> None:
        """ Save the current sequence data and persist it.

        Raises:
            ValueError: If the current sequence is missing.
        """

        from automation_menu.utils.localization import _

        if self.current_sequence is None:

            raise ValueError( _( '\'Current sequence\' was lost, can\'t save data' ) )

        self.current_sequence.name = self._sequence_widgets.name_field.get()
        self.current_sequence.description = self._sequence_widgets.description_field.get()
        self.current_sequence.stop_on_error = self._sequence_widgets.stop_sequence_on_error_var.get()

        self._sequences[ self.current_sequence.id ] = self.current_sequence
        self._persist_sequences()
        self.sequence_ui_controller.list_sequences( main_self = self._app_context.main_window )


    def start_new_step_edit( self, step: SequenceStep ) -> None:
        """ Start editing a copy of the provided sequence step.

        Args:
            step (SequenceStep): Step to copy into the current edit state.
        """

        self.current_step_for_edit = SequenceStep().from_step( step = step )


    def toggle_step_form( self ) -> None:
        """ Show or hide the step editing form."""

        if self._sequence_widgets.step_form.winfo_ismapped():
            self.sequence_ui_controller.hide_step_form()

        else:
            step_form: Frame | None = self._sequence_widgets.step_form

            if step_form is None or not step_form.winfo_exists():
                create_step_form( ui = self._sequence_widgets, add_translatable = self._app_context.LanguageManager.add_translatable_widget, op_callbacks = self.sequence_callbacks )
                step_form = self._sequence_widgets.step_form

            self.sequence_ui_controller.show_step_form()
