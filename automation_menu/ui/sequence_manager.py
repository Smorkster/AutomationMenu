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
from types import FunctionType
from typing import TYPE_CHECKING, Any, Literal, cast, Literal, cast
import uuid

from automation_menu.models.sequence_ui import SequenceUi

if TYPE_CHECKING:
    from automation_menu.core.app_context import ApplicationContext
    from automation_menu.models.application_state import ApplicationState
    from automation_menu.core.script_execution_manager import ScriptExecutionManager

import alwaysontop_tooltip
import threading

from tkinter import W, BooleanVar, Canvas, Event
from tkinter.ttk import Button, Checkbutton, Combobox, Entry, Frame, Label, Notebook, Scrollbar, Treeview
from typing import Callable

from automation_menu.core.script_runner import ScriptRunner
from automation_menu.models.presetparam import PreSetParam
from automation_menu.models.scriptinfo import ScriptInfo
from automation_menu.models.widget_for_translation import WidgetForTranslation
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
            saved_sequences (list[ Sequence ]): User saved sequences
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

        self._current_sequence: Sequence | None = None
        self._current_step_for_edit: SequenceStep | None = None
        self._parent: Notebook | None = None
        self._sequences: dict[ str, Sequence ] = {}
        self._sequence_widgets: SequenceUi = SequenceUi()
        self._sequence_callbacks: dict = {}

        for s in sorted( normalized_sequences, key = lambda x: x.name.lower() ):
            for step in s.steps:
                step.script_info = self._app_context.ScriptManager.get_script_info_by_path( path = step.script_file )

            self._sequences[ s.id ] = s


    def _clear_sequence_info( self ) -> None:
        """ Clear widgets of loaded sequence info """

        self._sequence_widgets.name_field.delete( 0, 'end' )
        self._sequence_widgets.description_field.delete( 0, 'end' )
        self._sequence_widgets.stop_sequence_on_error_var.set( False )


    def _clear_sequence_steps( self ) -> None:
        """ Delete widgets for all listed sequence steps """

        for c in self._sequence_widgets.steps_container.winfo_children():
            c.destroy()


    def _create_sequence_list_op_buttons( self ) -> None:
        """ Define button to create or edit sequences """

        from automation_menu.utils.localization import _

        sequence_op_frame: Frame = Frame( master = self._sequence_widgets.main_frame )
        sequence_op_frame.grid( column = 0, row = 1, sticky = 'we' )

        col: int = 0

        sequence_op_frame.grid_columnconfigure( index = col, weight = 0 )
        create_new_sequence: Button = Button( master = sequence_op_frame, text = _( 'Create new sequence' ), command = self._sequence_callbacks[ 'op_create_new_sequence' ] )
        create_new_sequence.grid( column = col, row = 0, sticky = 'nw' )
        self._sequence_widgets.new_sequence_btn = create_new_sequence

        wft: WidgetForTranslation = WidgetForTranslation( widget = create_new_sequence, default_text = 'Create new sequence' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        col += 1

        sequence_op_frame.grid_columnconfigure( index = col, weight = 0 )
        edit_sequence: Button = Button( master = sequence_op_frame, text = _( 'Edit' ), command = self._sequence_callbacks[ 'op_edit_sequence' ], state = 'disable' )
        edit_sequence.grid( column = col, row = 0, sticky = 'nw' )
        self._sequence_widgets.edit_sequence_btn = edit_sequence

        wft: WidgetForTranslation = WidgetForTranslation( widget = edit_sequence, default_text = 'Edit' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        col += 1

        sequence_op_frame.grid_columnconfigure( index = col, weight = 1 )

        col += 1

        sequence_op_frame.grid_columnconfigure( index = col, weight = 0 )
        run_sequence: Button = Button( master = sequence_op_frame, text = _( 'Run selected' ), command = self._sequence_callbacks[ 'op_run_sequence' ], state = 'disable' )
        run_sequence.grid( column = col, row = 0, sticky = 'nw' )
        self._sequence_widgets.run_sequence_btn = run_sequence

        wft: WidgetForTranslation = WidgetForTranslation( widget = run_sequence, default_text = 'Run selected' )
        self._app_context.LanguageManager.add_translatable_widget( wft )


    def _create_sequence_editing_op_buttons( self ) -> None:
        """ Create buttons for editing a sequence """

        from automation_menu.utils.localization import _

        sequence_ops: Frame = Frame( master = self._sequence_widgets.sequence_form )
        sequence_ops.grid( column = 0, columnspan = 2, row = 4, sticky = 'se' )
        self._sequence_widgets.sequence_ops = sequence_ops

        col: int = 0

        sequence_ops.grid_columnconfigure( index = col, weight = 0 )
        add_step_button: Button = Button( master = sequence_ops, text = _( 'Add step' ) , command = self._sequence_callbacks[ 'op_add_sequence_step' ] )
        add_step_button.grid( column = col, row = 0 )
        self._sequence_widgets.add_step_btn = add_step_button

        wft: WidgetForTranslation = WidgetForTranslation( widget = add_step_button, default_text = 'Add step' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        col += 1

        sequence_ops.grid_columnconfigure( index = col, weight = 0 )
        save_sequence: Button = Button( master = sequence_ops, text = _( 'Save sequence' ), command = self._sequence_callbacks[ 'op_save_sequence' ] )
        save_sequence.grid( column = col, row = 0 )
        self._sequence_widgets.save_sequence_btn = save_sequence

        wft: WidgetForTranslation = WidgetForTranslation( widget = save_sequence, default_text = 'Save sequence' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        col += 1

        sequence_ops.grid_columnconfigure( index = col, weight = 0 )
        delete_sequence: Button = Button( master = sequence_ops, text = _( 'Delete sequence' ), command = self._sequence_callbacks[ 'op_delete_sequence' ] )
        delete_sequence.grid( column = col, row = 0, sticky = 'nw' )
        self._sequence_widgets.delete_sequence_btn = delete_sequence

        wft: WidgetForTranslation = WidgetForTranslation( widget = delete_sequence, default_text = 'Delete' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        col += 1

        sequence_ops.grid_columnconfigure( index = col, weight = 0 )
        abort_sequence_edit: Button = Button( master = sequence_ops, text = _( 'Abort edit' ), command = self._sequence_callbacks[ 'op_abort_sequence_edit' ] )
        abort_sequence_edit.grid( column = col, row = 0, sticky = 'nw' )
        self._sequence_widgets.abort_sequence_edit_btn = abort_sequence_edit

        wft: WidgetForTranslation = WidgetForTranslation( widget = abort_sequence_edit, default_text = 'Abort edit' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        sequence_ops.grid_remove()


    def _create_sequence_form( self ) -> None:
        """ Define a form for displaying sequence information """

        from automation_menu.utils.localization import _

        sequence_form: Frame = Frame( master = self._sequence_widgets.main_frame )
        sequence_form.grid( column = 0, row = 2, rowspan = 2, sticky = 'nswe' )
        sequence_form.grid_columnconfigure( index = 0, weight = 0 )
        sequence_form.grid_columnconfigure( index = 1, weight = 1 )
        sequence_form.grid_columnconfigure( index = 2, weight = 0 )
        sequence_form.grid_rowconfigure( index = 0, weight = 0 ) # Name
        sequence_form.grid_rowconfigure( index = 1, weight = 0 ) # Description
        sequence_form.grid_rowconfigure( index = 2, weight = 0 ) # Stop on error
        sequence_form.grid_rowconfigure( index = 3, weight = 1 ) # Empty
        sequence_form.grid_rowconfigure( index = 4, weight = 1 ) # Sequence op buttons
        self._sequence_widgets.sequence_form = sequence_form

        row: int = 0

        name_title: Label = Label( master = sequence_form, text = _( 'Name' ), style = 'History.TLabel' )
        name_title.grid( column = 0, row = row, sticky = ( W ) )

        wft: WidgetForTranslation = WidgetForTranslation( widget = name_title, default_text = 'Name' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        name_field: Entry = Entry( master = sequence_form )
        name_field.grid( column = 1, columnspan = 2, row = row, sticky = 'we' )
        self._sequence_widgets.name_field = name_field

        row += 1

        description_title: Label = Label( master = sequence_form, text = _( 'Description' ), style = 'History.TLabel' )
        description_title.grid( column = 0, row = row, sticky = ( W ) )

        wft: WidgetForTranslation = WidgetForTranslation( widget = description_title, default_text = 'Description' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        description_field: Entry = Entry( master = sequence_form )
        description_field.grid( column = 1, columnspan = 2, row = row, sticky = 'we' )
        self._sequence_widgets.description_field = description_field

        row += 1

        stop_on_error_title: Label = Label( master = sequence_form, text = _( 'Stop on error' ), style = 'History.TLabel' )
        stop_on_error_title.grid( column = 0, row = row, sticky = 'w' )

        wft: WidgetForTranslation = WidgetForTranslation( widget = stop_on_error_title, default_text = 'Stop on error' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        self._sequence_widgets.stop_sequence_on_error_var = BooleanVar( master = sequence_form, value = False )
        stop_on_error_field: Checkbutton = Checkbutton( master = sequence_form, variable = self._sequence_widgets.stop_sequence_on_error_var )
        stop_on_error_field.grid( column = 1, columnspan = 2, row = row, sticky = 'we' )
        self._sequence_widgets.stop_sequence_on_error_field = stop_on_error_field


    def _create_sequence_list( self ) -> None:
        """ Define a list to display available sequences """

        sequence_list: Treeview = Treeview( master = self._sequence_widgets.main_frame, columns = ( 'name', 'id' ), displaycolumns = 'name', show = '', selectmode = 'browse' )
        sequence_list.column( 'name', anchor = 'w' )
        sequence_list.column( 'id', anchor = 'w' )
        sequence_list.bind( '<ButtonRelease-1>', self._on_listbox_click )
        sequence_list.grid( column = 0, row = 0, sticky = 'nswe' )
        self._sequence_widgets.sequence_list = sequence_list

        list_scrollbar: Scrollbar = Scrollbar( master = self._sequence_widgets.main_frame )
        list_scrollbar.grid( column = 0, row = 0, sticky = 'nse' )

        sequence_list.config( yscrollcommand = list_scrollbar.set )

        list_scrollbar.config( command = sequence_list.yview )

        self._list_sequences()


    def _create_steps_display( self ) -> None:
        """ Create display frame to contain sequence steps """

        from automation_menu.utils.localization import _

        steps_display_frame: Frame = Frame( master = self._sequence_widgets.main_frame )
        steps_display_frame.grid( column = 1, row = 0, rowspan = 3, sticky = 'nswe' )
        steps_display_frame.grid_columnconfigure( index = 0, weight = 1 )
        steps_display_frame.grid_columnconfigure( index = 1, weight = 0 )
        steps_display_frame.grid_rowconfigure( index = 0, weight = 0 )
        steps_display_frame.grid_rowconfigure( index = 1, weight = 1 )
        steps_display_frame.grid_rowconfigure( index = 2, weight = 0 )
        self._sequence_widgets.steps_display_frame = steps_display_frame

        steps_title: Label = Label( master = steps_display_frame, text = _( 'Steps in sequence' ), style = 'BiggerTitle.TLabel' )
        steps_title.grid( column = 0, row = 0, sticky = ( W ) )

        wft: WidgetForTranslation = WidgetForTranslation( widget = steps_title, default_text = 'Steps in sequence' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        display_container: Frame = Frame( master = steps_display_frame )
        display_container.grid( column = 0, columnspan = 2, row = 1, sticky = 'nswe' )
        display_container.grid_columnconfigure( index = 0, weight = 1 )
        display_container.grid_rowconfigure( index = 0, weight = 1 )
        self._sequence_widgets.display_container = display_container

        container_canvas: Canvas = Canvas( master = display_container, highlightthickness = 0 )
        container_canvas.grid( sticky = 'nswe' )
        container_canvas.grid_columnconfigure( index = 0, weight = 1 )
        container_canvas.bind( '<Configure>', self._on_canvas_config )
        self._sequence_widgets.steps_list_container_canvas = container_canvas
        container_canvas.bind_all( '<MouseWheel>' , self._on_mousewheel )

        container_scrollbar: Scrollbar = Scrollbar( master = display_container, orient = 'vertical', command = container_canvas.yview )
        container_scrollbar.grid( column = 1, row = 0, sticky = 'ns' )
        self._sequence_widgets.container_scrollbar = container_scrollbar

        container_canvas.configure( yscrollcommand = container_scrollbar.set )

        steps_container: Frame = Frame( master = container_canvas )
        steps_container.grid_columnconfigure( index = 0, weight = 1 )
        steps_container.grid_rowconfigure( index = 0, weight = 1 )
        steps_container.bind( '<Configure>', self._on_steps_container_frame_config )
        self._sequence_widgets.steps_container = steps_container

        window_id = container_canvas.create_window( ( 0, 0 ), window = steps_container, anchor = 'nw' )
        self._sequence_widgets.steps_list_input_window_id = window_id


    def _create_step_form( self ) -> None:
        """ Create form for editing/creating a sequence step """

        from automation_menu.utils.localization import _

        step_form: Frame = Frame( master = self._sequence_widgets.steps_display_frame, style = 'SequenceStep.TFrame', borderwidth = 2, relief = 'solid' )
        step_form.grid( column = 0, row = 2, sticky = 'we' )
        step_form.grid_columnconfigure( index = 0, weight = 0 )
        step_form.grid_columnconfigure( index = 1, weight = 1 )
        self._sequence_widgets.step_form = step_form

        row: int = 0

        step_form.grid_rowconfigure( index = row, weight = 0 ) # Script title
        script_title: Label = Label( master = step_form, text = _( 'Script for this step' ), style = 'History.TLabel' )
        script_title.grid( column = 0, row = row, sticky = 'nw' )

        wft: WidgetForTranslation = WidgetForTranslation( widget = script_title, default_text = 'Script for this step' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        script_names: list[ str ] = sorted( [ s.filename for s in self._app_context.ScriptManager.get_script_list() ] )
        script_list: Combobox = Combobox( master = step_form, values = script_names, state = 'readonly' )
        script_list.bind( '<<ComboboxSelected>>', self._on_step_script_selected )
        script_list.grid( column = 1, row = row, padx = 5, sticky = 'nw' )
        self._sequence_widgets.step_script_list = script_list

        row += 1

        step_form.grid_rowconfigure( index = row, weight = 0 ) # Stop on error
        stop_on_error_title: Label = Label( master = step_form, text = _( 'Stop on error' ), style = 'History.TLabel' )
        stop_on_error_title.grid( column = 0, row = row, sticky = 'w' )

        wft: WidgetForTranslation = WidgetForTranslation( widget = stop_on_error_title, default_text = 'Stop on error' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        self._sequence_widgets.stop_step_on_error_var = BooleanVar( master = step_form, value = False )
        stop_on_error_field: Checkbutton = Checkbutton( master = step_form, variable = self._sequence_widgets.stop_step_on_error_var )
        stop_on_error_field.grid( column = 1, row = row, sticky = 'w' )

        row += 1

        step_form.grid_rowconfigure( index = row, weight = 0 ) # Input title
        input_title: Label = Label( master = step_form, text = _( 'Script input parameters' ), style = 'History.TLabel' )
        input_title.grid( column = 0, row = row, sticky = 'nw' )
        self._sequence_widgets.step_input_title = input_title

        wft: WidgetForTranslation = WidgetForTranslation( widget = input_title, default_text = 'Script input parameters' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        row += 1

        step_form.grid_rowconfigure( index = row, weight = 0 ) # Input parameters
        input_container: Frame = Frame( master = step_form )
        input_container.grid( column = 0, columnspan = 2, row = row, sticky = 'we' )
        input_container.grid_columnconfigure( index = 0, weight = 1 )
        input_container.grid_columnconfigure( index = 1, weight = 0 )
        input_container.grid_rowconfigure( index = 0, weight = 0 )

        container_canvas: Canvas = Canvas( master = input_container, height = 150, highlightthickness = 0 )
        container_canvas.grid( column = 0, row = 0, sticky = 'we' )
        container_canvas.grid_columnconfigure( index = 0, weight = 1 )

        container_scrollbar: Scrollbar = Scrollbar( master = input_container, orient = 'vertical', command = container_canvas.yview )
        container_scrollbar.grid( column = 1, row = 0, sticky = 'ns' )

        container_canvas.configure( yscrollcommand = container_scrollbar.set )

        input_frame: Frame = Frame( master = container_canvas )
        window_id: int = container_canvas.create_window( ( 0, 0 ), window = input_frame, anchor = 'nw' )

        self._sequence_widgets.step_input_container = input_container
        self._sequence_widgets.step_form_container_canvas = container_canvas
        self._sequence_widgets.step_input_window_id = window_id
        self._sequence_widgets.step_input_frame = input_frame

        input_frame.bind(
            '<Configure>',
            lambda e: container_canvas.configure(
                scrollregion = container_canvas.bbox( 'all' )
                )
        )

        container_canvas.bind(
            '<Configure>',
            lambda e: container_canvas.itemconfig( window_id, width = e.width )
        )

        row += 1

        step_form.grid_rowconfigure( index = row, weight = 0 ) # Step op buttons

        step_op_buttons_frame: Frame = Frame( master = step_form )
        step_op_buttons_frame.grid( column = 1, row = row, sticky = 'se' )

        col = 0

        step_op_buttons_frame.grid_columnconfigure( index = col, weight = 0 )
        step_add: Button = Button( master = step_op_buttons_frame, text = _( 'Save step' ), command = self._save_edited_step )
        step_add.grid( column = col, row = 0, sticky = 'e' )

        wft: WidgetForTranslation = WidgetForTranslation( widget = step_add, default_text = 'Save step' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        col += 1

        step_op_buttons_frame.grid_columnconfigure( index = col, weight = 0 )
        step_remove: Button = Button( master = step_op_buttons_frame, text = _( 'Remove step' ), command = self._sequence_callbacks[ 'op_remove_sequence_step' ] )
        step_remove.grid( column = col, row = 0, sticky = 'e' )

        wft: WidgetForTranslation = WidgetForTranslation( widget = step_remove, default_text = 'Remove step' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        col += 1

        step_op_buttons_frame.grid_columnconfigure( index = col, weight = 0 )
        step_abort: Button = Button( master = step_op_buttons_frame, text = _( 'Abort' ), command = self._sequence_callbacks[ 'op_abort_add_sequence_step' ] )
        step_abort.grid( column = col, row = 0, sticky = 'e' )

        wft: WidgetForTranslation = WidgetForTranslation( widget = step_abort, default_text = 'Abort' )
        self._app_context.LanguageManager.add_translatable_widget( wft )

        step_form.grid_remove()


    def _get_selected_sequence_id( self ) -> str | None:
        """ Get id of the sequence selected in the UI list

        Returns:
            (int): Id of the selected sequence,
                None if no sequence is selected
        """

        values = self._sequence_widgets.sequence_list.item( self._sequence_widgets.sequence_list.focus() ).get( 'values', [] )

        if len( values ) < 2 or not isinstance( values[ 1 ], str ):

            return None

        return values[ 1 ]


    def _on_canvas_config( self, event: Event ) -> None:
        """ Eventhandler for when sequence step canvas changes size

        Args:
            event (Event): Event that triggered handler
        """

        canvas: Canvas = self._sequence_widgets.steps_list_container_canvas
        canvas.after_idle( lambda: canvas.itemconfig( self._sequence_widgets.steps_list_input_window_id, width = event.width ) if self._sequence_widgets.steps_list_input_window_id else '' )


    def _on_steps_container_frame_config( self, event: Event ) -> None:
        """ Eventhandler for when sequence step frame changes size

        Args:
            event (Event): Event that triggered handler
        """

        canvas: Canvas = self._sequence_widgets.steps_list_container_canvas
        canvas.after_idle( lambda: canvas.configure( scrollregion = canvas.bbox( 'all' ) ) )


    def _on_listbox_click( self, event: Event ) -> None:
        """ Verify if an item or empty area was clicked in the listbox

        Args:
            event (Event): Event that triggered handler
        """

        if not isinstance( event.widget, Treeview ):
            return

        sequence_listbox: Treeview = event.widget

        if item_focused := sequence_listbox.focus():
            values: list[ Any ] | Literal[ '' ] = sequence_listbox.item( item_focused ).get( 'values', [] )

            if len( values ) < 2:
                from automation_menu.utils.localization import _

                self._app_context.debug_logger.warning( _( 'Sequence list item missing id: {item}' ).format( item = values ) )

                return

            self._sequence_widgets.edit_sequence_btn.config( state = 'normal' )
            self._sequence_widgets.run_sequence_btn.config( state = 'normal' )

        return


    def _on_mousewheel( self, event: Event ) -> None:
        """ Eventhandler for mouse wheel scrolling in the steps list

        Args:
            event (Event): Event that triggered handler
        """

        self._sequence_widgets.steps_list_container_canvas.yview_scroll( int( -1 * ( event.delta / 120 ) ), 'units' )


    def _on_step_click( self, step: SequenceStep ) -> None:
        """ Eventhandler for click on step row

        Args:
            step (SequenceStep): Index of the step that got clicked
        """

        if not self._current_sequence or not step:
            from automation_menu.utils.localization import _

            self._app_context.debug_logger.warning( _( 'Invalid step at index {i}' ).format( i = step.step_index ) )

            return

        self._current_step_for_edit = step
        self._show_step_form()


    def _on_step_script_selected( self, event: Event ) -> None:
        """ Eventhandler for when a script is selected for a sequence step

        Args:
            event (Event): Event that triggered handler
        """

        from automation_menu.utils.localization import _

        step_input_frame: Frame | None = self._sequence_widgets.step_input_frame

        if step_input_frame is not None and step_input_frame.winfo_exists():
            for c in step_input_frame.winfo_children():
                c.destroy()

        selected_name: str = cast( Combobox, event.widget ).get()
        selected_script: ScriptInfo = self._app_context.ScriptManager.get_script_info_by_filename( selected_name )

        if self._current_step_for_edit is None:

            raise ValueError( _( '\'Current step\' was lost, can\'t load step' ) )

        self._current_step_for_edit.script_file = selected_script.fullpath
        self._current_step_for_edit.script_info = selected_script

        if len( selected_script.scriptmeta.script_input_parameters ) > 0:
            self._show_step_form_input( input = selected_script.scriptmeta.script_input_parameters )


    def _persist_sequences( self ) -> None:
        """ Transform sequence data to dict and save to settings """

        from automation_menu.utils.localization import _

        sequences_dict_list: list[ dict ] = []
        sequences_list: list[ Sequence ] = []

        for s in self._sequences.values():

            jsoned_sequence: dict = s.to_dict()
            sequences_dict_list.append( jsoned_sequence )

            sequences_list.append( s )

        self._app_state.settings.saved_sequences = sequences_list


    def _populate_sequence_form( self, sequence: Sequence ) -> None:
        """ Enter selected sequence data to info widgets

        Args:
            sequence (Sequence): Sequence to take information from
        """

        self._sequence_widgets.sequence_ops.grid()

        self._sequence_widgets.name_field.config( state = 'normal' )
        self._sequence_widgets.name_field.delete( 0, 'end' )
        self._sequence_widgets.name_field.insert( 0, sequence.name )

        self._sequence_widgets.description_field.config( state = 'normal' )
        self._sequence_widgets.description_field.delete( 0, 'end' )
        self._sequence_widgets.description_field.insert( 0, sequence.description )

        self._sequence_widgets.stop_sequence_on_error_field.config( state = 'normal' )
        self._sequence_widgets.stop_sequence_on_error_var.set( sequence.stop_on_error )

        self._populate_sequence_steps( sequence )


    def _populate_sequence_steps( self, sequence: Sequence ) -> None:
        """ Create widgets per sequence step and populate display frame

        Args:
            sequence (Sequence): Sequence to take step list from
        """

        from automation_menu.utils.localization import _

        self._clear_sequence_steps()

        for step in sequence.steps:
            lambda_bind: FunctionType = lambda e, i = step: self._on_step_click( step = i )

            self._sequence_widgets.steps_container.grid_rowconfigure( index = step.step_index, weight = 0 )
            step_frame: Frame = Frame( master = self._sequence_widgets.steps_container, borderwidth = 2, relief = 'solid', padding = 5 )
            step_frame.grid( column = 0, row = step.step_index, sticky = 'we' )
            step_frame.bind( '<Button-1>', lambda_bind )

            step_label: Label = Label( master = step_frame, text = f'{ step.step_index } :: { step.script_file }' )
            step_label.grid( sticky = 'we' )
            step_label.bind( '<Button-1>', lambda_bind )

            tooltip_text: str = ""

            if step.pre_set_parameters:
                tooltip_text = '\n'.join( [ f'--{ p[ 'name' ] } { p[ 'set' ] }' for p in step.pre_set_parameters ] )

            else:
                tooltip_text = _( 'Input not specified' )

            alwaysontop_tooltip.alwaysontop_tooltip.AlwaysOnTopToolTip( widget = step_label, msg = tooltip_text )


    def _recalculate_step_indexes( self ) -> None:
        """ Sequence step list have changed, recalculate each steps list index """

        if self._current_sequence is None:

            return

        for step in [ ( i, s ) for i, s in enumerate( self._current_sequence.steps ) ]:
            step[ 1 ].step_index = step[ 0 ]


    def _list_sequences( self ) -> None:
        """ List available sequences """

        tree: Treeview = self._sequence_widgets.sequence_list

        tree.delete( *tree.get_children() )

        for k in self._sequences.items():
            tree.insert( '', 'end', values = ( k[ 1 ].name, k[ 0 ] ) )

        if self._app_context.main_window is not None:
            self._app_context.main_window.op_buttons[ 'sequence_menu' ].rebuild_menu( exec_list = self._sequences )


    def _save_edited_step( self ) -> None:
        """ Save the currently edited step """

        if self._current_sequence is None:

            return

        if not self._current_step_for_edit:
            self._current_step_for_edit = SequenceStep()
            self._current_sequence.steps.append( self._current_step_for_edit )
            self._current_step_for_edit.step_index = self._current_sequence.steps.index( self._current_step_for_edit )

        selected_script: ScriptInfo = self._app_context.ScriptManager.get_script_info_by_filename( filename = self._sequence_widgets.step_script_list.get() )
        self._current_step_for_edit.script_file = selected_script.fullpath
        self._current_step_for_edit.script_info = selected_script
        self._current_step_for_edit.stop_on_error = self._sequence_widgets.stop_step_on_error_var.get()

        try:
            index: int = self._current_sequence.steps.index( self._current_step_for_edit )

        except:
            self._current_sequence.steps.append( self._current_step_for_edit )
            index: int = len( self._current_sequence.steps ) - 1

        self._current_step_for_edit.step_index = index

        if self._sequence_widgets.input_params_frame is None:
            ipf: Frame | None = self._sequence_widgets.input_params_frame

            if ipf and ipf.winfo_exists():
                step_input: list[ PreSetParam ] = self._app_context.InputManager.collect_entered_input( frame_to_search = ipf )
                self._current_step_for_edit.pre_set_parameters = step_input

        self.hide_step_form()
        self._populate_sequence_steps( sequence = self._current_sequence )
        self._persist_sequences()


    def _sequence_runner( self, sequence: Sequence ) -> None:
        """ Worker function to execute sequence and its steps

        Args:
            sequence (Sequence): Sequence to execute
        """

        from automation_menu.utils.localization import _

        for step in sequence.steps:
            exec_mgr: ScriptExecutionManager = self._app_context.ExecutionManager
            run_args: list[ str ] = build_run_args( params = step.pre_set_parameters )
            run_success: int = 0
            runner: ScriptRunner | None = None

            if self._app_context.main_window is None:
                break

            try:
                with exec_mgr.create_runner() as runner:
                    if runner is None:

                        raise ValueError( _( f'Couldn\'t initiate a runner for sequence ''{s}''' ).format( s = sequence.name ) )

                    runner.run_script( script_info = step.script_info,
                                    main_window = self._app_context.main_window.root,
                                    api_callbacks = self._app_context.main_window.api_callbacks,
                                    enable_stop_button_callback = self._app_context.main_window.enable_stop_script_button,
                                    enable_pause_button_callback = self._app_context.main_window.enable_pause_script_button,
                                    stop_pause_button_blinking_callback = self._app_context.main_window.stop_pause_button_blinking,
                                    run_input = run_args
                    )

                    runner.current_process.wait()
                    exit_code: int = runner.get_exit_code()
                    terminated: bool = runner.was_terminated()
                    effective_stop: bool = step.stop_on_error or sequence.stop_on_error

                    if terminated:
                        # Manual stop, abort sequence
                        self._app_context.OutputQueue.put({
                            "line": _( 'Aborted by user at step {i}' ).format( i = step.step_index ),
                            "tag": OutputStyleTags.SYSINFO,
                            "exec_item": runner._exec_item,
                        })

                        run_success = 1

                    elif exit_code != 0:
                        if effective_stop:
                            self._app_context.OutputQueue.put({
                                "line": _( 'Stopped on error at step {i} (exit code: {e})' ).format( i = step.step_index, e = exit_code ),
                                "tag": OutputStyleTags.SYSERROR,
                                "exec_item": runner._exec_item,
                            })

                            run_success = 2

                        else:
                            self._app_context.OutputQueue.put({
                                "line": _( 'Step {i} failed (exit code {e})' ).format( i = step.step_index, e = exit_code ),
                                "tag": OutputStyleTags.SYSWARNING,
                                "exec_item": runner._exec_item,
                            })

                            run_success = 3

            except Exception as e:
                self._app_context.OutputQueue.put( {
                    'line': _( 'Error in {f}, step {s} of {c}' ).format( f = step.script_info, s = step.step_index + 1, c = len( sequence.steps ) ),
                    'tag': OutputStyleTags.SYSERROR,
                    'exec_item': getattr( runner, '_exec_item', None )
                } )

                if sequence.stop_on_error or step.stop_on_error:
                    break

            else:
                if run_success > 0:
                    self._app_context.OutputQueue.put( {
                        'line': _( 'Sequence stopped at step {i} due to individual step error' ).format( i = step.step_index ),
                        'tag': OutputStyleTags.SYSWARNING,
                        'exec_item': None
                    } )

                    break


    def _show_step_form( self ) -> None:
        """ Display the form to edit/add sequence step """

        step_form: Frame | None = self._sequence_widgets.step_form

        if step_form is None or not step_form.winfo_exists():
            self._create_step_form()
            step_form = self._sequence_widgets.step_form

        self._sequence_widgets.step_form.grid()

        step_input_frame: Frame | None = self._sequence_widgets.step_input_frame

        if step_input_frame is not None and step_input_frame.winfo_exists():
            for c in step_input_frame.winfo_children():
                c.destroy()

        if self._current_step_for_edit:
            script_info = self._current_step_for_edit.script_info
            self._sequence_widgets.step_script_list.set( script_info.filename )
            self._sequence_widgets.stop_step_on_error_var.set( self._current_step_for_edit.stop_on_error )

            if len( script_info.scriptmeta.script_input_parameters ) > 0:
                self._show_step_form_input( input = script_info.scriptmeta.script_input_parameters, pre_set = self._current_step_for_edit.pre_set_parameters )

            else:
                self._show_step_form_input( show = False )

        else:
            self._current_step_for_edit = SequenceStep()
            self._sequence_widgets.step_script_list.set( '' )
            self._sequence_widgets.stop_step_on_error_var.set( False )

            self._show_step_form_input()


    def _show_step_form_input( self, input: list[ ScriptInputParameter ] = [], pre_set: list[ PreSetParam ] = [], show: bool = True ) -> None:
        """ Display or hide step input widgets, depending on script
        
        Args:
            input (list[ ScriptInputParameter ]): List of input parameters to display
            pre_set (list[ PreSetParam ]): List of pre set parameter values
            show (bool): Should the input frame be shown
        """

        ipf: Frame | None = self._sequence_widgets.input_params_frame

        if show:
            self._sequence_widgets.step_input_title.grid()
            self._sequence_widgets.step_input_container.grid()

            if ipf is not None and ipf.winfo_exists():
                ipf.grid()

            if input:
                input_params_frame = self._app_context.InputManager.create_input_widgets(
                    parameters = input,
                    pre_set_parameters = pre_set,
                    parent = self._sequence_widgets.step_input_frame,
                    canvas = self._sequence_widgets.step_form_container_canvas
                )
                input_params_frame.grid()
                self._sequence_widgets.input_params_frame = input_params_frame

        else:
            self._sequence_widgets.step_input_title.grid_remove()
            self._sequence_widgets.step_input_container.grid_remove()

            if ipf is not None and ipf.winfo_exists():
                ipf.grid_remove()


    def abort_sequence_edit( self ) -> None:
        """ Clear all data from widgets stop editing """

        self._current_sequence = None
        self._current_step_for_edit = None

        self._clear_sequence_info()
        self._clear_sequence_steps()

        step_form: Frame = self._sequence_widgets.step_form

        if step_form is not None and step_form.winfo_exists():
            step_form.grid_remove()

        sequence_ops: Frame = self._sequence_widgets.sequence_ops

        if sequence_ops is not None and sequence_ops.winfo_exists():
            sequence_ops.grid_remove()

        self._sequence_widgets.name_field.config( state = 'disable' )
        self._sequence_widgets.description_field.config( state = 'disable' )
        self._sequence_widgets.stop_sequence_on_error_field.config( state = 'disable' )


    def build_tab_content( self ) -> None:
        """ Call for creation of widgets to display sequence data """

        self._create_sequence_list()
        self._create_sequence_list_op_buttons()
        self._create_sequence_form()
        self._create_steps_display()
        self._create_sequence_editing_op_buttons()
        self._create_step_form()


    def create_new_sequence( self ) -> None:
        """ Display empty sequence form """

        new_id: str = str( uuid.uuid4() )
        self._current_sequence = Sequence( id = new_id, description = '', name = '', stop_on_error = False, steps = [] )
        self._sequences[ new_id ] = self._current_sequence

        self._populate_sequence_form( self._current_sequence )


    def create_sequence_tab( self, tabcontrol: Notebook, sequence_callbacks: dict[ str, Callable ], translate_callback: Callable ) -> Frame:
        """ Create a Frame that displays and creates sequences

        Args:
            tabcontrol (Notebook): Parent widget to attach frame to
            sequence_callbacks (dict[ str, Callable ]): Function callbacks for UI execution wrappers
            translate_callback (Callable): Function callback for localization translation
        """

        from automation_menu.utils.localization import _

        self._sequence_callbacks = sequence_callbacks
        self._parent = tabcontrol

        main_frame: Frame = Frame( master = self._parent, name = 'sequence' )
        main_frame.grid( sticky = "nswe" )
        main_frame.grid_columnconfigure( index = 0, weight = 0 ) # Sequence list/op buttons/editing
        main_frame.grid_columnconfigure( index = 1, weight = 1 ) # Sequence steps
        main_frame.grid_rowconfigure( index = 0, weight = 0 ) # Sequence list / Sequence steps
        main_frame.grid_rowconfigure( index = 1, weight = 0 ) # Sequence op buttons
        main_frame.grid_rowconfigure( index = 2, weight = 1 ) # Sequence editing
        main_frame.grid_rowconfigure( index = 3, weight = 0 ) # Sequence editing / Steps op buttons

        tabcontrol.add( child =  main_frame, text = _( 'Automation sequence' ) )

        wft: WidgetForTranslation = WidgetForTranslation( widget = main_frame, default_text = 'Automation sequence' )
        translate_callback( wft )

        self._sequence_widgets.main_frame = main_frame

        return main_frame


    def delete_sequence( self ) -> None:
        """ Delete sequence """

        from automation_menu.utils.localization import _

        if self._current_sequence is None:

            raise ValueError( _( '\'Current sequence\' was lost, can\'t remove sequence' ) )

        sequence_id: str = self._current_sequence.id

        del self._sequences[ sequence_id ]

        self.abort_sequence_edit()
        self._persist_sequences()
        self._list_sequences()


    def edit_sequence( self ) -> None:
        """ Load selected sequence for editing """

        id: str | None = self._get_selected_sequence_id()

        if id is None:
            return

        self._current_sequence = self._sequences[ id ]

        self._populate_sequence_form( sequence = self._current_sequence )


    def get_sequence_list( self ) -> dict[ str, Sequence ]:
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

        list: list[ str ] = []

        for i, s in [ ( i , s ) for i, s in self._sequences.items() ]:
            list.append( s.name )

        return sorted( list )


    def hide_step_form( self ) -> None:
        """ Hide sequence step editing form """

        self._sequence_widgets.step_script_list.set( '' )
        self._sequence_widgets.stop_step_on_error_var.set( False )

        step_form: Frame = self._sequence_widgets.step_form

        if step_form is not None and step_form.winfo_exists():
            step_form.grid_remove()

        self._current_step_for_edit = None


    def remove_sequence_step( self ) -> None:
        """ Remove step from sequence list """

        from automation_menu.utils.localization import _

        if self._current_sequence is None:

            raise ValueError( _( '\'Current sequence\' was lost, can\'t remove step' ) )

        if self._current_step_for_edit is None:

            raise ValueError( _( '\'Current step\' was lost, can\'t remove step' ) )

        self._current_sequence.steps.remove( self._current_step_for_edit )
        self._recalculate_step_indexes()
        self._populate_sequence_steps( sequence = self._current_sequence )
        self.hide_step_form()


    def run_sequence( self, on_finished: Callable , sequence_id: str | None = None ) -> None:
        """ Run selected sequence

        Args:
            on_finished (Callable): Function callback to run after sequence finished execution
            sequence_id (str | None): Id of sequence to run
        """

        def _mini_runner() -> None:
            """ Worker async sequence execution """

            try:
                self._sequence_runner( seq )

            finally:
                on_finished()

        from automation_menu.utils.localization import _

        sid = sequence_id if sequence_id is not None else self._get_selected_sequence_id()

        # Use the sequence selected in list
        if sid is None:

            return

        seq: Sequence = self._sequences[ sid ]
        self._app_context.OutputQueue.put( SysInstructions.CLEAROUTPUT )
        main_window = self._app_context.main_window

        if main_window is None:

            return

        main_window.execution_pre_work( is_sequence = True )
        self._app_context.OutputQueue.put( {
            'line': _( 'Starting sequence ''{name}'', with {step_count} steps' ).format( name = seq.name, step_count = len( seq.steps ) ),
            'tag': OutputStyleTags.SYSINFO,
            'exec_item': None
        } )

        threading.Thread( target = _mini_runner, daemon = True ).start()


    def save_sequence( self ) -> None:
        """ Save sequence data and steps, as it is """

        from automation_menu.utils.localization import _

        if self._current_sequence is None:

            raise ValueError( _( '\'Current sequence\' was lost, can\'t save data' ) )

        self._current_sequence.name = self._sequence_widgets.name_field.get()
        self._current_sequence.description = self._sequence_widgets.description_field.get()

        self._sequences[ self._current_sequence.id ] = self._current_sequence
        self._persist_sequences()
        self._list_sequences()


    def toggle_step_form( self ) -> None:
        """ Show/hide step editing form """

        if self._sequence_widgets.step_form.winfo_ismapped():
            self.hide_step_form()

        else:
            self._show_step_form()
