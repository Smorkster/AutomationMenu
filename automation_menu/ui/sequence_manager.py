"""
Manager class for displaying and managing automatic
run sequences

Author: Smorkster
GitHub: https://github.com/Smorkster/automationmenu
License: MIT
Version: 1.0.0
Created: 2025-11-20
"""

from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.models.application_state import ApplicationState
    from automation_menu.core.script_execution_manager import ScriptExecutionManager

import alwaysontop_tooltip
import threading

from tkinter import E, END, N, S, W, BooleanVar, Canvas, Event, Listbox, Scrollbar
from tkinter.ttk import Button, Checkbutton, Combobox, Entry, Frame, Label, Notebook
from typing import Callable

from automation_menu.core import script_execution_manager
from automation_menu.models.enums import OutputStyleTags, SysInstructions
from automation_menu.models.scriptinputparameter import ScriptInputParameter
from automation_menu.models.sequence import Sequence
from automation_menu.models.sequencestep import SequenceStep
from automation_menu.utils.build_run_args import build_run_args


class SequenceManager:
    def __init__( self, app_state: ApplicationState, app_context: ApplicationContext, saved_sequences: list[ Sequence ] ) -> None:
        """ Manage sequences for editing and orchestration

        Args:
            app_state (ApplicationState): State vault for application
            app_context (ApplicationContext): Context and manager vault for application
            saved_sequences (list[ Sequences ]): User saved sequences
        """

        self._app_state: ApplicationState = app_state
        self._app_context: ApplicationContext = app_context

        self._current_sequence: Sequence = None
        self._current_step_for_edit: SequenceStep = None
        self._parent: Notebook = None
        self._sequences: dict = {}
        self._sequence_widgets: dict = {}
        self._sequence_callbacks: dict = {}

        for s in sorted( saved_sequences, key = lambda x: x[ 'name' ] ):
            steps = [
                SequenceStep( **y )
                for y in sorted( s[ 'steps' ], key = lambda i: i[ 'step_index' ] )
            ]

            for step in steps:
                step.script_info = self._app_context.script_manager.get_script_info_by_path( path = step.script_file )

            sequence = Sequence(
                name = s[ 'name' ],
                description = s.get( 'description', '<Description not set>' ),
                steps = steps,
                stop_on_error = s.get( 'stop_on_error', False )
            )
            self._sequences[ s[ 'name' ] ] = sequence


    def _clear_sequence_info( self ) -> None:
        """ Clear widgets of loaded sequence info """

        self._sequence_widgets[ 'name_field' ].delete( 0, 'end' )
        self._sequence_widgets[ 'description_field' ].delete( 0, 'end' )
        self._sequence_widgets[ 'stop_sequence_on_error_var' ].set( False )


    def _clear_sequence_steps( self ) -> None:
        """ Delete widgets for all listed sequence steps """

        for c in self._sequence_widgets[ 'steps_container' ].winfo_children():
            c.destroy()


    def _create_sequence_list_op_buttons( self ) -> None:
        """ Define button to create or edit sequences """

        from automation_menu.utils.localization import _

        sequence_op_frame = Frame( master = self._sequence_widgets[ 'main_frame' ] )
        sequence_op_frame.grid( column = 0, row = 1, sticky = ( W, E ) )

        col = 0

        sequence_op_frame.grid_columnconfigure( index = col, weight = 0 )
        create_new_sequence = Button( master = sequence_op_frame, text = _( 'Create new sequence' ), command = self._sequence_callbacks[ 'op_create_new_sequence' ] )
        create_new_sequence.grid( column = col, row = 0, sticky = ( N, W ) )
        self._sequence_widgets[ 'new_sequence_btn' ] = create_new_sequence
        self._app_context.language_manager.add_translatable_widget( ( create_new_sequence, 'Create new sequence' ) )

        col += 1

        sequence_op_frame.grid_columnconfigure( index = col, weight = 0 )
        edit_sequence = Button( master = sequence_op_frame, text = _( 'Edit' ), command = self._sequence_callbacks[ 'op_edit_sequence' ], state = 'disable' )
        edit_sequence.grid( column = col, row = 0, sticky = ( N, W ) )
        self._sequence_widgets[ 'edit_sequence_btn' ] = edit_sequence
        self._app_context.language_manager.add_translatable_widget( ( edit_sequence, 'Edit' ) )

        col += 1

        sequence_op_frame.grid_columnconfigure( index = col, weight = 1 )

        col += 1

        sequence_op_frame.grid_columnconfigure( index = col, weight = 0 )
        run_sequence = Button( master = sequence_op_frame, text = _( 'Run selected' ), command = self._sequence_callbacks[ 'op_run_sequence' ], state = 'disable' )
        run_sequence.grid( column = col, row = 0, sticky = ( N, W ) )
        self._sequence_widgets[ 'run_sequence_btn' ] = run_sequence
        self._app_context.language_manager.add_translatable_widget( ( run_sequence, 'Run selected' ) )


    def _create_steps_display( self ) -> None:
        """ Create display frame to contain sequence steps """

        from automation_menu.utils.localization import _

        steps_display_frame: Frame = Frame( master = self._sequence_widgets[ 'main_frame' ] )
        steps_display_frame.grid( column = 1, row = 0, rowspan = 3, sticky = ( N, S, W, E ) )
        steps_display_frame.grid_columnconfigure( index = 0, weight = 1 )
        steps_display_frame.grid_columnconfigure( index = 1, weight = 0 )
        steps_display_frame.grid_rowconfigure( index = 0, weight = 0 )
        steps_display_frame.grid_rowconfigure( index = 1, weight = 1 )
        steps_display_frame.grid_rowconfigure( index = 2, weight = 0 )
        self._sequence_widgets[ 'steps_display_frame' ] = steps_display_frame

        steps_title: Label = Label( master = steps_display_frame, text = _( 'Steps in sequence' ), style = 'BiggerTitle.TLabel' )
        steps_title.grid( column = 0, row = 0, sticky = ( W ) )

        display_container: Frame = Frame( master = steps_display_frame )
        display_container.grid( column = 0, columnspan = 2, row = 1, sticky = ( N, S, W, E ) )
        display_container.grid_columnconfigure( index = 0, weight = 1 )
        display_container.grid_rowconfigure( index = 0, weight = 1 )
        self._sequence_widgets[ 'display_container' ] = display_container

        container_canvas: Canvas = Canvas( master = display_container, highlightthickness = 0 )
        container_canvas.grid( sticky = ( N, S, W, E ) )
        container_canvas.grid_columnconfigure( index = 0, weight = 1 )
        container_canvas.bind( '<Configure>', self._on_canvas_config )
        self._sequence_widgets[ 'container_canvas' ] = container_canvas
        container_canvas.bind_all( '<MouseWheel>' , self._on_mousewheel )

        container_scrollbar: Scrollbar = Scrollbar( master = display_container, orient = 'vertical', command = container_canvas.yview )
        container_scrollbar.grid( column = 1, row = 0, sticky = ( N, S ) )
        self._sequence_widgets[ 'container_scrollbar' ] = container_scrollbar

        container_canvas.configure( yscrollcommand = container_scrollbar.set )

        steps_container: Frame = Frame( master = container_canvas )
        steps_container.grid_columnconfigure( index = 0, weight = 1 )
        steps_container.grid_rowconfigure( index = 0, weight = 1 )
        steps_container.bind( '<Configure>', self._on_frame_config )
        self._sequence_widgets[ 'steps_container' ] = steps_container

        window_id = container_canvas.create_window( ( 0, 0 ), window = steps_container, anchor = 'nw' )
        self._sequence_widgets[ 'window_id' ] = window_id


    def _create_sequence_editing_op_buttons( self ) -> None:
        """ Create buttons for editing a sequence """

        from automation_menu.utils.localization import _

        sequence_ops: Frame = Frame( master = self._sequence_widgets[ 'sequence_form' ] )
        sequence_ops.grid( column = 0, columnspan = 2, row = 4, sticky = ( S, E ) )
        self._sequence_widgets[ 'sequence_ops' ] = sequence_ops

        col = 0

        sequence_ops.grid_columnconfigure( index = col, weight = 0 )
        add_step_button: Button = Button( master = sequence_ops, text = _( 'Add step' ) , command = self._sequence_callbacks[ 'op_add_sequence_step' ] )
        add_step_button.grid( column = col, row = 0 )
        self._sequence_widgets[ 'add_step_btn' ] = add_step_button
        self._app_context.language_manager.add_translatable_widget( ( add_step_button, 'Add step' ) )

        col += 1

        sequence_ops.grid_columnconfigure( index = col, weight = 0 )
        save_sequence: Button = Button( master = sequence_ops, text = _( 'Save sequence' ), command = self._sequence_callbacks[ 'op_save_sequence' ] )
        save_sequence.grid( column = col, row = 0 )
        self._sequence_widgets[ 'save_sequence_btn' ] = save_sequence
        self._app_context.language_manager.add_translatable_widget( ( save_sequence, 'Save sequence' ) )

        col += 1

        sequence_ops.grid_columnconfigure( index = col, weight = 0 )
        delete_sequence: Button = Button( master = sequence_ops, text = _( 'Delete sequence' ), command = self._sequence_callbacks[ 'op_delete_sequence' ] )
        delete_sequence.grid( column = col, row = 0, sticky = ( N, W ) )
        self._sequence_widgets[ 'delete_sequence_btn' ] = delete_sequence
        self._app_context.language_manager.add_translatable_widget( ( delete_sequence, 'Delete' ) )

        col += 1

        sequence_ops.grid_columnconfigure( index = col, weight = 0 )
        abort_sequence_edit: Button = Button( master = sequence_ops, text = _( 'Abort edit' ), command = self._sequence_callbacks[ 'op_abort_sequence_edit' ] )
        abort_sequence_edit.grid( column = col, row = 0, sticky = ( N, W ) )
        self._sequence_widgets[ 'abort_sequence_edit_btn' ] = abort_sequence_edit
        self._app_context.language_manager.add_translatable_widget( ( abort_sequence_edit, 'Abort edit' ) )

        sequence_ops.grid_remove()


    def _create_sequence_form( self ) -> None:
        """ Define a form for displaying sequence information """

        from automation_menu.utils.localization import _

        sequence_form = Frame( master = self._sequence_widgets[ 'main_frame' ] )
        sequence_form.grid( column = 0, row = 2, rowspan = 2, sticky = ( N, S, W, E ) )
        sequence_form.grid_columnconfigure( index = 0, weight = 0 )
        sequence_form.grid_columnconfigure( index = 1, weight = 1 )
        sequence_form.grid_columnconfigure( index = 2, weight = 0 )
        sequence_form.grid_rowconfigure( index = 0, weight = 0 ) # Name
        sequence_form.grid_rowconfigure( index = 1, weight = 0 ) # Description
        sequence_form.grid_rowconfigure( index = 2, weight = 0 ) # Stop on error
        sequence_form.grid_rowconfigure( index = 3, weight = 1 ) # Empty
        sequence_form.grid_rowconfigure( index = 4, weight = 1 ) # Sequence op buttons
        self._sequence_widgets[ 'sequence_form' ] = sequence_form

        row = 0

        name_title = Label( master = sequence_form, text = _( 'Name' ), style = 'History.TLabel' )
        name_title.grid( column = 0, row = row, sticky = ( W ) )

        name_field = Entry( master = sequence_form )
        name_field.grid( column = 1, columnspan = 2, row = row, sticky = ( W, E ) )
        self._sequence_widgets[ 'name_field' ] = name_field

        row += 1

        description_title = Label( master = sequence_form, text = _( 'Description' ), style = 'History.TLabel' )
        description_title.grid( column = 0, row = row, sticky = ( W ) )

        description_field = Entry( master = sequence_form )
        description_field.grid( column = 1, columnspan = 2, row = row, sticky = ( W, E ) )
        self._sequence_widgets[ 'description_field' ] = description_field

        row += 1

        stop_on_error_title = Label( master = sequence_form, text = _( 'Stop on error' ), style = 'History.TLabel' )
        stop_on_error_title.grid( column = 0, row = row, sticky = ( W ) )

        self._sequence_widgets[ 'stop_sequence_on_error_var' ] = BooleanVar( master = sequence_form, value = False )
        stop_on_error_field = Checkbutton( master = sequence_form, variable = self._sequence_widgets[ 'stop_sequence_on_error_var' ] )
        stop_on_error_field.grid( column = 1, columnspan = 2, row = row, sticky = ( W, E ) )
        self._sequence_widgets[ 'stop_sequence_on_error_field' ] = stop_on_error_field


    def _create_sequence_list( self ) -> None:
        """ Define a list to display available sequences """

        sequence_list = Listbox( master = self._sequence_widgets[ 'main_frame' ], width = 50, font = ( 'Calibri', 13 ), selectbackground = '#C5fAFF', selectforeground = '#000000', selectborderwidth = 2, activestyle = 'none' )
        sequence_list.bind( '<Button-1>', self._on_listbox_click )
        sequence_list.grid( column = 0, row = 0, sticky = ( N, S, W, E ) )
        self._sequence_widgets[ 'sequence_list' ] = sequence_list

        list_scrollbar = Scrollbar( master = self._sequence_widgets[ 'main_frame' ] )
        list_scrollbar.grid( column = 0, row = 0, sticky = ( N, S, E ) )

        sequence_list.config( yscrollcommand = list_scrollbar.set )

        list_scrollbar.config( command = sequence_list.yview )

        for k in self._sequences.keys():
            sequence_list.insert( 'end', k )


    def _create_step_form( self ) -> None:
        """ Create form for editing/creating a sequence step """

        from automation_menu.utils.localization import _

        step_form = Frame( master = self._sequence_widgets[ 'steps_display_frame' ], style = 'SequenceStep.TFrame', borderwidth = 2, relief = 'solid' )
        step_form.grid( column = 0, row = 2, rowspan = 3, sticky = ( N, S, W, E ) )
        step_form.grid_columnconfigure( index = 0, weight = 0 )
        step_form.grid_columnconfigure( index = 1, weight = 1 )
        self._sequence_widgets[ 'step_form' ] = step_form

        row = 0

        step_form.grid_rowconfigure( index = row, weight = 0 ) # Script title
        script_title = Label( master = step_form, text = _( 'Script for this step' ), style = 'History.TLabel' )
        script_title.grid( column = 0, row = row, sticky = ( N, W ) )

        script_names = sorted( [ s.filename for s in self._app_context.script_manager.get_script_list() ] )
        script_field = Combobox( master = step_form, values = script_names )
        script_field.bind( '<<ComboboxSelected>>', self._on_step_script_selected )
        script_field.grid( column = 1, row = row, padx = 5, sticky = ( N, W ) )
        self._sequence_widgets[ 'step_script_field' ] = script_field

        row += 1

        step_form.grid_rowconfigure( index = row, weight = 0 ) # Stop on error
        stop_on_error_title = Label( master = step_form, text = _( 'Stop on error' ), style = 'History.TLabel' )
        stop_on_error_title.grid( column = 0, row = row, sticky = ( W ) )

        self._sequence_widgets[ 'stop_step_on_error_var' ] = BooleanVar( master = step_form, value = False )
        stop_on_error_field = Checkbutton( master = step_form, variable = self._sequence_widgets[ 'stop_step_on_error_var' ] )
        stop_on_error_field.grid( column = 1, row = row, sticky = ( W ) )

        row += 1

        step_form.grid_rowconfigure( index = row, weight = 0 ) # Input title
        input_title = Label( master = step_form, text = _( 'Script input parameters' ), style = 'History.TLabel' )
        input_title.grid( column = 0, row = row, sticky = ( N, W ) )
        self._sequence_widgets[ 'step_input_title' ] = input_title

        row += 1

        step_form.grid_rowconfigure( index = row, weight = 0 ) # Input parameters
        input_frame = Frame( master = step_form )
        input_frame.grid( column = 0, columnspan = 3, row = row, sticky = ( N, S, W, E ) )
        self._sequence_widgets[ 'step_input_frame' ] = input_frame

        row += 1

        step_form.grid_rowconfigure( index = row, weight = 0 ) # Input parameters

        step_op_buttons_frame = Frame( master = step_form )
        step_op_buttons_frame.grid( column = 1, row = row, sticky = ( S, E ) )

        col = 0

        step_op_buttons_frame.grid_columnconfigure( index = col, weight = 0 )
        step_add = Button( master = step_op_buttons_frame, text = _( 'Save step' ), command = self._save_edited_step )
        step_add.grid( column = col, row = 0, sticky = ( E ) )

        col += 1

        step_op_buttons_frame.grid_columnconfigure( index = col, weight = 0 )
        step_remove = Button( master = step_op_buttons_frame, text = _( 'Remove step' ), command = self._sequence_callbacks[ 'op_remove_sequence_step' ] )
        step_remove.grid( column = col, row = 0, sticky = ( E ) )

        col += 1

        step_op_buttons_frame.grid_columnconfigure( index = col, weight = 0 )
        step_abort = Button( master = step_op_buttons_frame, text = _( 'Abort' ), command = self._sequence_callbacks[ 'op_abort_add_sequence_step' ] )
        step_abort.grid( column = col, row = 0, sticky = ( E ) )

        step_form.grid_remove()


    def _on_canvas_config( self, event: Event ) -> None:
        """ Eventhandler for when sequence step canvas changes size """

        self._sequence_widgets[ 'container_canvas' ].itemconfig( self._sequence_widgets[ 'window_id' ], width = event.width, height = event.height )


    def _on_frame_config( self, event: Event ) -> None:
        """ Eventhandler for when sequence step frame changes size """

        self._sequence_widgets[ 'container_canvas' ].configure( scrollregion = self._sequence_widgets[ 'container_canvas' ].bbox( 'all' ) )


    def _on_listbox_click( self, event: Event ) -> None:
        """ Verify if an item or empty area was clicked in the listbox

        Args:
            event (tk.Event): The event that called this handler
        """

        sequence_listbox: Listbox = event.widget
        index = sequence_listbox.nearest( event.y )
        bbox = sequence_listbox.bbox( index )

        if index >= sequence_listbox.size() or not bbox or not ( bbox[ 1 ] <= event.y <= bbox[ 1 ] + bbox[ 3 ] ):
            sequence_listbox.selection_clear( first = 0, last = END )

            self._sequence_widgets[ 'edit_sequence_btn' ].config( state = 'disable' )
            self._sequence_widgets[ 'run_sequence_btn' ].config( state = 'disable' )

            return 'break'

        self._sequence_widgets[ 'edit_sequence_btn' ].config( state = 'normal' )
        self._sequence_widgets[ 'run_sequence_btn' ].config( state = 'normal' )


    def _on_mousewheel( self, event: Event ) -> None:
        """ Eventhandler for mouse wheel scrolling in the steps list """

        self._sequence_widgets[ 'container_canvas' ].yview_scroll( int( -1 * ( event.delta / 120 ) ), 'units' )


    def _on_step_click( self, step_index: int ) -> None:
        """ Eventhandler for click on step row """

        self._current_step_for_edit = self._current_sequence.steps[ step_index ]
        self._show_step_form()


    def _on_step_script_selected( self, event: Event ) -> None:
        """ Eventhandler for when a script is selected for a sequence step """

        selected_name = event.widget.get()

        selected_script = self._app_context.script_manager.get_script_info_by_filename( selected_name )

        self._current_step_for_edit.script_file = selected_script.fullpath
        self._current_step_for_edit.script_info = selected_script

        if len( selected_script.scriptmeta.script_input_parameters ) > 0:
            self._show_step_form_input( input = selected_script.scriptmeta.script_input_parameters )


    def _persist_sequences( self ) -> None:
        """ Transform sequence data to dict and save to settings """

        sequences_list = []

        for s in self._sequences.values():
            sequences_list.append(
                {
                    'name': s.name,
                    'description': s.description,
                    'stop_on_error': s.stop_on_error,
                    'steps': [
                        {
                            'script_file': step.script_file,
                            'pre_set_parameters': step.pre_set_parameters,
                            'stop_on_error': step.stop_on_error,
                            'step_index': step.step_index,
                        }
                        for step in s.steps
                    ],
                }
            )

        self._app_state.settings.saved_sequences = sequences_list


    def _populate_sequence_form( self, sequence: Sequence ) -> None:
        """ Enter selected sequence data to info widgets

        Args:
            seguence (Sequence): Sequence to take information from
        """

        from automation_menu.utils.localization import _

        self._sequence_widgets[ 'sequence_ops' ].grid()

        self._sequence_widgets[ 'name_field' ].config( state = 'normal' )
        self._sequence_widgets[ 'name_field' ].delete( 0, 'end' )
        self._sequence_widgets[ 'name_field' ].insert( 0, sequence.name )

        self._sequence_widgets[ 'description_field' ].config( state = 'normal' )
        self._sequence_widgets[ 'description_field' ].delete( 0, 'end' )
        self._sequence_widgets[ 'description_field' ].insert( 0, sequence.description )

        self._sequence_widgets[ 'stop_sequence_on_error_field' ].config( state = 'normal' )
        self._sequence_widgets[ 'stop_sequence_on_error_var' ].set( sequence.stop_on_error )

        self._populate_sequence_steps( sequence )


    def _populate_sequence_steps( self, sequence: Sequence ) -> None:
        """ Create widgets per sequence step and populate display frame """

        from automation_menu.utils.localization import _

        self._clear_sequence_steps()

        for step in sequence.steps:
            lambda_bind = lambda e, i = sequence.steps.index( step ): self._on_step_click( i )

            self._sequence_widgets[ 'steps_container' ].grid_rowconfigure( index = step.step_index, weight = 0 )
            step_frame = Frame( master = self._sequence_widgets[ 'steps_container' ], borderwidth = 2, relief = 'solid', padding = 5 )
            step_frame.grid( column = 0, row = step.step_index, sticky = ( W, E ) )
            step_frame.bind( '<Button-1>', lambda_bind )

            step_label = Label( master = step_frame, text = f'{ step.step_index } :: { step.script_file }' )
            step_label.grid( sticky = ( W, E ) )
            step_label.bind( '<Button-1>', lambda_bind )

            tooltip_text = ""

            if step.pre_set_parameters:
                tooltip_text = '\n'.join( [ f'--{ p['name'] } { p['set'] }' for p in step.pre_set_parameters ] )

            else:
                tooltip_text = _( 'Input not specified' )

            alwaysontop_tooltip.alwaysontop_tooltip.AlwaysOnTopToolTip( widget = step_label, msg = tooltip_text )


    def _recalculate_step_indexes( self ) -> None:
        """ Sequence step list have changed, recalculate each steps list index """

        for step in [ ( i, s ) for i, s in enumerate( self._current_sequence.steps ) ]:
            step[ 1 ].step_index = step[ 0 ]


    def _save_edited_step( self ) -> None:
        """ Save the currently edited step """

        if not self._current_step_for_edit:
            self._current_step_for_edit = SequenceStep()
            self._current_sequence.steps.append( self._current_step_for_edit )
            self._current_step_for_edit.step_index = self._current_sequence.steps.index( self._current_step_for_edit )

        selected_script = self._app_context.script_manager.get_script_info_by_filename( filename = self._sequence_widgets[ 'step_script_field' ].get() )
        self._current_step_for_edit.script_file = selected_script.fullpath
        self._current_step_for_edit.script_info = selected_script
        self._current_step_for_edit.stop_on_error = self._sequence_widgets[ 'stop_step_on_error_var' ].get()

        try:
            self._current_step_for_edit.step_index = self._current_sequence.steps.index( self._current_step_for_edit )

        except:
            self._current_sequence.steps.append( self._current_step_for_edit )
            self._current_step_for_edit.step_index = self._current_sequence.steps.index( self._current_step_for_edit )

        if self._sequence_widgets.get( 'input_params_frame', False ):
            ipf = self._sequence_widgets[ 'input_params_frame' ]
            if ipf.winfo_exists():
                step_input = self._app_context.input_manager.collect_input_values(
                    frame_name_to_search = ipf
                )
                self._current_step_for_edit.pre_set_parameters = step_input

        self.hide_step_form()
        self._populate_sequence_steps( sequence = self._current_sequence )
        self._persist_sequences()


    def _show_step_form( self ) -> None:
        """ Display the form to edit/add sequence step """

        step_form = self._sequence_widgets.get( 'step_form' )

        if step_form is None or not step_form.winfo_exists():
            self._create_step_form()
            step_form = self._sequence_widgets[ 'step_form' ]

        self._sequence_widgets[ 'step_form' ].grid()

        step_input_frame = self._sequence_widgets.get( 'step_input_frame' )

        if step_input_frame is not None and step_input_frame.winfo_exists():
            for c in self._sequence_widgets[ 'step_input_frame' ].winfo_children():
                c.destroy()

        if self._current_step_for_edit:
            self._sequence_widgets[ 'step_script_field' ].set( self._current_step_for_edit.script_info.filename )
            self._sequence_widgets[ 'stop_step_on_error_var' ].set( self._current_step_for_edit.stop_on_error )

            if len( self._current_step_for_edit.script_info.scriptmeta.script_input_parameters ) > 0:
                self._show_step_form_input( input = self._current_step_for_edit.script_info.scriptmeta.script_input_parameters, pre_set = self._current_step_for_edit.pre_set_parameters )

            else:
                self._show_step_form_input( show = False )

        else:
            self._current_step_for_edit = SequenceStep()
            self._sequence_widgets[ 'step_script_field' ].set( '' )
            self._sequence_widgets[ 'stop_step_on_error_var' ].set( False )

            self._show_step_form_input()


    def _show_step_form_input( self, input: list[ ScriptInputParameter ] = [], pre_set: list[ dict ] = [], show: bool = True ) -> None:
        """ Display or hide step input widgets, depending on script
        
        Args:
            input (list[ ScriptInputParameter ]): List of input parameters to display
            pre_set (list[ dict ]): List of pre set parameter values
        """

        if show:
            self._sequence_widgets[ 'step_input_title' ].grid()
            self._sequence_widgets[ 'step_input_frame' ].grid()

            ipf = self._sequence_widgets.get( 'input_params_frame' )
            if ipf is not None and ipf.winfo_exists():
                ipf.grid()

            if input:
                input_params_frame = self._app_context.input_manager.create_input_widgets(
                    parameters = input,
                    pre_set_parameters = pre_set,
                    parent = self._sequence_widgets[ 'step_input_frame' ]
                )
                input_params_frame.grid()
                self._sequence_widgets[ 'input_params_frame' ] = input_params_frame

        else:
            self._sequence_widgets[ 'step_input_title' ].grid_remove()
            self._sequence_widgets[ 'step_input_frame' ].grid_remove()

            ipf = self._sequence_widgets.get( 'input_params_frame' )
            if ipf is not None and ipf.winfo_exists():
                ipf.grid_remove()


    def abort_sequence_edit( self ) -> None:
        """ Clear all data from widgets stop editing """

        self._current_sequence = None
        self._current_step_for_edit = None

        self._clear_sequence_info()
        self._clear_sequence_steps()

        step_form = self._sequence_widgets.get('step_form')
        if step_form is not None and step_form.winfo_exists():
            step_form.grid_remove()

        sequence_ops = self._sequence_widgets.get('sequence_ops')
        if sequence_ops is not None and sequence_ops.winfo_exists():
            sequence_ops.grid_remove()

        self._sequence_widgets[ 'name_field' ].config( state = 'disable' )
        self._sequence_widgets[ 'description_field' ].config( state = 'disable' )
        self._sequence_widgets[ 'stop_sequence_on_error_field' ].config( state = 'disable' )


    def create_new_sequence( self ) -> None:
        """ Display new sequence form """

        self._sequence_widgets[ 'name_field' ].config( state = 'normal' )
        self._sequence_widgets[ 'description_field' ].config( state = 'normal' )
        self._sequence_widgets[ 'stop_sequence_on_error_field' ].config( state = 'normal' )

        self._sequence_widgets[ 'sequence_ops' ].grid()

    def create_sequence_tab( self, tabcontrol: Notebook, sequence_callbacks: list[ Callable ], translate_callback: Callable ) -> Frame:
        """ Create a Frame that displays and creates sequences """

        from automation_menu.utils.localization import _

        self._sequence_callbacks = sequence_callbacks
        self._parent = tabcontrol

        main_frame = Frame( master = self._parent )
        main_frame.grid( sticky = ( N, S, W, E ) )
        main_frame.grid_columnconfigure( index = 0, weight = 0 ) # Sequence list/op buttons/editing
        main_frame.grid_columnconfigure( index = 1, weight = 1 ) # Sequence steps
        main_frame.grid_rowconfigure( index = 0, weight = 0 ) # Sequence list / Sequence steps
        main_frame.grid_rowconfigure( index = 1, weight = 0 ) # Sequence op buttons
        main_frame.grid_rowconfigure( index = 2, weight = 1 ) # Sequence editing
        main_frame.grid_rowconfigure( index = 3, weight = 0 ) # Sequence editing / Steps op buttons

        tabcontrol.add( child =  main_frame, text = _( 'Automation sequence' ) )
        translate_callback( ( main_frame, 'Automation sequence' ) )

        self._sequence_widgets[ 'main_frame' ] = main_frame

        self._create_sequence_list()
        self._create_sequence_list_op_buttons()
        self._create_sequence_form()
        self._create_steps_display()
        self._create_sequence_editing_op_buttons()
        self._create_step_form()

        return main_frame


    def delete_sequence( self ) -> None:
        """ Delete sequence """

        name = self._current_sequence.name

        del self._sequences[ name ]

        self.abort_sequence_edit()


    def edit_sequence( self ) -> None:
        """ Load selected sequence for editing """

        name = self._sequence_widgets[ 'sequence_list' ].get( self._sequence_widgets[ 'sequence_list' ].curselection() )
        self._current_sequence = self._sequences[ name ]

        self._populate_sequence_form( sequence = self._current_sequence )


    def get_sequence_by_name( self, name: str ) -> Sequence:
        """ Get sequence with the given name

        Returns:
            (Sequence): A Sequence with the asked name
        """

        return self._sequences[ name ]


    def get_sequence_list( self ) -> list[ Sequence ]:
        """ Return a list of names of available sequence

        Returns:
            (list[ Sequence ]): List of names of sequences
        """

        return self._sequences


    def get_sequence_name_list( self ) -> list[ str ]:
        """ Return a list of names of available sequence

        Returns:
            (list[ str ]): List of names of sequences
        """

        list = self._sequences.keys()

        return sorted( list )


    def hide_step_form( self ) -> None:
        """ Hide sequence step editing form """

        self._sequence_widgets[ 'step_script_field' ].set( '' )
        self._sequence_widgets[ 'stop_step_on_error_var' ].set( False )

        step_form = self._sequence_widgets.get('step_form')
        if step_form is not None and step_form.winfo_exists():
            step_form.grid_remove()

        self._current_step_for_edit = None


    def remove_sequence_step( self ) -> None:
        """ Remove step from sequence list """

        self._current_sequence.steps.remove( self._current_step_for_edit )
        self._recalculate_step_indexes()
        self._populate_sequence_steps( sequence = self._current_sequence )
        self.hide_step_form()


    def run_sequence( self, name: str | None = None, on_finished: Callable = None ) -> None:
        """ Run selected sequence

        Args:
            name (str): Name of sequence to run
        """

        def _mini_runner() -> None:
            """ Worker async sequence execution """

            try:
                self._sequence_runner( seq )

            finally:
                if on_finished:
                    on_finished()

        from automation_menu.utils.localization import _

        # Use the sequence selected in list
        if not name:
            name = self._sequence_widgets[ 'sequence_list' ].get( self._sequence_widgets[ 'sequence_list' ].curselection() )

        seq: Sequence = self._sequences[ name ]

        self._app_context.output_queue.put( SysInstructions.CLEAROUTPUT )

        self._app_context.output_queue.put( {
            'line': _( 'Starting sequence ''{name}'', with {step_count} steps' ).format( name = seq.name, step_count = len( seq.steps ) ),
            'tag': OutputStyleTags.SYSINFO,
            'exec_item': None
        } )

        threading.Thread( target = _mini_runner, daemon = True ).start()


    def _sequence_runner( self, sequence: Sequence ) -> None:
        """ Worker function to execute sequence and its steps

        Args:
            sequence (Sequence): Sequence to execute
        """

        from automation_menu.utils.localization import _

        for step in sequence.steps:
            exec_mgr: ScriptExecutionManager = self._app_context.execution_manager

            run_args = build_run_args( step.pre_set_parameters )

            with exec_mgr.create_runner() as runner:
                runner.run_script( script_info = step.script_info,
                                main_window = self._app_context.main_window.root,
                                api_callbacks = self._app_context.main_window.api_callbacks,
                                enable_stop_button_callback = self._app_context.main_window.enable_stop_script_button,
                                enable_pause_button_callback = self._app_context.main_window.enable_pause_script_button,
                                stop_pause_button_blinking_callback = self._app_context.main_window.stop_pause_button_blinking,
                                run_input = run_args
                )

                runner.current_process.wait()
                exit_code = runner._exec_item.exit_code
                terminated = runner._terminated

                effective_stop = step.stop_on_error or sequence.stop_on_error

                if terminated:
                    # Manual stop, abort sequence
                    self._app_context.output_queue.put({
                        "line": _( 'Aborted by user at step {i}' ).format( i = step.step_index ),
                        "tag": OutputStyleTags.SYSINFO,
                        "exec_item": runner._exec_item,
                    })

                    run_success = 1

                elif exit_code != 0:
                    if effective_stop:
                        self._app_context.output_queue.put({
                            "line": _( 'Stopped on error at step {i} (exit code: {e})' ).format( i = step.step_index, e = exit_code ),
                            "tag": OutputStyleTags.SYSERROR,
                            "exec_item": runner._exec_item,
                        })

                        run_success = 2

                    else:
                        self._app_context.output_queue.put({
                            "line": _( 'Step {i} failed (exit code {e})' ).format( i = step.step_index, e = exit_code ),
                            "tag": OutputStyleTags.SYSWARNING,
                            "exec_item": runner._exec_item,
                        })

                        run_success = 3

                run_success = 0

            if run_success > 0:
                self._app_context.output_queue.put( {
                    'line': _( 'Sequence stopped due to individual step error' ),
                    'tag': OutputStyleTags.SYSWARNING,
                    'exec_item': None
                } )

                break


    def save_sequence( self ) -> None:
        """ Save sequence data and steps, as it is """

        self._persist_sequences()


    def toggle_step_form( self ) -> None:
        """ Show/hide step editing form """

        if self._sequence_widgets[ 'step_form' ].winfo_ismapped():
            self.hide_step_form()

        else:
            self._show_step_form()
