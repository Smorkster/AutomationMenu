"""
Control sequence-related UI behavior and interactions.

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
"""


from __future__ import annotations

import alwaysontop_tooltip

from typing import TYPE_CHECKING
from logging import Logger
from tkinter import Event
from tkinter.ttk import Combobox, Frame, Label, Treeview
from types import FunctionType
from typing import Any, Callable, Literal, Tuple, cast

from automation_menu.models.scriptinfo_not_loaded import ScriptInfoNotLoaded

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.services.sequence_manager import SequenceManager

from automation_menu.models.presetparam import PreSetParam
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.scriptinputparameter import ScriptInputParameter
from automation_menu.models.sequence import Sequence
from automation_menu.models.sequencestep import SequenceStep
from automation_menu.ui.controllers.execution_ui_controller import ExecutionUiController
from automation_menu.ui.types.sequence_ui import SequenceUi
from automation_menu.utils.decorators import ui_guard_method


class SequenceUiController:
    """ Control sequence UI interactions for editing, displaying, and running sequences."""

    def __init__( self, app_context: ApplicationContext, sequence_manager: SequenceManager, execution_ui_controller: ExecutionUiController, debugger: Logger, get_script_callback: Callable ) -> None:
        """ Initialize the sequence UI controller.

        Args:
            app_context (ApplicationContext): Shared application context.
            sequence_manager (SequenceManager): Manager handling sequence data and operations.
            execution_ui_controller (ExecutionUiController): Controller handling execution-related UI state.
            debugger (Logger): Logger used for warnings and debug output.
            get_script_callback (Callable): Callback used to retrieve script information by name.
        """

        self.app_context:ApplicationContext = app_context
        self._sequence_manager: SequenceManager = sequence_manager
        self._execution_ui: ExecutionUiController = execution_ui_controller
        self._debugger: Logger = debugger
        self._get_script_callback: Callable = get_script_callback
        self._sequence_ui: SequenceUi

        self._blink_job: str = ''
        self._blink_state: bool = False
        self._blink_active: bool = False

        self._in_edit_mode: bool = False


    def _on_mouseover_frame_step_enter( self, event: Event ) -> None:
        """ Eventhandler for mouse hover over step frame

        Args:
            event (Event): Event triggering this handler
        """

        if self._in_edit_mode:
            cast( Frame, event.widget ).configure( style = 'StepHoverInEdit.TFrame' )

        else:
            cast( Frame, event.widget ).configure( style = 'StepHover.TFrame' )


    def _on_mouseover_frame_step_leave( self, event: Event ) -> None:
        """ Eventhandler for mouse hover leaving step frame

        Args:
            event (Event): Event triggering this handler
        """

        cast( Frame, event.widget ).configure( style = 'Step.TFrame' )


    def _start_blinking( self ) -> None:
        """ Start or continue blinking the save-sequence button."""

        self._blink_active = True
        self._blink_state = not self._blink_state

        blinking_style: str = 'BlinkBg.TButton' if self._blink_state else 'TButton'
        self._sequence_ui.save_sequence_btn.after( 100, lambda: self._sequence_ui.save_sequence_btn.config( style = blinking_style ) )

        self._blink_job = self._sequence_ui.save_sequence_btn.after( 600, self._start_blinking )


    def _stop_blinking( self ) -> None:
        """ Stop save-sequence button blinking and restore its default style."""

        self._blink_active = False

        if self._blink_job:
            self._sequence_ui.save_sequence_btn.after_cancel( self._blink_job )
            self._blink_job = ''
            self._sequence_ui.save_sequence_btn.config( style = 'TButton' )


    @ui_guard_method( when_message = 'Call for aborting sequence editing' )
    def abort_sequence_edit( self, *args: Tuple ) -> None:
        """ Stop sequence editing and reset related UI state.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        self.clear_sequence_info()
        self.clear_sequence_steps()

        step_form: Frame = self._sequence_ui.step_form

        if step_form is not None and step_form.winfo_exists():
            step_form.grid_remove()

        sequence_ops: Frame = self._sequence_ui.sequence_ops

        if sequence_ops is not None and sequence_ops.winfo_exists():
            sequence_ops.grid_remove()

        self._sequence_ui.name_field.config( state = 'disable' )
        self._sequence_ui.description_field.config( state = 'disable' )
        self._sequence_ui.stop_sequence_on_error_field.config( state = 'disable' )

        self._stop_blinking()
        self._in_edit_mode = False


    @ui_guard_method( when_message = 'Call for aborting step editing' )
    def abort_add_sequence_step( self, *args: Tuple ) -> None:
        """ Hide the step form and end sequence step editing.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        self.hide_step_form()

        self._stop_blinking()


    @ui_guard_method( when_message = 'Call for displaying step form' )
    def add_sequence_step( self, *args: Tuple ) -> None:
        """ Toggle display of the sequence step form.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        self._sequence_manager.toggle_step_form()


    def bind_ui( self, sequence_ui: SequenceUi ) -> None:
        """ Bind sequence UI widget references to the controller.

        Args:
            sequence_ui (SequenceUi): Sequence UI widget collection.
        """

        self._sequence_ui = sequence_ui


    def clear_sequence_info( self ) -> None:
        """ Clear UI widgets containing the loaded sequence information."""

        self._sequence_ui.name_field.delete( 0, 'end' )
        self._sequence_ui.description_field.delete( 0, 'end' )
        self._sequence_ui.stop_sequence_on_error_var.set( False )


    def clear_sequence_steps( self ) -> None:
        """ Remove all displayed sequence step widgets from the UI."""

        for c in self._sequence_ui.steps_container.winfo_children():
            c.destroy()


    @ui_guard_method( when_message = 'Call for creating new sequence' )
    def create_new_sequence( self, *args: Tuple ) -> None:
        """ Create a new sequence for editing.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        self._sequence_manager.create_new_sequence()


    @ui_guard_method( when_message = 'Call for deleting sequence' )
    def delete_sequence( self, *args: Tuple ) -> None:
        """ Delete the currently selected sequence.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        self._sequence_manager.delete_sequence()

        self._stop_blinking()


    @ui_guard_method( when_message = 'Call for start editing sequence' )
    def edit_sequence( self, *args: Tuple ) -> None:
        """ Load the selected sequence for editing.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        self._in_edit_mode = True
        self._sequence_manager.edit_sequence()


    def get_selected_sequence_id( self ) -> str | None:
        """ Get the ID of the sequence selected in the UI list.

        Returns:
            (str | None): Selected sequence ID, or None if no valid sequence is selected.
        """

        values = self._sequence_ui.sequence_list.item( self._sequence_ui.sequence_list.focus() ).get( 'values', [] )

        if len( values ) < 2 or not isinstance( values[ 1 ], str ):

            return None

        return values[ 1 ]


    def hide_step_form( self ) -> None:
        """ Hide the sequence step editing form and clear its state."""

        self._sequence_ui.step_script_list.set( '' )
        self._sequence_ui.stop_step_on_error_var.set( False )

        step_form: Frame = self._sequence_ui.step_form

        if step_form is not None and step_form.winfo_exists():
            step_form.grid_remove()

        self._sequence_manager.current_step_for_edit = None


    def list_sequences( self ) -> None:
        """ Populate the UI list with available sequences.

        Args:
            main_self (AutomationMenuWindow): Main window object used to rebuild the sequence menu.
        """

        tree: Treeview = self._sequence_ui.sequence_list

        tree.delete( *tree.get_children() )

        for k in self._sequence_manager._sequences.items():
            tree.insert( '', 'end', values = ( k[ 1 ].name, k[ 0 ] ) )

        self._execution_ui.main_window.menu_buttons.sequence_menu.rebuild_menu( exec_list = self._sequence_manager._sequences )


    def on_listbox_click( self, event: Event ) -> None:
        """ Handle clicks in the sequence list and enable sequence actions when valid.

        Args:
            event (Event): Event that triggered the handler.
        """

        if not isinstance( event.widget, Treeview ):

            return

        sequence_listbox: Treeview = event.widget

        if event.widget.identify_element( event.x, event.y ) == '':

            event.widget.selection_remove( *event.widget.selection() )
            self._sequence_ui.edit_sequence_btn.config( state = 'disabled' )
            self._sequence_ui.run_sequence_btn.config( state = 'disabled' )

        elif item_focused := sequence_listbox.focus():
            values: list[ Any ] | Literal[ '' ] = sequence_listbox.item( item_focused ).get( 'values', [] )

            if len( values ) < 2:
                from automation_menu.utils.localization import _

                self._debugger.warning( _( 'Sequence list item missing id: {item}' ).format( item = values ) )

                return

            self._sequence_ui.edit_sequence_btn.config( state = 'normal' )
            self._sequence_ui.run_sequence_btn.config( state = 'normal' )

            if not self._in_edit_mode:
                self.populate_sequence_steps( sequence = self._sequence_manager.get_sequence( list_id = values[ 1 ] ) )

        return


    def on_info_checkbutton_changed( self ) -> None:
        """ Mark the current sequence as having unsaved changes.

        Args:
            event (Event): UI event triggered by editing a sequence field.
        """

        if not self._blink_active:
            self._start_blinking()


    def on_info_entry_changed( self, event: Event ) -> None:
        """ Mark the current sequence as having unsaved changes.

        Args:
            event (Event): UI event triggered by editing a sequence field.
        """

        if not self._blink_active:
            self._start_blinking()


    def on_step_click( self, step: SequenceStep ) -> None:
        """ Handle clicks on a sequence step row.

        Args:
            step (SequenceStep): Sequence step that was clicked.
        """

        if not self._in_edit_mode:

            return

        if not self._sequence_manager.get_current_sequence() or not step:
            from automation_menu.utils.localization import _

            self._debugger.warning( _( 'Invalid step at index {i}' ).format( i = step.step_index ) )

            return

        self._sequence_manager.start_new_step_edit( step )
        self.show_step_form()


    def on_step_script_selected( self, event: Event ) -> None:
        """ Handle selection of a script for a sequence step.

        Args:
            event (Event): Event that triggered the handler.

        Raises:
            ValueError: If the current step being edited is missing.
        """

        from automation_menu.utils.localization import _

        step_input_frame: Frame | None = self._sequence_ui.step_input_frame

        if step_input_frame is not None and step_input_frame.winfo_exists():
            for c in step_input_frame.winfo_children():
                c.destroy()

        selected_name: str = cast( Combobox, event.widget ).get()
        selected_script: ScriptInfo = self._get_script_callback( selected_name )

        if self._sequence_manager.current_step_for_edit is None:

            raise ValueError( _( '\'Current step\' was lost, can\'t load step' ) )

        self._sequence_manager.current_step_for_edit.script_file = selected_script.fullpath
        self._sequence_manager.current_step_for_edit.script_info = selected_script

        if len( selected_script.scriptmeta.script_input_parameters ) > 0:
            self.show_step_form_input( input = selected_script.scriptmeta.script_input_parameters )

        else:
            self.show_step_form_input( show = False )


    def populate_sequence_form( self, sequence: Sequence ) -> None:
        """ Populate sequence info widgets from a sequence.

        Args:
            sequence (Sequence): Sequence to load into the form.
        """

        self._sequence_ui.sequence_ops.grid()

        self._sequence_ui.name_field.config( state = 'normal' )
        self._sequence_ui.name_field.delete( 0, 'end' )
        self._sequence_ui.name_field.insert( 0, sequence.name )

        self._sequence_ui.description_field.config( state = 'normal' )
        self._sequence_ui.description_field.delete( 0, 'end' )
        self._sequence_ui.description_field.insert( 0, sequence.description )

        self._sequence_ui.stop_sequence_on_error_field.config( state = 'normal' )
        self._sequence_ui.stop_sequence_on_error_var.set( sequence.stop_on_error )

        self.populate_sequence_steps( sequence )


    def populate_sequence_steps( self, sequence: Sequence ) -> None:
        """ Create and display widgets for each step in a sequence.

        Args:
            sequence (Sequence): Sequence whose steps should be displayed.
        """

        from automation_menu.utils.localization import _

        self.clear_sequence_steps()

        for step in sequence.steps:
            self._sequence_ui.steps_container.grid_rowconfigure( index = step.step_index, weight = 0 )
            step_frame: Frame = Frame( master = self._sequence_ui.steps_container,
                                      borderwidth = 2,
                                      relief = 'solid',
                                      style = 'Step.TFrame',
                                      padding = ( 10, 2 ) )
            step_frame.grid( column = 0,
                            row = step.step_index,
                            sticky = 'we' )
            step_frame.grid_columnconfigure( index = 0, weight = 1 )

            step_label: Label = Label( master = step_frame,
                                      padding = ( 3, 2 ),
                                      text = f'{ step.step_index } :: { step.script_file }' )
            step_label.grid( sticky = 'we' )

            tooltip_text: str = ''

            if isinstance( step.script_info, ScriptInfoNotLoaded ):
                step_label.config( style = 'StepNotLoaded.TLabel',
                                  foreground = "#868686" )
                tooltip_text = step.script_info.scriptmeta.description

            else:
                lambda_bind: FunctionType = lambda e, i = step: self.on_step_click( step = i )
                step_label.config( style = 'Step.TLabel' )

                step_frame.bind( '<Button-1>', lambda_bind )
                step_label.bind( '<Button-1>', lambda_bind )
                step_frame.bind( '<Enter>', self._on_mouseover_frame_step_enter )
                step_frame.bind( '<Leave>', self._on_mouseover_frame_step_leave )

                if step.pre_set_parameters:
                    tooltip_text = _( 'Predefined input:\n' )
                    tooltip_text += '\n'.join( [ f'--{ p.name } { p.set }' for p in step.pre_set_parameters ] )

                else:
                    tooltip_text = _( 'Input not specified' )

            alwaysontop_tooltip.alwaysontop_tooltip.AlwaysOnTopToolTip( widget = step_label, msg = tooltip_text )


    @ui_guard_method( when_message = 'Call for deleting sequence step' )
    def remove_sequence_step( self, *args: Tuple ) -> None:
        """ Remove the currently edited step from the sequence.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        self._sequence_manager.remove_sequence_step()

        if not self._blink_active:
            self._start_blinking()


    @ui_guard_method( when_message = 'Call for running sequence' )
    def run_sequence( self, *args: Tuple, sequence_id: str | None = None ) -> None:
        """ Run a sequence and apply execution UI state changes.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
            sequence_id (str | None): ID of the sequence to run. If not provided, the selected sequence is used.
        """

        self._execution_ui.execution_pre_work( disable_minimize = False, is_sequence = True )

        on_finished_lambda: FunctionType = lambda: self._execution_ui.execution_post_work( disable_minimize = False,
                                                                            is_sequence = True )
        self._sequence_manager.run_sequence( sequence_id = sequence_id,
                                            on_finished = on_finished_lambda )


    @ui_guard_method( when_message = 'Call for saving sequence' )
    def save_current_step( self, *args: Tuple ) -> None:
        """ Save the currently edited sequence step.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        self._sequence_manager.save_edited_step( selected_script_name = self._sequence_ui.step_script_list.get(),
                                                selected_stop_on_error = self._sequence_ui.stop_step_on_error_var.get(),
                                                step_input_frame = self._sequence_ui.input_params_frame )

        if not self._blink_active:
            self._start_blinking()


    @ui_guard_method( when_message = 'Call for saving sequence' )
    def save_sequence( self, *args: Tuple ) -> None:
        """ Save the current sequence.

        Args:
            args (Tuple): Unused positional arguments accepted by the callback.
        """

        self._sequence_manager.save_sequence()
        self._stop_blinking()


    def show_step_form( self ) -> None:
        """ Display the form used to add or edit a sequence step."""

        self._sequence_ui.step_form.grid()

        step_input_frame: Frame | None = self._sequence_ui.step_input_frame

        if step_input_frame is not None and step_input_frame.winfo_exists():
            for c in step_input_frame.winfo_children():
                c.destroy()

        if self._sequence_manager.current_step_for_edit:
            script_info = self._sequence_manager.current_step_for_edit.script_info
            self._sequence_ui.step_script_list.set( script_info.filename )
            self._sequence_ui.stop_step_on_error_var.set( self._sequence_manager.current_step_for_edit.stop_on_error )

            if len( script_info.scriptmeta.script_input_parameters ) > 0:
                self.show_step_form_input( input = script_info.scriptmeta.script_input_parameters,
                                          pre_set = self._sequence_manager.current_step_for_edit.pre_set_parameters )

            else:
                self.show_step_form_input( show = False )

        else:
            self._sequence_manager.current_step_for_edit = SequenceStep()
            self._sequence_ui.step_script_list.set( '' )
            self._sequence_ui.stop_step_on_error_var.set( False )

            self.show_step_form_input()


    def show_step_form_input( self, input: list[ ScriptInputParameter ] = [], pre_set: list[ PreSetParam ] = [], show: bool = True ) -> None:
        """ Show or hide step input widgets depending on the selected script.

        Args:
            input (list[ScriptInputParameter]): Input parameters to display.
            pre_set (list[PreSetParam]): Pre-set parameter values to populate.
            show (bool): Whether the input frame should be shown.
        """

        ipf: Frame | None = self._sequence_ui.input_params_frame

        if show:
            self._sequence_ui.step_input_title.grid()
            self._sequence_ui.step_input_container.grid()

            if ipf is not None and ipf.winfo_exists():
                ipf.grid()

            if input:
                input_params_frame = self.app_context.InputManager.show_for_step( parameters = input,
                                                                                 container = self._sequence_ui.step_input_frame,
                                                                                 pre_set_parameters = pre_set,
                                                                                 canvas = self._sequence_ui.step_form_container_canvas )
                input_params_frame.grid()
                self._sequence_ui.input_params_frame = input_params_frame

        else:
            self._sequence_ui.step_input_title.grid_remove()
            self._sequence_ui.step_input_container.grid_remove()

            if ipf is not None and ipf.winfo_exists():
                ipf.grid_remove()
